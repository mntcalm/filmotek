# -*- coding: utf-8 -*-
import configparser
import os.path
import base64
from PIL import Image
import io
from io import BytesIO
import psycopg2 as ps
from flask import Flask, render_template, redirect, url_for, send_file, request
from math import ceil

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

app = Flask(__name__)


if str(db_details.driver) == 'PostgreSQL':
    connection = ps.connect(
         host=str(db_details.host),
         user=str(db_details.login),
         password=str(db_details.password),
         database=str(db_details.name),
         port=int(db_details.port)
        )



@app.route("/")
def index():

    return render_template('index.html')


@app.route("/perechen", methods=["GET", 'POST'])
def perechen():
  if request.method == "GET":
    f_filtr_name = str(request.args.get("ff_n", ""))
    j_filtr_id = str(request.args.get("jj_id", "-8"))
    god_ot = str(request.args.get("gg_ot", ""))
    god_do = str(request.args.get("gg_do", ""))
    sortirovka = str(request.args.get("ww_sort", ""))
    paginacia = int(request.args.get("nn_pagin", 10))
    page = int(request.args.get("pp_page", 1))
    offset = (page - 1) * paginacia
 #   print("-------------", god_ot, god_do)
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
    class Janry(object):
        def __init__(
            self,
            id,
            j_name):
                self.id = id
                self.j_name = j_name
    janre_list = [Janry('-8', '<empty>'),]        
    request_to_read_data = '''SELECT id, janr from janre;'''
    cursor = connection.cursor()
    cursor.execute(request_to_read_data)
    data = cursor.fetchall()
    for row in data:
        a = Janry(row[0], row[1])
        janre_list.append(a)
    

        
    if f_filtr_name == 'None' or len(f_filtr_name) <=2:
        db_f_filtr_name = ''
    else:
        db_f_filtr_name = " AND f.film_name ILIKE '%" + f_filtr_name + "%\'"
    
    if j_filtr_id == 'None' or str(j_filtr_id) == '-8':
        db_j_filtr_id = ''
    else:
        db_j_filtr_id = " AND f.janre_id = '" + str(j_filtr_id) + "'"
 

    if str(god_ot) == 'None' or len(str(god_ot)) <=2:
        god_filtr = ''
    else:
        god_filtr = " AND release_date BETWEEN '" + god_ot + "-01-01' AND '" + god_do + "-12-31'"

    if sortirovka == 'nosort':
        db_sortirovka = ' ORDER BY f.film_name'
    elif sortirovka == 'datev':
        db_sortirovka = ' ORDER BY f.release_date DESC'
    else:
        db_sortirovka = ' ORDER BY f.rate DESC'

    lim_step = " LIMIT " + str(paginacia) + " OFFSET " + str(paginacia * (page - 1)) + ";"


    request_to_read_data = '''SELECT f.id, film_name, j.janr,
    release_date, r.rejiser, descript, rate, u.user_name, f.poster FROM
    films f INNER JOIN rejis r ON f.rejiser_id = r.Id INNER
    JOIN users u ON f.user_id=u.id INNER JOIN janre j on
    j.Id=f.janre_id WHERE TRUE''' + db_f_filtr_name + db_j_filtr_id \
    + god_filtr + db_sortirovka + lim_step
    


    r_n = '''SELECT COUNT(*) FROM
    films f INNER JOIN rejis r ON f.rejiser_id = r.Id INNER
    JOIN users u ON f.user_id=u.id INNER JOIN janre j on 
    j.Id=f.janre_id WHERE TRUE''' + db_f_filtr_name \
    + db_j_filtr_id + god_filtr + ';'
    

    cursor.execute(r_n)
    entryes = cursor.fetchall()
    n_pages = ceil(entryes[0][0] / paginacia)
    n_entr = entryes[0][0]

    cursor.execute(request_to_read_data)

    data = cursor.fetchall()
#    #print(len(data))
    prch_th = []
    for row in data:
        a = Prch(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        prch_th.append(a)
    
    cursor.close()
    
    return render_template('perechen.html', prch_th=prch_th,
      janre_list=janre_list, page=page, paginacia=paginacia,
      f_filtr_name=f_filtr_name,
      j_filtr_id=j_filtr_id, god_ot=god_ot, god_do=god_do,
      sortirovka=sortirovka, offset=offset,
      n_pages=n_pages, n_entr=n_entr )
  elif request.method == "POST":
    f_n = request.form["f_name"]
    j_id = request.form["janr"]
    g_ot = request.form["god_ot"]
    g_do = request.form["god_do"]
    w_sort = request.form["sortr"]
    n_pagin = request.form["pagin"]
    return redirect(url_for('perechen', ff_n=f_n, jj_id=j_id, gg_ot=g_ot, gg_do=g_do, ww_sort=w_sort, nn_pagin=n_pagin, pp_page=1))

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
