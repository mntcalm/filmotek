import configparser
import os.path
from flask import Flask, render_template, url_for


class Db_details(object):
    def __init__(self, driver, name, host, port, login, password):
        self.driver = driver
        self.name = name
        self.host = host
        self.port = port
        self.login = login
        self.password = password


def parse_config():
    # Создаем объект ConfigParser, файл filmotek.conf рядом
    config = configparser.ConfigParser()
    try:
        program_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(program_dir, "filmotek.conf")
        config.read(config_path)
    # Получаем значениz параметрjd font из секции db
        db_driver = config.get("db", "driver")
        db_name = config.get("db", "name")
        db_host = config.get("db", "host")
        db_port = config.get("db", "port")
        db_l = config.get("db", "login")
        db_p = config.get("db", "password")
        return Db_details(db_driver, db_name, db_host, db_port, db_l, db_p)
    except:
        return Db_details("Failed", "to", "get.config", "404", "from", "file")


db_details = parse_config()
print(db_details.name)


app = Flask(__name__)


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/perechen")
def perechen():

    return render_template('perechen.html')


@app.route("/adding")
def adding():

    return render_template('adding.html')


@app.route("/editing")
def editing():

    return render_template('editing.html')


@app.route("/user_edit")
def user_edit():

    return render_template('user_edit.html')


@app.route("/help")
def help_it():

    return render_template('help.html')


app.run(host='127.0.0.1', port=8080, debug=True)
