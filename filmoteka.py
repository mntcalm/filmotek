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
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import hashlib
from werkzeug.utils import secure_filename
import os
import random
import string
from models import (Db_details,
   UserLogin,
   Prch,
   Janry,
   Regisery)
#import models
#from UserLogin import UserLogin




def parse_config():
    # Создаем объект ConfigParser, файл filmotek.conf рядом
    config = configparser.ConfigParser()
    try:
        program_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(program_dir, "filmotek.conf")
        config.read(config_path)
#    # Получаем значения параметров font из секции db
        db_driver = config.get("db", "driver")
        db_name = config.get("db", "name")
        db_host = config.get("db", "host")
        db_port = config.get("db", "port")
        db_l = config.get("db", "login")
        db_p = config.get("db", "password")
        return Db_details(db_driver, db_name, db_host, db_port, db_l, db_p)
    except:
        return "Failed to read DB config"

def generate_random_filename():
    # Генерация случайной строки из 8 символов
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    # Добавление расширения к имени файла
    return random_string


def get_janre_list(cursr):
#   формирование таблицы жанров и их ID
    j_l = [Janry('-8', '<empty>'),]        
    request_to_read_data = '''SELECT id, janr from janre;'''
    cursr.execute(request_to_read_data)
    data = cursr.fetchall()
    for row in data:
        a = Janry(row[0], row[1])
        j_l.append(a)
    return j_l

def get_regis_list(cursr):
#   формирование таблицы Режиссеров и их ID   
    r_l = [Regisery('-8', '<empty>'),]        
    request_to_read_data = '''SELECT id, rejiser from rejis;'''
    cursr.execute(request_to_read_data)
    data = cursr.fetchall()
    for row in data:
        a = Regisery(row[0], row[1])
        r_l.append(a)
    return r_l

