import sqlite3

db_name = "assistant.db"
schema_file = "schema.sql"

def initialized_database():
    try:
        with sqlite3.connect(db_name) as connect_obj:
            cursor_obj = connect_obj.cursor()
            
            with open(schema_file, 'r') as f:
                schema_script = f.read()
                
            cursor_obj.executescript(schema_script)
            connect_obj.commit()
        
        print(f"Database '{db_name}' initialized successfully!")
        
    except FileNotFoundError:
        print(f"Error '{schema_file}' not found...")
    except sqlite3.Error as e:
        print(f"Database error: '{e}' ")
    except Exception as e:  
        print(f"Unexpected error: '{e}'")
    
if __name__ == "__main__":
    initialized_database()