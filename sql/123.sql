\COPY films (id, film_name, janre_id, release_date, rejiser_id, descript, rate, poster, user_id) FROM '/home/calltop/daa_python_film/filmotek/sql/films.csv' WITH (FORMAT csv,header false, delimiter ',');
