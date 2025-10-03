import mysql.connector
def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    return conn