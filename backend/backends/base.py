"""Interface untuk data backend. Semua backend (CSV lokal / Google Sheets) mengikuti ini."""

from abc import ABC, abstractmethod
from typing import Dict, List


def normalize_headers(headers: List[str]) -> List[str]:
    """Ganti header kosong -> col_N dan pastikan tidak ada duplikat."""
    result = []
    seen = {}
    for i, h in enumerate(headers):
        name = (h or "").strip() or f"col_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        result.append(name)
    return result


class DataBackend(ABC):
    @abstractmethod
    def get_rows(self, worksheet: str, header_row: int = 1) -> List[Dict[str, str]]:
        """Kembalikan semua baris worksheet sebagai list of dict (key = header kolom)."""
        raise NotImplementedError

    @abstractmethod
    def append_row(self, worksheet: str, row: Dict[str, str],
                   header_row: int = 1) -> Dict[str, str]:
        """Tambah satu baris baru. Kembalikan baris yang tersimpan."""
        raise NotImplementedError

    @abstractmethod
    def update_row(self, worksheet: str, key_field: str, key_value: str,
                   updates: Dict[str, str], header_row: int = 1) -> Dict[str, str]:
        """Update baris yang match key_field == key_value. Kembalikan baris terbaru."""
        raise NotImplementedError

    def search(self, worksheet: str, filters: Dict[str, str],
               header_row: int = 1) -> List[Dict[str, str]]:
        """Cari baris yang cocok dengan SEMUA filter (case-insensitive, exact match).

        Filter bernilai kosong/None diabaikan. Kosong semua -> kembalikan semua baris.
        """
        rows = self.get_rows(worksheet, header_row)
        active = {k: str(v).strip() for k, v in filters.items() if v not in (None, "")}
        if not active:
            return rows
        result = []
        for row in rows:
            if all(str(row.get(f, "")).strip().lower() == v.lower()
                   for f, v in active.items()):
                result.append(row)
        return result
