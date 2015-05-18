import os

from flask import Flask
from postmates.postmates import PostmatesAPI

app = Flask(__name__)

pm = PostmatesAPI('dc937388-2da1-4652-b539-e77b45d478e2', 'cus_It8IMxcQUK4_ik')

@app.route('/')
def hello():
  return 'Hello World!'
