#!/usr/bin/env python3
"""
🛰️ ANGELUS GDRIVE & TELEMETRY CLIENT
Permite a Jules y agentes subir archivos a Google Drive y reportar telemetría a Google Sheets.
Autor: Perez, Ernesto Rafael ("Rafa") & Angelus AGI
"""

import sys
import os
import json
import base64
import argparse
import requests
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzhqS3u9QeWAe4kmTR1Z2UiGJEsDvL1u2_njawat86-BqBKKXO7d4kL4RvEt4yLEqs/exec"
SECRET_API_KEY = "ANGELUS_SISTEMA_SOBERANO_2026"
REPO_ID = "0032"
REPO_NAME = "ghost-reseller-hub"

def report_status(estado=None, progreso=None, tarea=None, notas=None):
    payload = {
        "token": SECRET_API_KEY,
        "action": "update_repo_status",
        "id": REPO_ID,
        "nombre": REPO_NAME
    }
    if estado: payload["estado"] = estado
    if progreso: payload["progreso_jules"] = progreso
    if tarea: payload["proxima_tarea"] = tarea
    if notas: payload["notas_jules"] = notas

    print(f"[*] Enviando telemetría de {REPO_ID}-{REPO_NAME} a Google Sheets...")
    try:
        r = requests.post(WEB_APP_URL, json=payload, timeout=30, allow_redirects=True)
        if r.status_code == 200:
            print(f"[+] Éxito: {r.json().get('message', 'Telemetría enviada')}")
        else:
            print(f"[!] Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[!] Error de conexión: {e}")

def upload_file_to_drive(file_path_str):
    p = Path(file_path_str)
    if not p.exists():
        print(f"[!] Error: El archivo {file_path_str} no existe.")
        return

    print(f"[*] Codificando archivo {p.name} ({p.stat().st_size} bytes)...")
    with open(p, "rb") as f:
        file_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "token": SECRET_API_KEY,
        "action": "upload_file",
        "id": REPO_ID,
        "nombre": REPO_NAME,
        "filename": p.name,
        "file_base64": file_b64
    }

    print(f"[*] Subiendo {p.name} a la carpeta Google Drive de {REPO_ID}-{REPO_NAME}...")
    try:
        r = requests.post(WEB_APP_URL, json=payload, timeout=60, allow_redirects=True)
        if r.status_code == 200:
            res = r.json()
            if res.get("status") == "success":
                print(f"[+] ¡Archivo subido exitosamente a Google Drive!")
                print(f"[*] Nombre: {res.get('file_name')}")
                print(f"[*] URL: {res.get('file_url')}")
            else:
                print(f"[!] Respuesta: {res}")
        else:
            print(f"[!] Error HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[!] Error al subir a Google Drive: {e}")

def list_drive_files():
    payload = {
        "token": SECRET_API_KEY,
        "action": "list_files",
        "id": REPO_ID,
        "nombre": REPO_NAME
    }
    print(f"[*] Consultando archivos en Google Drive para {REPO_ID}-{REPO_NAME}...")
    try:
        r = requests.post(WEB_APP_URL, json=payload, timeout=30, allow_redirects=True)
        if r.status_code == 200:
            res = r.json()
            files = res.get("files", [])
            print(f"[+] Total archivos encontrados en Drive: {len(files)}")
            for f in files:
                print(f"  - 📄 {f['name']} ({f['size']} bytes) -> {f['url']}")
        else:
            print(f"[!] Error HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[!] Error al listar archivos: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cliente Google Drive & Telemetría Angelus")
    parser.add_argument("--status", help="Estado general (ej: '🟢 100% tests pasados')")
    parser.add_argument("--progreso", help="Progreso Jules (ej: '5/9 tareas (55%)')")
    parser.add_argument("--task", help="Próxima tarea a ejecutar")
    parser.add_argument("--notes", help="Notas breves o bitácora de la sesión")
    parser.add_argument("--upload", help="Ruta del archivo a subir a Google Drive")
    parser.add_argument("--list", action="store_true", help="Listar archivos en Google Drive")

    args = parser.parse_args()

    if args.upload:
        upload_file_to_drive(args.upload)
    elif args.list:
        list_drive_files()
    elif args.status or args.progreso or args.task or args.notes:
        report_status(args.status, args.progreso, args.task, args.notes)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
