import sqlite3
import sys
from pathlib import Path

DB_NAME = "assistant.db"
SCHEMA_FILE = "schema.sql"

def initialized_database(db_name:str = DB_NAME, schema_file:str = SCHEMA_FILE) -> None:
    schema_path = Path(schema_file)
    
    if not schema_path.exists():
        print(f"ERROR: schema file {schema_file} was not found."
              f"Run this script from the project root.", file = sys.stderr)
        sys.exit(1)
        
    connect_obj = None
    try:
        with sqlite3.connect(db_name) as connect_obj:
            cursor_obj = connect_obj.cursor()
            
            cursor_obj.execute("PRAGMA journal_mode = WAL;")
            mode = cursor_obj.fetchone()[0]
            if mode.lower() != "wal":
                print(f"WARNING: expected WAL mode, got '{mode}'."
                      f"Concurrent access might be less reliable", file = sys.stderr)
                
            cursor_obj.execute("PRAGMA foreign_keys = ON;")
            
            schema_script = schema_path.read_text()
            cursor_obj.executescript(schema_script)
            connect_obj.commit()
            
            print(f"Database '{db_name}' successfully initialized in (journal mode = {mode}).")
        
    except FileNotFoundError:
        print(f"Error '{db_name}' not found...")
    except sqlite3.Error as e:
        print(f"Database error: '{e}' ")
    except Exception as e:  
        print(f"Unexpected error: '{e}'")
    
if __name__ == "__main__":
    initialized_database()