import configparser
import os.path
import base64
from PIL import Image
import io
from io import BytesIO
import psycopg2 as ps
from flask import Flask, render_template, redirect, url_for, send_file, request


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
#    # Получаем значениz параметрjd font из секции db
        db_driver = config.get("db", "driver")
        db_name = config.get("db", "name")
        db_host = config.get("db", "host")
        db_port = config.get("db", "port")
        db_l = config.get("db", "login")
        db_p = config.get("db", "password")
        return Db_details(db_driver, db_name, db_host, db_port, db_l, db_p)
    except:
        return "Failed to read DB config"


db_details = parse_config()
if str(db_details.driver) == 'PostgreSQL':
    connection = ps.connect(
         host=str(db_details.host),
         user=str(db_details.login),
         password=str(db_details.password),
         database=str(db_details.name),
         port=int(db_details.port)
        )

cursor = connection.cursor()
app = Flask(__name__)


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/perechen", methods=["GET", 'POST'])
def perechen():
  if request.method == "GET":
    f_filtr_name = str(request.args.get("ff_n"))
#    print(f_filtr_name)
    class Prch(object):
        def __init__(
            self,
            id,
            film_name,
            janre_id,
            release_date,
            rejiser,
            descript,
            rate,
            user,
            poster):
                self.id = id
                self.film_name = film_name
                self.janre_id = janre_id
                self.release_date = release_date
                self.rejiser = rejiser
                self.descript = descript
                self.rate = rate
                self.user = user
                self.poster = poster
#    #cursor.close()
#    #connection.close()
#    print(f_filtr_name)

    if f_filtr_name != None:
        f_filtr_name = " WHERE f.film_name = \'" + f_filtr_name + "\'"


    request_to_read_data = '''SELECT f.id, film_name, j.janr,
    release_date, r.rejiser, descript, rate, u.user_name, f.poster FROM
    films f INNER JOIN rejis r ON f.rejiser_id = r.Id INNER
    JOIN users u ON f.user_id=u.id INNER JOIN janre j on 
    j.Id=f.janre_id''' + f_filtr_name + ' ORDER BY f.film_name;'
# + filtr_perechen 

    cursor.execute(request_to_read_data)

    data = cursor.fetchall()
#    #print(len(data))
    prch_th = []
    for row in data:
        a = Prch(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        prch_th.append(a)
    return render_template('perechen.html', prch_th=prch_th)
  elif request.method == "POST":
    f_n = request.form["f_name"]
    
    return redirect(url_for('perechen', ff_n=f_n))


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
