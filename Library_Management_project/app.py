from flask import Flask
from config import SNOWFLAKE_CONNECTOR,SECRET_KEY
from users import users_api
from librarian import librarians_api
 
app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.register_blueprint(users_api)
app.register_blueprint(librarians_api)


@app.route('/')
def home():
    if SNOWFLAKE_CONNECTOR:
        return "Yes"
    else:
        return "Connection Issues"


if __name__ == '__main__':
    app.run(debug=True)