import os
from flask import Flask

app = Flask(__name__)

print("Current working directory:", os.getcwd())
print("app.root_path:", app.root_path)
print("app.template_folder:", app.template_folder)
print("Files in current directory:", os.listdir())