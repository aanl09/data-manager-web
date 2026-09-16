"""
Konfigurasi pemetaan sheet & kolom (disesuaikan dengan struktur spreadsheet asli).

Setiap entri:
- worksheet    : nama tab di Google Sheets (juga nama file CSV di data/ untuk mode local)
- header_row   : baris ke berapa yang berisi NAMA KOLOM (1 = baris pertama).
                 Untuk sheet dengan judul/merge di atas, set ke 2, dst.
- search_fields: kolom yang dipakai untuk mencari
- extra_return : kolom yang ditonjolkan pada hasil (mis. DESTINATION untuk terminasi)
- key          : primary key logis (untuk update)
"""

import os

GSHEET_ID = os.getenv("GSHEET_ID", "10pbJavqs6uIDJQ4jidygOF8Y_H2feIJoyAcgvULw_So")
DATA_BACKEND = os.getenv("DATA_BACKEND", "local")

SHEETS = {
    # Cari user berdasarkan ID dan/atau SID
    "user": {
        "worksheet": "user",
        "header_row": 1,          # <- cek: apakah header user di baris 1 atau 2?
        "search_fields": ["ID", "SID"],
        "extra_return": [],
        "key": "ID",
    },
    # Cari IDJB -> tampilkan semua data (Kabel 1..6 berisi daftar user/titik)
    "jb": {
        "worksheet": "JB",
        "header_row": 1,
        "search_fields": ["IDJB"],
        "extra_return": [],
        "key": "IDJB",
    },
    # Cari terminasi -> tampilkan semua data + DESTINATION
    "terminasi": {
        "worksheet": "terminasi",
        "header_row": 2,          # <- header asli ada di baris 2 (baris 1 = judul/merge)
        "search_fields": ["TERMINASI"],
        "extra_return": ["DESTINATION"],
        "key": "TERMINASI",
    },
    # Cari sarpen berdasarkan SITE  (header grup di baris 1, nama kolom di baris 2)
    "sarpen": {
        "worksheet": "sarpen",
        "header_row": 2,          # <- baris 1 = judul grup (DATA CATU DAYA, dll), baris 2 = nama kolom
        "search_fields": ["SITE"],
        "extra_return": [],
        "key": "SITE",
    },
}
