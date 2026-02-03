import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

def connectdb():
    conn = mysql.connector.connect(
        host=os.getenv("host"),   
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database"),
        port=os.getenv("port")
    )
    return conn

def closedb(conn):
    conn.close()    
    