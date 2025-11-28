import os
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
OUTPUT_FOLDER = f"sheets/output/{date}"

def ensure_output_folder():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

def log_success(username):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_FOLDER, "exitos.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_fail(username, reason):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_FOLDER, "fallos.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def save_unprocessed(unprocessed_list):
    ensure_output_folder()
    df = pd.DataFrame({"username": unprocessed_list})
    path = os.path.join(OUTPUT_FOLDER, "no_procesados.csv")
    df.to_csv(path, index=False)
