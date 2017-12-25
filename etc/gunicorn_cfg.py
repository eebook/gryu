import os


bind = "unix:/tmp/gunicorn.sock"
workers = os.getenv('WORKER_NUM', 4)
