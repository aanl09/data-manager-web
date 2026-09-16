"""Data backends package."""

from .base import DataBackend


def get_backend(name: str) -> DataBackend:
    """Factory: kembalikan instance backend sesuai nama ('local' atau 'sheets')."""
    if name == "sheets":
        from .gsheets import GoogleSheetsBackend
        return GoogleSheetsBackend()
    from .local_csv import LocalCSVBackend
    return LocalCSVBackend()
