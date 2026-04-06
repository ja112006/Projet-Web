import sqlite3

DATABASE = 'rdv.db'


def get_db(): # Pour get la db
    tab = sqlite3.connect(DATABASE)
    tab.row_factory = sqlite3.Row
    return tab


def execute_query(query, params=(), fetch_one=False, fetch_all=False): # Pour executer sans devoir créer un cursor à chaque fois
    tab = get_db()
    cursor = tab.cursor()
    
    cursor.execute(query, params)
    
    if fetch_one:
        result = cursor.fetchone()
    elif fetch_all:
        result = cursor.fetchall()
    else:
        tab.commit()
        result = cursor.lastrowid
    
    tab.close()
    return result
