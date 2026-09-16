"""Backend CSV lokal. Meniru perilaku Google Sheets untuk development/testing tanpa internet.

Satu file CSV per worksheet, disimpan di folder `data/` (mis. data/user.csv).
"""

import csv
import os
import threading
from typing import Dict, List

from .base import DataBackend

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class LocalCSVBackend(DataBackend):
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self._lock = threading.Lock()
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, worksheet: str) -> str:
        exact = os.path.join(self.data_dir, f"{worksheet}.csv")
        if os.path.exists(exact):
            return exact
        # fallback: cari file secara case-insensitive (tab Sheets "JB" -> jb.csv)
        target = f"{worksheet}.csv".lower()
        if os.path.isdir(self.data_dir):
            for fname in os.listdir(self.data_dir):
                if fname.lower() == target:
                    return os.path.join(self.data_dir, fname)
        return exact  # path default (untuk pembuatan file baru)

    def get_rows(self, worksheet: str, header_row: int = 1) -> List[Dict[str, str]]:
        # CSV lokal selalu memakai baris pertama sebagai header (header_row diabaikan).
        path = self._path(worksheet)
        if not os.path.exists(path):
            return []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [dict(r) for r in reader]

    def _headers(self, worksheet: str) -> List[str]:
        path = self._path(worksheet)
        if not os.path.exists(path):
            return []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            return next(reader, [])

    def _write_all(self, worksheet: str, headers: List[str], rows: List[Dict[str, str]]):
        path = self._path(worksheet)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({h: row.get(h, "") for h in headers})

    def append_row(self, worksheet: str, row: Dict[str, str],
                   header_row: int = 1) -> Dict[str, str]:
        with self._lock:
            headers = self._headers(worksheet)
            if not headers:
                headers = list(row.keys())
            # tambahkan kolom baru bila ada key yang belum ada di header
            for k in row:
                if k not in headers:
                    headers.append(k)
            rows = self.get_rows(worksheet)
            rows.append(row)
            self._write_all(worksheet, headers, rows)
            return {h: row.get(h, "") for h in headers}

    def update_row(self, worksheet: str, key_field: str, key_value: str,
                   updates: Dict[str, str], header_row: int = 1) -> Dict[str, str]:
        with self._lock:
            headers = self._headers(worksheet)
            rows = self.get_rows(worksheet)
            updated = None
            for row in rows:
                if str(row.get(key_field, "")).strip() == str(key_value).strip():
                    row.update(updates)
                    updated = row
                    break
            if updated is None:
                raise KeyError(f"Baris dengan {key_field}={key_value} tidak ditemukan")
            self._write_all(worksheet, headers, rows)
            return updated
