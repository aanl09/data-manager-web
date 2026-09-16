# Data Manager (Web)

Aplikasi manajemen data dengan **backend Python (Flask)** dan **frontend HTML/JS**,
memakai **Google Spreadsheet sebagai database**. Setiap action (tambah/update) otomatis
memperbarui spreadsheet.

## Sheet & cara query

| Sheet       | Cari berdasarkan | header_row | Hasil                                          |
|-------------|------------------|-----------|------------------------------------------------|
| `user`      | `ID` dan `SID`   | 1         | Data user (primary key)                        |
| `jb`        | `IDJB`           | 1         | Semua data + `Kabel 1..6` (daftar user/titik)  |
| `terminasi` | `TERMINASI`      | 2         | Semua data + kolom `DESTINATION` (disorot)     |
| `sarpen`    | `SITE`           | 2         | Semua data sarpen pada SITE tsb                |

> `header_row` = baris yang berisi nama kolom. Sheet dengan judul/merge di baris atas
> (terminasi, sarpen) memakai baris ke-2 sebagai header.

## Arsitektur

```
backend/
  app.py            # Flask app + REST API + serve frontend
  config.py         # Mapping sheet, kolom pencarian, header_row  <-- SESUAIKAN di sini
  backends/
    base.py         # Interface + logika search + normalisasi header
    local_csv.py    # Backend CSV lokal (dev / tanpa internet)
    gsheets.py      # Backend Google Sheets (produksi, via gspread, dukung header_row)
  data/             # Data contoh CSV (dipakai backend local)
  requirements.txt
frontend/
  index.html
  style.css
  app.js
```

## REST API

| Method | Endpoint                     | Fungsi                                  |
|--------|------------------------------|-----------------------------------------|
| GET    | `/api/health`                | Cek status + backend aktif              |
| GET    | `/api/user?ID=..&SID=..`     | Cari user                               |
| GET    | `/api/jb?IDJB=GTOJ064`       | Cari data JB                            |
| GET    | `/api/terminasi?TERMINASI=..`| Cari terminasi (+ DESTINATION)          |
| GET    | `/api/sarpen?SITE=..`        | Cari sarpen                             |
| POST   | `/api/<sheet>`               | Tambah baris (auto-update spreadsheet)  |
| PUT    | `/api/<sheet>/<key>`         | Update baris (auto-update spreadsheet)  |

## Menjalankan (mode LOCAL / CSV — tanpa internet)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATA_BACKEND=local
python app.py
# buka http://localhost:8000
```

## Menjalankan (mode Google Sheets)

1. Buat **Service Account** di Google Cloud, aktifkan **Google Sheets API** + **Google Drive API**.
2. Buat & unduh kunci **JSON** service account.
3. **Share spreadsheet** ke email service account (role **Editor**).
4. Set environment variable lalu jalankan:

```bash
export DATA_BACKEND=sheets
export GSHEET_ID=10pbJavqs6uIDJQ4jidygOF8Y_H2feIJoyAcgvULw_So
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
python app.py
```

## Menyesuaikan dengan spreadsheet aslimu

Edit `backend/config.py`:
- `worksheet`     : samakan dengan **nama tab** persis di spreadsheet.
- `header_row`    : baris yang berisi nama kolom (1 atau 2).
- `search_fields` : samakan dengan **nama header kolom** persis (case-sensitive).
- `extra_return`  : kolom yang ingin disorot (mis. `DESTINATION`).
- `key`           : kolom primary key untuk update.

> Catatan: nama kolom sheet `sarpen` masih perkiraan (screenshot resolusi kecil) —
> sesuaikan `config.py` + `data/sarpen.csv` bila ada yang berbeda.
> Cek juga apakah header sheet `user` ada di baris 1 atau 2.
