# POC-Team
## A proof of concept app designed to manage and moderate simple classroom's tasks.

● [Caution](#CAUTION)

● [How to config Postgres?](#How-to-config-Postgres?)

● [Fix for linux](#Fix-for-linux)

<!-- Copy-paste in your Readme.md file -->

<a href="https://next.ossinsight.io/widgets/official/analyze-repo-stars-history?repo_id=1020854412" target="_blank" style="display: block" align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://next.ossinsight.io/widgets/official/analyze-repo-stars-history/thumbnail.png?repo_id=1020854412&image_size=auto&color_scheme=dark" width="721" height="auto">
    <img alt="Star History of SkySplinter/POC-TAHW" src="https://next.ossinsight.io/widgets/official/analyze-repo-stars-history/thumbnail.png?repo_id=1020854412&image_size=auto&color_scheme=light" width="721" height="auto">
  </picture>
</a>

<!-- Made with [OSS Insight](https://ossinsight.io/) -->

<!-- Copy-paste in your Readme.md file -->

<a href="https://next.ossinsight.io/widgets/official/analyze-repo-pull-requests-size-per-month?repo_id=1020854412" target="_blank" style="display: block" align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://next.ossinsight.io/widgets/official/analyze-repo-pull-requests-size-per-month/thumbnail.png?repo_id=1020854412&image_size=auto&color_scheme=dark" width="721" height="auto">
    <img alt="Pull Request Size of SkySplinter/POC-TAHW" src="https://next.ossinsight.io/widgets/official/analyze-repo-pull-requests-size-per-month/thumbnail.png?repo_id=1020854412&image_size=auto&color_scheme=light" width="721" height="auto">
  </picture>
</a>

<!-- Made with [OSS Insight](https://ossinsight.io/) -->

# CAUTION

> [!CAUTION]
> Never, never, ***NEVER*** use Python string concatenation (+) or string parameters interpolation (%) to pass variables to a SQL query string.

# How to build this project...

To run this application on your device, follow these steps:

## Installation

1. Make sure you have python3 and pip installed...
```
sudo apt install python3 python3-pip
```
2. Download Streamlit
```
pip install streamlit
```
You can verify the installation with the following command:
```
streamlit hello
```
3. Install postgres
```
sudo apt install postgresql-common
```
4. Clone the project
```
git clone https://github.com/SkySplinter/POC-TAHW
cd POC-TAHW
```

## How to config Postgres?

1.
```
CREATE DATABASE hw_streamlit;
```
2.
```
\c hw_streamlit
```
3.
```
CREATE TABLE hw_cn (
f_name TEXT NOT NULL,
l_name TEXT NOT NULL,
university_code BIGINT NOT NULL PRIMARY KEY);
```
4.
```
COPY hw_cn(f_name, l_name, university_code) FROM 'db.csv' WITH (
FORMAT csv,
ENCODING 'UTF-8');
```
5.
```
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```
6.
```
CREATE TABLE admin (
    name TEXT PRIMARY KEY,
    password TEXT NOT NULL  -- will store hashed password
);
```
7.
```
INSERT INTO admin (name, password)
VALUES ('admin', crypt('admins_password', gen_salt('bf')));
```
8.
Install required packages:
```
sudo apt install python3-psycopg2
pip install streamlit-pdf-viewer
```

## Fix for linux

For linux you will encounter a permission denied error. so:
1.
```
sudo cp /home/user/POC-Team/db_test.csv /tmp/
sudo chmod 644 /tmp/db_test.csv
sudo chown postgres:postgres /tmp/db_test.csv
```
2. Log back in postgres:
```
sudo -i -u postgres
postgres
\c hw_streamlit
\copy hw_cn(f_name, l_name, university_code) FROM '/tmp/db_test.csv' WITH (FORMAT csv, ENCODING 'UTF-8');
```
3. exit :
```
\q 
exit
```
4. remove temp


## Run streamlit
```
streamlit run hw_login.py
```
