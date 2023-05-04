## How to execute my project
As the final capstone, we are supposed to run fellow's projects at our machines. So I'll summarize here how you can run my project. You will need a Mac or Linux Machine(like Ubuntu 22.04). Windows folks could use Ubuntu 22.04 at WSL2 withou problem.

### Setup Google Cloud Plataform for a new project
1. Access [GPC New Project by clicking here](https://console.cloud.google.com/projectcreate)
1. Define for Project name and for Project ID: `br-weather-your-name`
1. Go to [IAM & Admin >> Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) and create a New Service Account.
    1. Put in Service account name: `admin-svc`
    1. Assign these roles for your new account:
    - BigQuery Admin
    - Compute Admin
    - Storage Admin
    - Storage Object Admin
    - Viewer
    >For real world projects, you **must** create more granular rules for your service accounts.
    1. At [IAM & Admin >> Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) click over your `admin-svc` account.
    1. In the new page, click in KEYS >> [ADD KEYS] >> Create new key >> * JSON >> CREATE
    1. A new file will be downloaded, *keep it safe*, never publish it to public shares (GitHub, PasteBin, etc).
1. For the first use, go to [Compute Engine](https://console.cloud.google.com/compute) and enable *Compute Engine API* in the new page.
1. Setup Google Cloud SDK at your computer ([Item 4 for instructions](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/2_gcp_overview.md#initial-setup))
1. Setup Terraform at your computer. [Instructions here](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/1_terraform_overview.md)

### Git Clone Me
It's time to clone this repositorie to a folder in your PC.
In your shell, run this:
```bash
cd ~
git clone https://github.com/romiof/brazil-weather.git
cd brazil-weather
```

### How to use Terraform
At folder `brazil-weather/terraform` run this to download all artifacts:
```bash
terraform init
```
My terraform recipe will setup three GCP objects at "us-west1" / "us-west1-a", to use GCP Free Tier.
- A Google Cloud Storage Bucket
- A Big Query Dataset
- A Ubuntu 22.04 VM type `e2-medium` *(which charges about $0.03 hourly)*
> Keep an [eye here](https://cloud.google.com/free/docs/free-cloud-features#free-tier-usage-limits) to see your free tier limits

Also for the VM, will be created a swap file and all PIP requeriments will be installed. Prefect agent will start with VM root user.
Need to use this approach, because all of us are out of GCP 90-days trial, and now we must pay for some resources ;)

Here how to plan / apply / destroy yor cloud resources:
```bash
terraform plan 
    -var="project=your-gcp-project-id" \
    -var="PREFECT_API_KEY=your_prefect_cloud_token_api" \
    -var="PREFECT_WORKSPACE=prefect_cloud/workspace_string"

terraform apply \
    -var="project=your-gcp-project-id" \
    -var="PREFECT_API_KEY=your_prefect_cloud_token_api" \
    -var="PREFECT_WORKSPACE=prefect_cloud/workspace_string"

terraform destroy \
    -var="project=your-gcp-project-id" \
    -var="PREFECT_API_KEY=your_prefect_cloud_token_api" \
    -var="PREFECT_WORKSPACE=prefect_cloud/workspace_string"
```

### Prefect Cloud
Use your Prefect Cloud Key / Workspace to complete terraform command variables.
- [API Keys here](https://app.prefect.cloud/my/api-keys)
- [Workspace at main page](https://app.prefect.cloud/)

Now on Prefect Cloud, let's create all needed blocks.
Under `Blocks` create four itens:
1. GCP Credentials / gcp-login *
1. GCS / gcs-prefect *
1. BigQuery Warehouse / gcp-bq **
1. GCS Bucket / gcs-bucket **

\* Under these blocks, you must *copy/paste* the content of your [GCP Service Account JSON Key](README.md#setup-google-cloud-plataform-for-a-new-project)

\** And under these, you must associate with `gcp-login` created early.

<details>
![Prefect Blocks](/assets/prefect-cloud-blocks.png)
</details>

### Python, VirtualEnv and Prefect Local
First of all, in your PC:
- Install Python 3.10 (or newer) 
- Install [VirtualEnv](https://virtualenv.pypa.io/en/latest/)

Then follow this to create a VENV:

```bash
cd ~/brazil-weather
virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requeriments.txt
```
A VirtualEnv was created at your project folder and all PiP requeriments has been downloaded.
Login to Prefect Cloud.
```bash
cd ~/brazil-weather
prefect cloud login -k <your_prefect_cloud_token_api>
prefect cloud workspace set --workspace <prefect_cloud/workspace_string>
prefect config set PREFECT_API_ENABLE_HTTP2=false
```
> Prefect Agents / Cloud are having some troubles with HTTP2, for this, I suggest you disable it for a while. [GitHub Issue](https://github.com/PrefectHQ/prefect/issues/7442)

Now lets deploy our flow to Cloud Workspace.
It will use a sub-folder `/flows/`, under GCS Bucket (from Prefect Block), to save our `.py` files.
After that, our `Prefect Agent` will download these files in each execution.

```bash
cd ~/brazil-weather/prefect
prefect deployment build elt_flow.py:main_flow -n brazil-weather-flow -sb gcs/gcs-prefect/flows -q default --cron "0 5 * * *" -o brazil-weather-flow.yaml
```
My default parameters are a JSON/Dict attributes, and I can't figure how to include them at `deployment build`.
So, please edit the file `brazil-weather-flow.yaml` , under *parameters* key, include this:
```yaml
parameters:
  dict_param:
    BASE_URL: https://portal.inmet.gov.br/uploads/dadoshistoricos/
    DEST_DIR: ./dump_zips/
    FILE_EXT: .zip
    START_YEAR: 2013
    END_YEAR: 2023
```

<details>
![Deployment Parameters](/assets/prefect-yaml.png)
</details>

Now lets apply it to Prefect Cloud, and you will see it at your environment:
```bash
prefect deployment apply brazil-weather-flow.yaml
```
<details>
![Prefect Cloud Deployment](/assets/prefect-cloud-deployment.png)
</details>

This *deployment* has a schedule to run once a day, at UTC 05:00 AM.


### dbt Cloud


### Looker Studio
url
imagem

