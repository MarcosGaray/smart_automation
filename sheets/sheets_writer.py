import os
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
OUTPUT_FOLDER = f"sheets/output/{date}"
OUTPUT_CONNECTION_RESULTS_FOLDER = f"{OUTPUT_FOLDER}/connection-results"
OUTPUT_SVLAN_FOLDER = f"{OUTPUT_FOLDER}/check_svlan"

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
    path = os.path.join(OUTPUT_FOLDER, "migration-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_disconected_success(username, reason):
    ensure_output_folder()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_FOLDER, "disconected-success.csv")
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


def log_connection_success(username,onu_url):
    ensure_output_folder(OUTPUT_CONNECTION_RESULTS_FOLDER)
    df = pd.DataFrame([{
        "username": username,
        "onu_url": onu_url,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_CONNECTION_RESULTS_FOLDER, "connection-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_connection_fail(username, reason, onu_url):
    ensure_output_folder(OUTPUT_CONNECTION_RESULTS_FOLDER)
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "onu_url": onu_url,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_CONNECTION_RESULTS_FOLDER, "connection-fail.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_check_svlan_success(username):
    ensure_output_folder(OUTPUT_SVLAN_FOLDER)
    df = pd.DataFrame([{
        "username": username,
        "timestamp": datetime.now().isoformat()
    }])
    path = os.path.join(OUTPUT_SVLAN_FOLDER, "check-svlan.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def save_unprocessed(unprocessed_list):
    ensure_output_folder()
    df = pd.DataFrame({"username": unprocessed_list})
    path = os.path.join(OUTPUT_FOLDER, "not-processed.csv")
    df.to_csv(path, index=False)

def backup_success_block(block_number):
    """
    Copia migration-success.csv dentro de processed-blocks-backup
    y luego lo vacía.
    """
    ensure_output_folder()

    backup_folder = os.path.join(OUTPUT_FOLDER, "processed-blocks-backup")
    os.makedirs(backup_folder, exist_ok=True)

    original_path = os.path.join(OUTPUT_FOLDER, "migration-success.csv")
    if not os.path.exists(original_path):
        return False

    backup_path = os.path.join(backup_folder, f"migration-success-block-{block_number}.csv")

    # Copiar el archivo
    df = pd.read_csv(original_path)
    df.to_csv(backup_path, index=False)

    # **Vaciar el original**
    pd.DataFrame(columns=df.columns).to_csv(original_path, index=False)

    return True
