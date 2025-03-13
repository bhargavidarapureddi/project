from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from SnowflakeCreds import snowflake_config

#SNOWFLAKE STRING
connection_string = f"snowflake://{snowflake_config['user']}:{snowflake_config['password']}@{snowflake_config['account']}.{snowflake_config['region']}/{snowflake_config['schema']}"
print(connection_string)

#CONFIGURE CONNECTION POOLING
pool_size = 10  # adjust pool size as needed
max_overflow = 10  # adjust max overflow connections as needed
recycle = 3600  # recycle connections after 1 hour (optional)

pool_config = QueuePool(
    creator=lambda: create_engine(connection_string),
    pool_size=pool_size,
    max_overflow=max_overflow,
    recycle=recycle,
)

# SQLALCHEMY ENIGNE POOLING
engine = create_engine(connection_string, poolclass=pool_config)

with engine.connect() as connection:
    result = connection.execute("SELECT * FROM PRODUCTS")
    for row in result:
        print(row)