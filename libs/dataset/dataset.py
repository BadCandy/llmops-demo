import sqlite3
from typing import Dict, Optional, List, Any

from libs.util.secret import DEFAULT_DATABASE_PATH

# TODO: 추후 데이터셋 버저닝할수 있도록 개선
class Dataset:

    def __init__(self, dataset_id: int, database: str = DEFAULT_DATABASE_PATH):
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.dataset_id = dataset_id

    def add_entry(
            self,
            input_variables: Dict[str, Any],
            reference_output: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO data (dataset_id, input_variables, reference_output, metadata)
            VALUES (?, ?, ?, ?)
        ''', (self.dataset_id,
              str(input_variables),
              reference_output,
              str(metadata) if metadata else None))
        self.conn.commit()

    def get_entries(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT input_variables, reference_output, metadata FROM data WHERE dataset_id = ?",
            (self.dataset_id,)
        )
        rows = cursor.fetchall()
        return [
            {
                "input_variables": eval(row[0]),
                "reference_output": row[1],
                "metadata": eval(row[2]) if row[2] else None
            }
            for row in rows
        ]

    def delete_entry(self, entry_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM data WHERE id = ? AND dataset_id = ?", (entry_id, self.dataset_id))
        self.conn.commit()
