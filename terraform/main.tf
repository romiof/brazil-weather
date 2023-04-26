terraform {
  required_version = ">= 1.0"
  backend "local" {}  # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${local.data_lake_bucket}-${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
  delete_contents_on_destroy = true
}

# CE instance
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance
resource "google_compute_instance" "default" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 15
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-OUTEREOF
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
rm /root/.prefect/storage/*
sudo apt update
sudo apt install python3-pip -y
export PREFECT_API_KEY=${var.PREFECT_API_KEY}
export PREFECT_WORKSPACE=${var.PREFECT_WORKSPACE}
pip3 install aiohttp==3.8.4 aiosignal==1.3.1 aiosqlite==0.18.0 alembic==1.10.3 anyio==3.6.2 apprise==1.3.0 asgi-lifespan==2.1.0 async-timeout==4.0.2 asyncpg==0.27.0 attrs==22.2.0 autopep8==2.0.2 cachetools==5.3.0 certifi==2022.12.7 cffi==1.15.1 charset-normalizer==3.1.0 click==8.1.3 cloudpickle==2.2.1 colorama==0.4.6 coolname==2.2.0 croniter==1.3.14 cryptography==40.0.2 dateparser==1.1.8 decorator==5.1.1 docker==6.0.1 fastapi==0.95.1 frozenlist==1.3.3 fsspec==2023.4.0 gcsfs==2023.4.0 google-api-core==2.11.0 google-api-python-client==2.85.0 google-auth==2.17.3 google-auth-httplib2==0.1.0 google-auth-oauthlib==1.0.0 google-cloud-bigquery==3.10.0 google-cloud-bigquery-storage==2.19.1 google-cloud-core==2.3.2 google-cloud-storage==2.8.0 google-crc32c==1.5.0 google-resumable-media==2.4.1 googleapis-common-protos==1.59.0 greenlet==2.0.2 griffe==0.27.0 grpcio==1.54.0 grpcio-status==1.54.0 h11==0.14.0 h2==4.1.0 hpack==4.0.0 httpcore==0.17.0 httplib2==0.22.0 httpx==0.24.0 hyperframe==6.0.1 idna==3.4 Jinja2==3.1.2 jsonpatch==1.32 jsonpointer==2.3 jsonschema==4.17.3 kubernetes==26.1.0 Mako==1.2.4 Markdown==3.4.3 markdown-it-py==2.2.0 MarkupSafe==2.1.2 mdurl==0.1.2 multidict==6.0.4 numpy==1.24.2 oauthlib==3.2.2 orjson==3.8.10 packaging==23.1 pandas==2.0.1 pathspec==0.11.1 pendulum==2.1.2 prefect==2.10.4 prefect-gcp==0.4.0 proto-plus==1.22.2 protobuf==4.22.3 pyarrow==11.0.0 pyasn1==0.4.8 pyasn1-modules==0.2.8 pycodestyle==2.10.0 pycparser==2.21 pydantic==1.10.7 Pygments==2.15.0 pyparsing==3.0.9 pyrsistent==0.19.3 python-dateutil==2.8.2 python-slugify==8.0.1 pytz==2023.3 pytz-deprecation-shim==0.1.0.post0 pytzdata==2020.1 PyYAML==6.0 readchar==4.0.5 regex==2023.3.23 requests==2.28.2 requests-oauthlib==1.3.1 rich==13.3.4 rsa==4.9 six==1.16.0 sniffio==1.3.0 SQLAlchemy==1.4.47 starlette==0.26.1 text-unidecode==1.3 toml==0.10.2 tomli==2.0.1 typer==0.7.0 typing_extensions==4.5.0 tzdata==2023.3 tzlocal==4.3 uritemplate==4.1.1 urllib3==1.26.15 uvicorn==0.21.1 websocket-client==1.5.1 websockets==11.0.1 yarl==1.8.2
prefect cloud login -k $PREFECT_API_KEY
prefect cloud workspace set --workspace $PREFECT_WORKSPACE
prefect agent start -q default
OUTEREOF
}