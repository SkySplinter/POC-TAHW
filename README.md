# POC-Team
A proof of concept app designed to manage and moderate simple team's tasks.

# Warning
Never, never, NEVER use Python string concatenation (+) or string parameters interpolation (%) to pass variables to a SQL query string.

# How to config Postgres?
1. \
CREATE DATABASE hw_streamlit;
2. \
\c hw_streamlit
3. \
CREATE TABLE hw_cn (
f_name TEXT NOT NULL,
l_name TEXT NOT NULL,
university_code BIGINT NOT NULL PRIMARY KEY);
4. \
COPY hw_cn(f_name, l_name, university_code) FROM 'db.csv' WITH (
FORMAT csv,
ENCODING 'UTF-8');
5. \
CREATE EXTENSION IF NOT EXISTS pgcrypto;
6. \
CREATE TABLE admin (
    name TEXT PRIMARY KEY,
    password TEXT NOT NULL  -- will store hashed password
);
7. \
INSERT INTO admin (name, password)
VALUES ('admin', crypt('admins_password', gen_salt('bf')));
8. Install required packages: \
sudo apt install python3-psycopg2
pip install streamlit-pdf-viewer

# Fix for linux
For linux you will encounter a permission denied error. so:
1. \
sudo cp /home/user/POC-Team/db_test.csv /tmp/
sudo chmod 644 /tmp/db_test.csv
sudo chown postgres:postgres /tmp/db_test.csv
2. Log back in postgres:
sudo -i -u postgres
postgres
\c hw_streamlit
\copy hw_cn(f_name, l_name, university_code) FROM '/tmp/db_test.csv' WITH (FORMAT csv, ENCODING 'UTF-8');
3. exit :
\q 
exit
4. remove temp
