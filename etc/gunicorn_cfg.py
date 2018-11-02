import os
import multiprocessing

bind = "unix:/run/gunicorn.sock"
workers = os.getenv('WORKER_NUM', multiprocessing.cpu_count() * 2 + 1)
