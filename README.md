## Brazil Weather

This is my final project about the [DataTalksClub - Data Engineering Zoomcamp - 2023 Cohort](https://github.com/DataTalksClub/data-engineering-zoomcamp)
My purpose is to analyze Brazilian Weather Data, managed by [Instituto Nacional de Meteorologia (INMET)](https://portal.inmet.gov.br/).

INMET is a Brazilian government org which monitor weather data in almost 500 cities across entire country.

## Data Analysis

In my analysis, I will show data about weather and temperature, around different states in the country. I also will show how is the raining distribution along the years and seasons.

Some insights I will show:

- What is the raining distribution in summer along the last 10 years.
- Raining distribution by country region.
- Total raining by state and year.
- Which station has the highest and the lowest temperature across the months.


## Data Pipeline in use

My project consists in batch pipeline. It'll download a Zip file for each year, from INMET's website.
Then each file will be extracted and all CSVs whom are inside Zip, will be converted to a Parquet file.
So, it'll have one Parquet file for each year. 
Then, all Parquet files are uploaded to Google Cloud Storage, and a External Table in Big Query will link to its folder.


## Toolset

1. Google Cloud Platform(GCP): providing infrastructure for cloud computation, data lake storage and warehouse solution.
2. Prefect: to workflow and execute Python code following schedule definition.
3. Python: custom code with famous DE Libraries, like Pandas, to Extract and Load the data.
4. Terraform: to create and manipulate GCP resources.
5. dbt: solution to Transform data inside the BigQuery Warehouse.
6. Looker: my dashboard solution, this is the final step of all data.


## How to execute my project
For all instructions, [please follow to this page](HOW-TO-RUN.md).