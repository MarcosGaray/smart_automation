import os
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
OUTPUT_FOLDER = f"sheets/output/{date}"
OUTPUT_CONNECTION_RESULTS_FOLDER = f"{OUTPUT_FOLDER}/connection-results"

def ensure_output_folder(path=None):
    if path is None:
        path = OUTPUT_FOLDER
    if not os.path.exists(path):
        os.makedirs(path)

def log_migration_success(username,url):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "url": url,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_FOLDER, "migration_success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_disconected_success(username, reason):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_FOLDER, "disconected_success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_fail(username, reason):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_FOLDER, "failure.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_connection_success(username):
    ensure_output_folder(OUTPUT_CONNECTION_RESULTS_FOLDER)
    df = pd.DataFrame([{
        "username": username,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_CONNECTION_RESULTS_FOLDER, "connection-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_connection_fail(username):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_CONNECTION_RESULTS_FOLDER, "connection-fail.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)



def save_unprocessed(unprocessed_list):
    ensure_output_folder()
    df = pd.DataFrame({"username": unprocessed_list})
    path = os.path.join(OUTPUT_FOLDER, "no_procesados.csv")
    df.to_csv(path, index=False)
