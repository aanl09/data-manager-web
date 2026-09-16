"""Backend Google Sheets memakai gspread + service account.

Membaca via get_all_values() sehingga bisa menangani header di baris mana pun
(header_row) dan header kosong/duplikat (mis. kolom Status yang ter-merge).

Kebutuhan environment:
- GSHEET_ID                     : ID spreadsheet
- GOOGLE_APPLICATION_CREDENTIALS: path ke file JSON service account

Spreadsheet harus di-share ke email service account (role Editor) agar bisa auto-update.
"""

import os
import threading
from typing import Dict, List

from .base import DataBackend, normalize_headers

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsBackend(DataBackend):
    def __init__(self, sheet_id: str = None, creds_path: str = None):
        import gspread
        from google.oauth2.service_account import Credentials

        self.sheet_id = sheet_id or os.getenv("GSHEET_ID")
        creds_path = creds_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not self.sheet_id:
            raise RuntimeError("GSHEET_ID belum di-set")
        if not creds_path or not os.path.exists(creds_path):
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS tidak valid")

        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        self._client = gspread.authorize(creds)
        self._spreadsheet = self._client.open_by_key(self.sheet_id)
        self._lock = threading.Lock()

    def _ws(self, worksheet: str):
        return self._spreadsheet.worksheet(worksheet)

    def _read(self, worksheet: str, header_row: int):
        """Kembalikan (headers, list_of_dict) berdasarkan header_row (1-indexed)."""
        values = self._ws(worksheet).get_all_values()
        if len(values) < header_row:
            return [], []
        headers = normalize_headers(values[header_row - 1])
        data = []
        for raw in values[header_row:]:
            row = {headers[i]: (raw[i] if i < len(raw) else "")
                   for i in range(len(headers))}
            data.append(row)
        return headers, data

    def get_rows(self, worksheet: str, header_row: int = 1) -> List[Dict[str, str]]:
        return self._read(worksheet, header_row)[1]

    def append_row(self, worksheet: str, row: Dict[str, str],
                   header_row: int = 1) -> Dict[str, str]:
        with self._lock:
            ws = self._ws(worksheet)
            headers, _ = self._read(worksheet, header_row)
            values = [str(row.get(h, "")) for h in headers]
            ws.append_row(values, value_input_option="USER_ENTERED")
            return {h: str(row.get(h, "")) for h in headers}

    def update_row(self, worksheet: str, key_field: str, key_value: str,
                   updates: Dict[str, str], header_row: int = 1) -> Dict[str, str]:
        with self._lock:
            ws = self._ws(worksheet)
            headers, data = self._read(worksheet, header_row)
            if key_field not in headers:
                raise KeyError(f"Kolom key '{key_field}' tidak ada di worksheet")
            target = None
            target_row_number = None
            for i, rec in enumerate(data):
                if str(rec.get(key_field, "")).strip() == str(key_value).strip():
                    target = dict(rec)
                    target_row_number = header_row + 1 + i  # baris data pertama = header_row+1
                    break
            if target_row_number is None:
                raise KeyError(f"Baris dengan {key_field}={key_value} tidak ditemukan")

            target.update(updates)
            new_values = [str(target.get(h, "")) for h in headers]
            last_col = _col_letter(len(headers))
            ws.update(f"A{target_row_number}:{last_col}{target_row_number}",
                      [new_values], value_input_option="USER_ENTERED")
            return target


def _col_letter(n: int) -> str:
    """1 -> A, 26 -> Z, 27 -> AA ..."""
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result
