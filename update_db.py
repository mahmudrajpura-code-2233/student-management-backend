import sqlite3
import os

db_path = 'school.db'
if not os.path.exists(db_path):
    print('Database not found at', db_path)
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    columns = [
        ('gr_no', 'VARCHAR(50)'),
        ('father_name', 'VARCHAR(100)'),
        ('mother_name', 'VARCHAR(100)'),
        ('dob', 'DATE'),
        ('primary_phone', 'VARCHAR(20)'),
        ('secondary_phone', 'VARCHAR(20)'),
        ('aadhaar_number', 'VARCHAR(20)'),
        ('photo_url', 'VARCHAR(255)'),
        ('address', 'TEXT'),
        ('total_yearly_fees', 'FLOAT')
    ]
    for col, ctype in columns:
        try:
            cur.execute(f'ALTER TABLE students ADD COLUMN {col} {ctype}')
            print(f'Successfully added {col}')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'Column {col} already exists, skipping...')
            else:
                print(f'Error adding {col}:', e)
    conn.commit()
    conn.close()
    print("Database update complete!")
