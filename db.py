import sqlite3

def init_db():
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            name TEXT,
            path TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT,
            task_number_in_excel TEXT,
            task_code_in_moodle TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()
