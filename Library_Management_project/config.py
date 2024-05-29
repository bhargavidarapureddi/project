import snowflake.connector
SECRET_KEY = '12345'

SNOWFLAKE = {
    'account': 'vbwwcwa-dw50854',
    'user': 'BhargaviD',
    'password': 'Bhargavi2@',
    'database': 'LMS',
    'schema': 'public'
}


def get_connection():
    try:
        # ** is used to unpack the dictionary
        return snowflake.connector.connect(**SNOWFLAKE)
    except Exception as e:
        print("An error occurred while connecting to Snowflake:", e)
        return None
 
SNOWFLAKE_CONNECTOR  = get_connection()