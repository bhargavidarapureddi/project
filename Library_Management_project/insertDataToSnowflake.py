import snowflake.connector
from config import SNOWFLAKE_CONNECTOR

conn = SNOWFLAKE_CONNECTOR

cur = conn.cursor()

data = (1, 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 4)

cur.execute("""
    INSERT INTO LMS.PUBLIC.BOOK_DETAILS (BOOK_ID, BOOK_NAME, AUTHOR, GENRE, QUANTITY)
    VALUES (%s, %s, %s, %s, %s)
""", data)

conn.commit()

cur.close()
conn.close()
