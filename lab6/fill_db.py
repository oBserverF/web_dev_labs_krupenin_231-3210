import sqlite3

DB_PATH = 'lab6.db'
SQL_PATH = 'zapolnenie.sql'

def run_sql_script(db_path, sql_path):
    with sqlite3.connect(db_path) as conn:
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        # Split by semicolon, execute each statement
        for statement in sql.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    conn.execute(stmt)
                except Exception as e:
                    print(f'Error executing: {stmt[:80]}...')
                    print(f'Error: {e}')
        conn.commit()
        print('DB filled from zapolnenie.sql')

if __name__ == '__main__':
    run_sql_script(DB_PATH, SQL_PATH)
