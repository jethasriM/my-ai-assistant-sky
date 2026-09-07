import sqlite3

db_name = "assistant.db"

def get_pending_task():
    try:
        with sqlite3.connect(db_name) as connect_obj:
            cursor_obj = connect_obj.cursor()
            
            cursor_obj.execute("UPDATE tasks SET delay_count = delay_count + 1 WHERE status = 'pending'")
            cursor_obj.commit()
            
            cursor_obj.execute("SELECT description, deadline_time, delay_count FROM tasks WHERE status = 'pending'")
            rows = cursor_obj.fetchall()
            cursor_obj.close()
            
            return [{"Description": r[0], "time": r[1], "delay_count": r[2]} for r in rows]
        
    except FileNotFoundError:
            print(f"Error '{db_name}' not found...")
    except sqlite3.Error as e:
            print(f"Database error: '{e}' ")    
    except Exception as e:  
            print(f"Unexpected error: '{e}'")    
        
            
            
        
        
