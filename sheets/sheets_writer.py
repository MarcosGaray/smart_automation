import os
import pandas as pd
from datetime import datetime
from data import FOLDER_NAME

date = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
# Router general path
GENERAL_OUTPUT_FOLDER = f"exports/output/{FOLDER_NAME}"

# Router specific migration path by date
OUTPUT_FOLDER = f"{GENERAL_OUTPUT_FOLDER}/{date}"

# Special cases folders
OUTPUT_CONNECTION_RESULTS_FOLDER = f"{OUTPUT_FOLDER}/connection-results"
OUTPUT_SVLAN_FOLDER = f"{OUTPUT_FOLDER}/check_svlan"
OUTPUT_MORE_THAN_ONE_VLAN_FOLDER = f"{OUTPUT_FOLDER}/check_more_than_one_vlan"

def ensure_output_folder(path=None):
    if path is None:
        path = OUTPUT_FOLDER
    if not os.path.exists(path):
        os.makedirs(path)

# ================================
# LOGS NORMALES
# ================================

def log_migration_success(username,url):
    ensure_output_folder()
    timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "url": url,
        "timestamp": timestamp
    }])
    path = os.path.join(OUTPUT_FOLDER, "migration-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    log_all_migration_success(username, timestamp)
    log_all_success(username,"connected", timestamp)

def log_speed_change_success(username):
    ensure_output_folder()
    timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "timestamp": timestamp
    }])
    path = os.path.join(OUTPUT_FOLDER, "speed-change-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    log_all_migration_success(username, timestamp, filename="all-speed-change-success.csv")

    
def log_disconected_success(username, reason):
    ensure_output_folder()
    timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": timestamp
    }])
    path = os.path.join(OUTPUT_FOLDER, "disconnected-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    log_all_disconnected_success(username, reason, timestamp)
    log_all_success(username,"disconnected", timestamp)

def log_all_disconnected_success(username, reason, timestamp=None):
    ensure_output_folder(GENERAL_OUTPUT_FOLDER)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": timestamp
    }])
    path = os.path.join(GENERAL_OUTPUT_FOLDER, "all-disconnected-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_all_migration_success(username, timestamp=None, filename ="all-migration-success.csv"):
    ensure_output_folder(GENERAL_OUTPUT_FOLDER)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "timestamp": timestamp
    }])
    path = os.path.join(GENERAL_OUTPUT_FOLDER, filename)
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_all_success(username, status, timestamp=None):
    ensure_output_folder(GENERAL_OUTPUT_FOLDER)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "status": status,
        "timestamp": timestamp
    }])
    path = os.path.join(GENERAL_OUTPUT_FOLDER, "all-success.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_fail(username, reason):
    ensure_output_folder()
    timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": timestamp
    }])
    path = os.path.join(OUTPUT_FOLDER, "failure.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    log_all_fails(username, reason, timestamp)

def log_all_fails(username, reason, timestamp=None):
    ensure_output_folder(GENERAL_OUTPUT_FOLDER)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "reason": reason,
        "timestamp": timestamp
    }])
    path = os.path.join(GENERAL_OUTPUT_FOLDER, "all-fails.csv")
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

def log_check_svlan_success(username,svlan_status):
    ensure_output_folder(OUTPUT_SVLAN_FOLDER)
    timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "svlan_status": svlan_status,
        "timestamp": timestamp
    }])
    path = os.path.join(OUTPUT_SVLAN_FOLDER, "check-svlan.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

    log_all_check_svlans(username, svlan_status, timestamp)

def log_all_check_svlans(username, svlan_status, timestamp=None):
    ensure_output_folder(GENERAL_OUTPUT_FOLDER)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "svlan_status": svlan_status,
        "timestamp": timestamp
    }])
    path = os.path.join(GENERAL_OUTPUT_FOLDER, "all-check-svlans.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

def log_check_attached_vlans(username, message):
    ensure_output_folder(OUTPUT_MORE_THAN_ONE_VLAN_FOLDER)
    timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "message": message,
        "timestamp": timestamp
    }])
    path = os.path.join(OUTPUT_MORE_THAN_ONE_VLAN_FOLDER, "check-attached-vlans.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)

    log_all_attached_vlans(username, message, timestamp)

def log_all_attached_vlans(username, message, timestamp=None):
    ensure_output_folder(GENERAL_OUTPUT_FOLDER)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    df = pd.DataFrame([{
        "username": username,
        "message": message,
        "timestamp": timestamp
    }])
    path = os.path.join(GENERAL_OUTPUT_FOLDER, "all-attached-vlans.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False)



# ===========================================
# MANEJO SEGURO DE NOT-PROCESSED 
# ===========================================

def create_not_processed_temp(unprocessed_list):
    ensure_output_folder()
    
    path = os.path.join(OUTPUT_FOLDER, "not-processed-temp.csv")
    
    if os.path.exists(path):
        return
    
    df = pd.DataFrame({"username": unprocessed_list})
    df.to_csv(path, index=False)

def remove_from_not_processed_temp(onu_username):
    ensure_output_folder()

    path = os.path.join(OUTPUT_FOLDER, "not-processed-temp.csv")

    if not os.path.exists(path):
        # No deberia pasar, pero en caso extremo lo recreamos vacío
        pd.DataFrame({"username": []}).to_csv(path, index=False)
        return

    df = pd.read_csv(path)

    new_df = df[df["username"] != onu_username]

    # Guardado seguro (primero a archivo temporal, luego replace)
    temp_path = path + ".swap"
    new_df.to_csv(temp_path, index=False)
    os.replace(temp_path, path)

def rename_not_processed_temp():
    ensure_output_folder()

    temp_path = os.path.join(OUTPUT_FOLDER, "not-processed-temp.csv")
    final_path = os.path.join(OUTPUT_FOLDER, "no_procesados.csv")

    if not os.path.exists(temp_path):
        return

    os.replace(temp_path, final_path)

# ===========================
# BACKUP POR BLOQUES
# ===========================

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
