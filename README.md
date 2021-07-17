# Android-Backup-App-Web-Service
A Web Service API implementation for an Android's application's backup App with Flask.

## How to Run
1. python -m venv .env<br/>
2. source .env/bin/activate<br/>
3. python -m pip install -r requirements.txt<br/>
4. python app.py<br/>

## API Documentation
/backup<br/>
To backup a single app<br/>
POST request<br/>
user: user ID<br/>
app_name: Android application complete package name<br/>
app_version: version number<br/>
<br/>
/upload<br/>
To upload the backed up app in case it's not already availible in Server<br/>
POST request<br/>
user: user ID<br/>
app_name: Android application complete package name<br/>
app_version: version number<br/>
file: apk file<br/>
<br/>
/download<br/>
To download the backed up app<br/>
POST request<br/>
user: user ID<br/>
app_name: Android application complete package name<br/>
<br/>
/user<br/>
To get a list of backed up apps of a user<br/>
POST request<br/>
user: user ID<br/>
<br/>
/remove<br/>
To remove an app from user's backup<br/>
POST request<br/>
user: user ID<br/>
app_name: Android application complete package name<br/>
