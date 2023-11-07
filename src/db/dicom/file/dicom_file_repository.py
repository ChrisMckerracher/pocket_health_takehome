from typing import Any


class DicomFileRepository:
    def get(self, id: int):
        raise NotImplementedError("Failed to implement the interface for method get")

    def save(self, id: int, file: Any):
        raise NotImplementedError("Failed to implement the interface for method save")
