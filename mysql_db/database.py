import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_mysql_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user = os.getenv('MYSQL_USER'),
            password = os.getenv('MYSQL_PASSWORD'),
            database = os.getenv('MYSQL_DATABASE'),
            port = int(os.getenv('MYSQL_PORT')),
            cursorclass = pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print('Failed to connect to MySQL: {e}')
        return None
    
if __name__ == "__main__":
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    print("Connected to:", cursor.fetchone())
    cursor.close()
    conn.close()
