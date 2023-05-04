## Brazil Weather

This is my final project about the [DataTalksClub - Data Engineering Zoomcamp - 2023 Cohort](https://github.com/DataTalksClub/data-engineering-zoomcamp)
My purpose is to analyze Brazilian Weather Data, managed by [Instituto Nacional de Meteorologia (INMET)](https://portal.inmet.gov.br/).

INMET is a Brazilian government org which monitor weather data in almost 500 cities across whole country.


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

Then, all Parquet files will be uploaded to Google Cloud Storage, and a External Table in Big Query will link to its folder.

After that, the External Table will be processed by dbt to generate final data.

And using Looker Studio, we can see a nice view for all aggregate data.


## Toolset

1. [Google Cloud Platform(GCP)](https://cloud.google.com/): providing infrastructure for cloud computation, data lake storage and warehouse solution.
2. [Prefect](https://www.prefect.io/): to workflow and execute Python code following schedule definition.
3. [Python](https://www.python.org/): custom code with famous DE Libraries, like [Pandas](https://pandas.pydata.org/), to *Extract* and *Load* the data.
4. [Terraform](https://www.terraform.io/): to create and manipulate GCP resources using commands / CLI.
5. [dbt](https://www.getdbt.com/): solution to *Transform* data inside the [BigQuery](https://cloud.google.com/bigquery) and others warehouses.
6. [Looker Studio](https://lookerstudio.google.com): my dashboard solution, this is the final step of all data.


## How to execute my project
[Please follow to this page](HOW-TO-RUN.md) for instructions.


## Final Dashboard
[Link to Dashboard in Looker Studio](https://lookerstudio.google.com/reporting/47fbdd9c-7648-45da-8bce-ca84babc3969)

<details>

![Page 01](/assets/looker-01.png "Rain by year / seasson / state")
</details>

<details>

![Page 01](/assets/looker-02.png "High's and Low's Temperature")
</details>