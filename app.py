
import os
from pathlib import Path
import json
from multiprocessing import Process

from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import redis
from redis import StrictRedis


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "upload"
Redis = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

def get_user_apps(user):
   if Redis.exists(user):
      return Redis.lrange(user, 0, -1)
   else:
      return []

def set_user_apps(user, application_id, add_or_remove):
   if add_or_remove==0:
      Redis.lpush(user, application_id)
   else:
      Redis.lrem(user, 1, application_id)

def get_app_path(app_name):
   root_folder = app.config['UPLOAD_FOLDER']
   app_name_split = app_name.split(":")
   path = os.path.join(os.path.join(root_folder, app_name_split[0]), app_name_split[1])
   filename = app_name_split[0]+".apk"
   return path, filename

def app_exist_in_db(application_id):
   if Redis.exists(application_id):
      if Redis.get(application_id) == "True":
         return True
      else:
         return False
   else:
      return False

def add_app_backup(application_id):
   Redis.set(application_id, "True")

def remove_app_backup_if_no_user(application_id):
   for key in Redis.scan_iter():
      if ":" not in key:
         app_list = get_user_apps(key)
         if application_id in apps_list:
            return
   app_name_split = application_id.split(":")
   path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], app_name_split[0]), app_name_split[1])
   full_path = os.path.join(path, secure_filename(app_name_split[0]+".apk"))
   os.remove(full_path)
   os.rmdir(path)
   Redis.set(application_id, "False")
	
@app.route('/upload', methods = ['POST'])
def upload_app():
   if request.method == 'POST':
      user = request.form.get('user')
      app_name = request.form.get('app_name')
      app_version = request.form.get('app_version')
      application_id = app_name+":"+app_version
      uploaded_file = request.files['file']
      filename = secure_filename(app_name+".apk")
      path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], app_name), app_version)
      Path(path).mkdir(parents=True, exist_ok=True)
      uploaded_file.save(os.path.join(path, filename))
      add_app_backup(application_id)
      apps_list = get_user_apps(user)
      if application_id not in apps_list:
         set_user_apps(user, application_id, 0)
      return 'file uploaded successfully', 200

@app.route('/backup', methods = ['POST'])
def backup_app():
   user = request.form.get('user')
   app_name = request.form.get('app_name')
   app_version = request.form.get('app_version')
   application_id = app_name+":"+app_version
   if not app_exist_in_db(application_id):
      return 'upload app', 200
   else:
      apps_list = get_user_apps(user)
      if application_id not in apps_list:
         set_user_apps(user, application_id, 0)
      return 'backup successful', 200

@app.route('/download', methods = ['POST'])
def download_app():
   user = request.form.get('user')
   app_name = request.form.get('app_name')
   apps_list = get_user_apps(user)
   application_id = ""
   for app in apps_list:
      if app.split(":")[0] == app_name:
         application_id = app
   if application_id == "":
      return "no such app", 404
   if app_exist_in_db(application_id):
      path, filename = get_app_path(application_id)
      return send_from_directory(path, filename, as_attachment=True), 200
   return "no such app", 404

@app.route('/user', methods = ['POST'])
def get_user_app_list():
   user = request.form.get('user')
   apps_list = get_user_apps(user)
   json_apps_list = json.dumps(apps_list)
   return json_apps_list, 200

@app.route('/remove', methods = ['POST'])
def remove_app_backup():
   user = request.form.get('user')
   app_name = request.form.get('app_name')
   apps_list = get_user_apps(user)
   application_id = ""
   for app in apps_list:
      if app.split(":")[0] == app_name:
         application_id = app
   if application_id == "":
      return "no such app", 404
   apps_list = get_user_apps(user)
   if application_id in apps_list:
      index = apps_list.index(application_id)
      set_user_apps(user, application_id, 1)
      heavy_process = Process(target=remove_app_backup_if_no_user, daemon=True, args=(application_id,))
      heavy_process.start()
   return "remove successful", 200
		
if __name__ == '__main__':
   app.run(debug = True)
