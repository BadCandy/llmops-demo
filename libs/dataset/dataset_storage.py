import sqlite3
from typing import List

from libs.dataset import Dataset
from libs.util.database import DEFAULT_DATABASE_PATH


class DatasetStorage:

    def __init__(self, database: str = DEFAULT_DATABASE_PATH):
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self._initialize_db()

    def _initialize_db(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
                NAME TEXT UNIQUE NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DATA (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER NOT NULL,
                TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP,
                input_variables TEXT NOT NULL,
                reference_output TEXT,
                metadata TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def create_dataset(self, name: str):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO datasets (name) VALUES (?)", (name,))
        self.conn.commit()

    def delete_dataset(self, name: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM datasets WHERE name = ?", (name,))
        self.conn.commit()

    def list_datasets(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM datasets")
        return [row[0] for row in cursor.fetchall()]

    def get_dataset(self, name: str) -> Dataset:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM datasets WHERE name = ?", (name,))
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"Dataset '{name}' does not exist.")

        dataset_id = result[0]
        return Dataset(
            dataset_id=dataset_id,
            database=self.database,
        )
