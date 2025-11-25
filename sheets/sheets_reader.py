import pandas as pd
import os

def load_onu_list(path="sheets/input/onus.txt"):
    """
    Lee un archivo TXT o CSV que contenga una sola columna de usernames.
    Devuelve una lista de strings.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext in [".txt", ".csv"]:
        df = pd.read_csv(path, header=None, names=["username"], dtype=str)
    else:
        raise ValueError("Formato no soportado. Usa TXT o CSV.")

    # Limpiar filas vacías y espacios
    df["username"] = df["username"].astype(str).str.strip()
    df = df[df["username"] != ""]
    return df["username"].tolist()
