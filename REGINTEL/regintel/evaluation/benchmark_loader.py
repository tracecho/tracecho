import json
import os
from typing import List, Dict

class BenchmarkLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> List[Dict]:
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all(self):
        return self.data
