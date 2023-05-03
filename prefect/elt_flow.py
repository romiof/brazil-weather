from datetime import date
import os
import extras.functions as ef
from prefect import flow


@flow(log_prints=True, retries=3, retry_delay_seconds=10, persist_result=False)
def extract_load(site_url: str, to_folder: str, file_type: str, start_year: int, end_year: int) -> None:

    YEARS_TO_DOWNLOAD = range(start_year, end_year + 1)

    # downloads
    print("Started to download files.")
    for year in YEARS_TO_DOWNLOAD:
        work_dir = to_folder
        print(f"Downloading {year}.zip")
        downloaded_file = ef.downloader(url=f"{site_url}{year}{file_type}",
                                        folder=work_dir, filename=f"{year}{file_type}")

        # unzip
        zip_ext_dir = ef.unziper(
            zip_file=downloaded_file, folder=work_dir, year=year)

        # csvs to df
        print(f"CSVs {year}.zip to DataFrame")
        all_dfs_list = ef.csv_to_pd(foldername=zip_ext_dir)

        # remove sub-folder container for year, if so
        sub_folder = work_dir + str(year)
        if os.path.exists(sub_folder):
            os.rmdir(sub_folder)

        # df to parquet
        print(f"DataFrame {year} to Parquet")
        pq_file = ef.generate_parquet(all_dfs=all_dfs_list,
                                      folder="pqs/", filename=str(year))

        # parquet to GCS
        print(f"Upload {year}.Parquet to GCS")
        ef.upload_parquet(filename=pq_file)

    # remove working folder
    if os.path.exists(to_folder):
        os.rmdir(to_folder)


@flow(log_prints=True, retries=3, retry_delay_seconds=10, persist_result=False)
def main_flow(dict_param: dict) -> None:

    # Flow for Extract and Load
    extract_load(site_url=dict_param["BASE_URL"],
                 to_folder=dict_param["DEST_DIR"],
                 file_type=dict_param["FILE_EXT"],
                 start_year=dict_param["START_YEAR"],
                 end_year=dict_param["END_YEAR"],
                 )
    
    #create BG table
    ef.create_bg_ext_table("raw_zone")

    # Flow for dbt Transform
    

if __name__ == "__main__":
    flow_param = dict(
        BASE_URL="https://portal.inmet.gov.br/uploads/dadoshistoricos/",
        DEST_DIR="./dump_zips/",
        FILE_EXT=".zip",
        START_YEAR=date.today().year - 10,
        END_YEAR=date.today().year,
    )

    main_flow(dict_param=flow_param)