db_details = parse_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxhH345j4K4iuopO'
app.config['UPLOAD_FOLDER'] = 'static/img/posters'
app.config['MAX_CONTENT_LENGTH'] = 1.5 * 1024 * 1024  # 1.5 MB limit
ALLOWED_EXTENSIONS = {'png', 'gif', 'bmp', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


if str(db_details.driver) == 'postgresql':
    connection = ps.connect(
         host=str(db_details.host),
         user=str(db_details.login),
         password=str(db_details.password),
         database=str(db_details.name),
         port=int(db_details.port)
        )
    


@app.route("/")
def index():
    mssg = str(request.args.get("f_msg", "Привет-привет!"))
    return render_template('index.html', mssg=mssg, c_u=current_user)


@app.route("/perechen", methods=["GET", 'POST'])
def perechen():
  if request.method == "GET":
    f_filtr_name = str(request.args.get("ff_n", ""))
    j_filtr_id = str(request.args.get("jj_id", "-8"))
    r_filtr_id = str(request.args.get("rr_id", "-8"))
    god_ot = str(request.args.get("gg_ot", ""))
    god_do = str(request.args.get("gg_do", ""))
    sortirovka = str(request.args.get("ww_sort", ""))
    paginacia = int(request.args.get("nn_pagin", 10))
    page = int(request.args.get("pp_page", 1))
    offset = (page - 1) * paginacia


# обработка данных формы: фильтруем по каким полям        
    if f_filtr_name == 'None' or len(f_filtr_name) <=2:
        db_f_filtr_name = ''
    else:
        db_f_filtr_name = " AND f.film_name ILIKE '%" + f_filtr_name + "%\'"
    
    if j_filtr_id == 'None' or str(j_filtr_id) == '-8':
        db_j_filtr_id = ''
    else:
        db_j_filtr_id = " AND f.janre_id = '" + str(j_filtr_id) + "'"

# фильтр по режиссерам - по образу жанрового
    if r_filtr_id == 'None' or str(r_filtr_id) == '-8':
        db_r_filtr_id = ''
    else:
        db_r_filtr_id = " AND f.rejiser_id = '" + str(r_filtr_id) + "'"
 

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


# собственно сам запрос
    request_to_read_data = '''SELECT f.id, film_name, j.janr,
    release_date, r.rejiser, descript, rate, u.user_name, f.poster FROM
    films f INNER JOIN rejis r ON f.rejiser_id = r.Id INNER
    JOIN users u ON f.user_id=u.id INNER JOIN janre j on
    j.Id=f.janre_id WHERE TRUE''' + db_f_filtr_name + db_j_filtr_id \
    + god_filtr + db_r_filtr_id + db_sortirovka + lim_step

        

# Запрос пересчитывающий вхождения (и чтоб оценить кол-во страниц в пагинации)
    r_n = '''SELECT COUNT(*) FROM
    films f INNER JOIN rejis r ON f.rejiser_id = r.Id INNER
    JOIN users u ON f.user_id=u.id INNER JOIN janre j on 
    j.Id=f.janre_id WHERE TRUE''' + db_f_filtr_name \
    + db_j_filtr_id + god_filtr + db_r_filtr_id + ';'
    
    
    cursor = connection.cursor()

#   формирование таблиц жанров и режиссеров   
 
    janre_list = get_janre_list(cursor)
    regis_list = get_regis_list(cursor)

# запрашиваем, пересчитываем
    cursor.execute(r_n)
    entryes = cursor.fetchall()
    n_pages = ceil(entryes[0][0] / paginacia)
    n_entr = entryes[0][0]

# запрашиваем, запоминаем
    cursor.execute(request_to_read_data)

    data = cursor.fetchall()
#    #print(len(data))
    cursor.close()

# упаковываем в массив структуры(объекты класса извлеченного из БД)
    prch_th = []
    for row in data:
        a = Prch(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        prch_th.append(a)
    
    

#    if current_user:
#        cur_user = str(current_user.id)
#        cur_role = str(current_user.role_id)

    return render_template('perechen.html', prch_th=prch_th,
      janre_list=janre_list, page=page, paginacia=paginacia,
      f_filtr_name=f_filtr_name,
      j_filtr_id=j_filtr_id, god_ot=god_ot, god_do=god_do,
      sortirovka=sortirovka, offset=offset, regis_list=regis_list,
      n_pages=n_pages, n_entr=n_entr, c_u=current_user)
  elif request.method == "POST":
    f_n = request.form["f_name"]
    r_id = request.form["regis"]
    j_id = request.form["janr"]
    g_ot = request.form["god_ot"]
    g_do = request.form["god_do"]
    w_sort = request.form["sortr"]
    n_pagin = request.form["pagin"]
    return redirect(url_for('perechen', ff_n=f_n, jj_id=j_id, rr_id=r_id, gg_ot=g_ot,
    gg_do=g_do, ww_sort=w_sort, nn_pagin=n_pagin, pp_page=1))


@app.route("/addingsql", methods=["GET"])
@login_required
def addingsql():
    f_name = str(request.args.get("f_n"))
    f_desc = str(request.args.get("f_d"))
    rel_dat = str(request.args.get("r_d"))
    f_upl = str(request.args.get("f_u"))
    f_jnr = str(request.args.get("f_j"))
    f_rej = str(request.args.get("f_r"))
    c_uid = str(current_user.id)

    cursor = connection.cursor()
    ins_req = '''INSERT INTO films (film_name, janre_id, rejiser_id,
    release_date, descript, rate, user_id) VALUES (''' + "'" + f_name +\
    "', " + f_jnr + ", " + f_rej + ", '" +  rel_dat + "', '" +\
    f_desc + "', 5.5, " + c_uid + ") RETURNING id;"
    connection.commit()
    
    cursor.execute(ins_req)
    db_rep = cursor.fetchall()
    post_id = db_rep[0][0]
    print(post_id)
    
    
    old_f = app.config['UPLOAD_FOLDER'] + '/' + f_upl
    new_f = app.config['UPLOAD_FOLDER'] + '/perech' +\
    str(post_id) + ".png"
    upd_req = "UPDATE films SET poster = '" +\
    new_f + "' WHERE id = '" + str(post_id) + "';"
    print(upd_req)
    cursor.execute(upd_req)
    connection.commit()
    cursor.close()
    
    os.rename(old_f, new_f)
    return redirect(url_for('perechen', ff_n=f_name, page=1))

@app.route("/adding", methods=["GET", "POST"])
@login_required
def adding():
    if request.method == "GET":
        cursor = connection.cursor()
        janre_list = get_janre_list(cursor)
        regis_list = get_regis_list(cursor)
        cursor.close()
        return render_template('adding.html',
        janre_list=janre_list, regis_list=regis_list)
       


    elif request.method == "POST":
        f_n = request.form["f_name"]
        f_d = request.form["f_desc"]
        r_d = request.form["rel_date"]
#        u_file = request.form["fileToUpload"]
        f_j = request.form["janr"]
        f_r = request.form["regis"]
        
        file = request.files['fileToUpload']
        u_file = file.filename
        filename = secure_filename(file.filename)
        new_filename = generate_random_filename() + '.' + \
            filename.rsplit('.', 1)[1].lower()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)) 
        
        
        return redirect(url_for('addingsql', f_n=f_n, f_d=f_d, r_d=r_d,
        f_u=new_filename,
        f_j=f_j, f_r=f_r))


