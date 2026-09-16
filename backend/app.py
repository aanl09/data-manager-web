"""Flask app: REST API untuk query/update data + serve frontend statis."""

import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import config
from backends import get_backend

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = Flask(__name__, static_folder=None)
CORS(app)

backend = get_backend(config.DATA_BACKEND)


def _sheet_cfg(sheet: str):
    cfg = config.SHEETS.get(sheet)
    if cfg is None:
        return None
    return cfg


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "backend": config.DATA_BACKEND,
                    "sheets": list(config.SHEETS.keys())})


@app.get("/api/<sheet>")
def query_sheet(sheet):
    """Query generik berbasis konfigurasi search_fields.

    Contoh:
      GET /api/jb?JB=123
      GET /api/terminasi?TERMINASI=abc
      GET /api/user?ID=1&SID=xyz
      GET /api/sarpen?SITE=SITE01
    """
    cfg = _sheet_cfg(sheet)
    if cfg is None:
        return jsonify({"error": f"sheet '{sheet}' tidak dikenal"}), 404

    filters = {}
    for field in cfg["search_fields"]:
        val = request.args.get(field)
        if val not in (None, ""):
            filters[field] = val

    try:
        rows = backend.search(cfg["worksheet"], filters, cfg.get("header_row", 1))
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": str(e)}), 500

    # kolom yang ingin ditonjolkan (mis. DESTINATION untuk terminasi)
    highlight = cfg.get("extra_return", [])
    return jsonify({
        "sheet": sheet,
        "count": len(rows),
        "search_fields": cfg["search_fields"],
        "highlight": highlight,
        "rows": rows,
    })


@app.post("/api/<sheet>")
def create_row(sheet):
    """Tambah baris baru -> otomatis update spreadsheet."""
    cfg = _sheet_cfg(sheet)
    if cfg is None:
        return jsonify({"error": f"sheet '{sheet}' tidak dikenal"}), 404
    payload = request.get_json(silent=True) or {}
    if not payload:
        return jsonify({"error": "body JSON kosong"}), 400
    try:
        saved = backend.append_row(cfg["worksheet"], payload, cfg.get("header_row", 1))
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "created", "row": saved}), 201


@app.put("/api/<sheet>/<key_value>")
def update_row(sheet, key_value):
    """Update baris berdasarkan primary key -> otomatis update spreadsheet."""
    cfg = _sheet_cfg(sheet)
    if cfg is None:
        return jsonify({"error": f"sheet '{sheet}' tidak dikenal"}), 404
    payload = request.get_json(silent=True) or {}
    if not payload:
        return jsonify({"error": "body JSON kosong"}), 400
    try:
        row = backend.update_row(cfg["worksheet"], cfg["key"], key_value, payload,
                                 cfg.get("header_row", 1))
    except KeyError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "updated", "row": row})


# ---------------------------------------------------------------------------
# Frontend statis
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
