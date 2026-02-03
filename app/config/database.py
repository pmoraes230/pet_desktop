import mysql.connector

def connectdb():
    conn = mysql.connector.connect(
        host="localhost",   
        user="root",
        password="",
        database="pet_desktop"
    )
    return conn

def closedb(conn):
    conn.close()    
    