import sqlite3
import pandas as pd


class SqLite:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: list[str]) -> None:
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
        self.conn.commit()
    
    def insert_data_from_csv(self, table_name: str, csv_path: str, if_exists: str = "replace") -> None:
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)
        self.conn.commit()

    def query_data(self, query: str, params: dict) -> list:
        query = query.format(**(params  or {}))
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        return rows