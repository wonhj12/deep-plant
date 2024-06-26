import os
from dotenv import load_dotenv
import multiprocessing

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bind = "0.0.0.0:8080"
workers = (2 * multiprocessing.cpu_count()) + 1
