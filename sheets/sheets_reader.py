import pandas as pd
import os
from sheets.sheets_writer import OUTPUT_FOLDER

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


def load_check_connection_list(path=None):
    if path is None:
        path = os.path.join(OUTPUT_FOLDER, "migration-success.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")

    df = pd.read_csv(path, dtype=str)

    # Asegurar columnas esperadas
    if not {"username", "url"}.issubset(df.columns):
        raise ValueError("El archivo debe tener columnas 'username' y 'url'.")

    # Eliminar filas vacías
    df = df.dropna(subset=["username", "url"])

    # Limpiar espacios
    df["username"] = df["username"].str.strip()
    df["url"] = df["url"].str.strip()

    # Devolver lista de tuplas
    return list(df[["username", "url"]].itertuples(index=False, name=None))


def load_debbuggin_check_connection_list(path="sheets/input/debbuggin-connection-onus.txt"):
    if path is None:
        path = os.path.join(OUTPUT_FOLDER, "migration-success.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext in [".txt", ".csv"]:
        df = pd.read_csv(
            path,
            sep=",",
            engine="python",
            encoding="utf-8-sig",
            header=None,
            names=["username", "url"],
            dtype=str
        )
    else:
        raise ValueError("Formato no soportado. Usa TXT o CSV.")

    # Devolver lista de tuplas
    return list(df[["username", "url"]].itertuples(index=False, name=None))