@app.route("/editing")
@login_required
def editing():

    return render_template('editing.html', c_u=current_user)


@app.route("/login", methods=["GET", 'POST'])
def login():
    if request.method == "GET":
       return render_template('login.html', c_u=current_user)
    elif request.method == "POST":
      f_login = request.form["login"]
      f_passwd = request.form["password"]
      hash_passwd = hashlib.sha256(f_passwd.encode()).hexdigest()
      

# формируем запрос о таком пользователе       
      request_to_read_user='''SELECT u.id, u.user_name, 
      u.passwd, u.role_id, t.u_type, u.locked FROM \
      users u INNER JOIN user_type t ON u.role_id = t.id WHERE user_name = \'''' \
      + str(f_login) + '\';'
      
      
      cursor = connection.cursor()
      cursor.execute(request_to_read_user)
      user_details = cursor.fetchall()
      cursor.close()

      u_d = []
      for row in user_details:
          d_id = row[0]
          d_login = row[1]
          d_passwd = row[2]
          d_role = row[3]
          d_locked = row[5]
          u_d.append("+")
        

        
      if  len(u_d) == 1: # пользователь существует
          if str(d_passwd) == str(hash_passwd): # пароль правильный
              msg = "Вы успешно авторизованы как " + str(d_login)
              userlogin = UserLogin(d_id, d_login, d_role, d_locked)
              login_user(userlogin)
              


          else:
              msg = "Неправильный пароль"     
      else:
          msg = "Нет такого пользователя"
      
      
      return redirect(url_for('index', f_msg=msg))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/user_edit")
def user_edit():

    return render_template('user_edit.html', c_u=current_user)


@app.route("/help")
def help_it():

    return render_template('help.html', c_u=current_user)


@login_manager.user_loader
def load_user(userid):
    request_to_read_user='''SELECT u.id, u.user_name, 
      u.passwd, u.role_id, t.u_type, u.locked FROM \
      users u INNER JOIN user_type t ON u.role_id = t.id WHERE u.id = \'''' \
      + str(userid) + '\';'
    cursor = connection.cursor()
    cursor.execute(request_to_read_user)
    user_details = cursor.fetchall()
    cursor.close()
    
    u_d = []
    for row in user_details:
        d_id = row[0]
        d_login = row[1]
        d_passwd = row[2]
        d_role = row[3]
        d_locked = row[5]
        u_d.append("+")
        

        
    if  len(u_d) == 1: # пользователь существует
        loaded_user = UserLogin(d_id, d_login, d_role, d_locked)
            
    return loaded_user

app.run(host='127.0.0.1', port=8080, debug=True)
