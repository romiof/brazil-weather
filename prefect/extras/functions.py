"""
This module include functions/Tasks used in Flows.
"""
import os
from pathlib import Path
import pandas as pd
from prefect import task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import BigQueryWarehouse


@task(retries=3, retry_delay_seconds=10)
def downloader(url: str, folder: str, filename: str) -> str:
    """
    Function to download CSV/Zip files.

    Parameters
    ----------
    url: location of the source file
    folder: destination directory for downloaded file
    filename: name + extension of the destination file

    """
    from requests import get

    # make destination folder, if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # download and write the file
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as file:
        response = get(url)
        file.write(response.content)

    return file_path

@task(retries=3, retry_delay_seconds=10)
def unziper(zip_file: str, folder: str, year: int) -> str:
    """
    Function to unzip downloaded files.
    After extracted, the file will be deleted.

    Parameters
    ----------
    zip_file: file location to unzip 
    folder: destination folder to all files inside the original zip file

    """
    import os
    import zipfile

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(folder)

    # del zip file
    os.remove(zip_file)

    # sometimes, zip file has a folder container for year
    sub_dir = folder + str(year) + "/"
    if os.path.exists(sub_dir):
        return sub_dir
    else: 
        return folder


# helper function
def generate_pd(filename: str) -> pd.DataFrame:
    """
    Function to read CSV file and processing it using Pandas.
    Returns a Pandas DataFrame.

    Parameters
    ----------
    filename: file path of CSV

    """

    # first, need to catch the station code, which is on line #4 of every CSV file
    # then it will be added as a new column into main dataframe
    station_code = pd.read_csv(
        filename, encoding="cp1252", sep=';', skiprows=3, nrows=0, usecols=range(1, 2))
    col_st_code = list(station_code.columns)[0]

    # now, read the main data from the CSV, starting on line #9
    df = pd.read_csv(filename, encoding="cp1252", sep=';',
                     decimal=',', skiprows=8, usecols=range(19))

    # translate header from Portuguese to English
    dict_header = {
        "Data": "DATE",
        "Hora UTC": "TIME",
        "DATA (YYYY-MM-DD)": "DATE",
        "HORA (UTC)": "TIME",
        "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)": "TOTAL_PRECIPITATION",
        "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)": "ATMOSPHERIC_PRESSURE",
        "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)": "MAX_ATMOSPHERIC_PRESSURE",
        "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)": "MIN_ATMOSPHERIC_PRESSURE",
        "RADIACAO GLOBAL (Kj/m²)": "SOLAR_RADIATION",
        "RADIACAO GLOBAL (KJ/m²)": "SOLAR_RADIATION",
        "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)": "DRY_BULB_AIR_TEMPERATURE",
        "TEMPERATURA DO PONTO DE ORVALHO (°C)": "DEW_POINT_TEMPERATURE",
        "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)": "MAX_AIR_TEMP_DRY_BULB",
        "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)": "MIN_AIR_TEMP_DRY_BULB",
        "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)": "MAX_DEW_POINT_TEMP",
        "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)": "MIN_DEW_POINT_TEMP",
        "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)": "MAX_RELATIVE_HUMIDITY",
        "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)": "MIN_RELATIVE_HUMIDITY",
        "UMIDADE RELATIVA DO AR, HORARIA (%)": "RELATIVE_HUMIDITY",
        "VENTO, DIREÇÃO HORARIA (gr) (° (gr))": "WIND_DIRECTION",
        "VENTO, RAJADA MAXIMA (m/s)": "WIND_MAX_GUST",
        "VENTO, VELOCIDADE HORARIA (m/s)": "WIND_SPEED",
    }

    df.rename(columns=dict_header, inplace=True)

    # remove additional suffixes from "Time" column and merge with "Date" column
    df["TIME"].replace(' UTC', '', regex=True, inplace=True)
    df["DATE"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
    df.drop("TIME", axis=1, inplace=True)

    # some CSVs have blank lines, or lines with -9999 value, due of system malfunction
    # and for those, its lines will be dropped
    df = df[df.TOTAL_PRECIPITATION != -9999]
    df.drop_duplicates(inplace=True)
    df.dropna(axis=0, inplace=True)

    # add station code as the first column
    df.insert(0, "STATION_CODE", col_st_code)

    # cast RELATIVE_HUMIDITY to float 
    df["RELATIVE_HUMIDITY"] = df["RELATIVE_HUMIDITY"].astype(float)

    return df


@task(retries=3, retry_delay_seconds=10)
def csv_to_pd(foldername: str) -> list[pd.DataFrame]:
    """
    Function to read a folder with CSV files and processing it using Pandas 
    through "generate_pd" function.
    Returns a List with all Pandas DataFrame.

    Parameters
    ----------
    foldername: folder path with CSV files

    """
    all_dfs_list = []
    for filename in os.listdir(foldername):
        if filename.upper().endswith("CSV"):
            df = generate_pd(os.path.join(foldername + filename))
            if not df.empty:
                all_dfs_list.append(df)
            # remove processed file
            os.remove(foldername + filename)

    return all_dfs_list


@task(retries=3, retry_delay_seconds=10)
def generate_parquet(all_dfs: list[pd.DataFrame], folder: str, filename: str) -> str:
    """
    Function to write a parque file from a list of Pandas DataFrames.

    Parameters
    ----------
    all_dfs: list with all Pandas Dataframes
    filename: file path of .parquet file

    """
    import os

    # make destination folder, if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    df = pd.concat(all_dfs)
    df.reset_index(inplace=True, drop=True)
    pq_file = f"{folder}{filename}.parquet"
    df.to_parquet(path=pq_file,
                  index=False, compression="snappy", engine="pyarrow")

    return pq_file


@task(retries=3, retry_delay_seconds=10)
def upload_parquet(filename: str) -> None:
    """
    Function to upload a parque file to Google Cloud Storage

    Parameters
    filename: file path of .parquet file
    ----------
    all_dfs: list with all Pandas Dataframes

    """
    path = Path(filename)

    # gcs_bucket = GcsBucket.load(name="gcs-bucket", validate=False)
    gcp_cloud_storage_bucket_block = GcsBucket.load("gcs-bucket")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path)
    

@task(retries=3, retry_delay_seconds=10)
def create_bg_ext_table(tablename: str) -> None:
    """
    Function to create a external table in BigQuery
    and uses parquet files at Cloude Storage

    Parameters
    tablename: name of the table

    """

    gcs_bucket_block = GcsBucket.load("gcs-bucket")
    uri_gcs = gcs_bucket_block.bucket + "/" + gcs_bucket_block.bucket_folder

    # with BigQueryWarehouse(gcp_credentials=gcp_cred) as warehouse:
    with BigQueryWarehouse.load("gcp-bq") as warehouse:
        sql = f"""
               CREATE OR REPLACE EXTERNAL TABLE `br_weather.{tablename}`
                   OPTIONS (
                    format = 'PARQUET',
                    uris = ['gs://{uri_gcs}*.parquet']
                   );
                """
        warehouse.execute(sql)
    

if __name__ == "__main__":
    pass
