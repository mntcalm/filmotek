import requests, os, unittest
import logging
#import flask
from requests.auth import HTTPBasicAuth
#from filmoteka import app
#from pathlib import Path


login_data = {
'login': 'user4',
'password': 'pass4woRd'
}

session = requests.Session()

# Задаем базовый URL API
base_url = 'http://127.0.0.1:8082'
# название фильма для теста
flm_name = 'Название JustForTestOnly'
#flm_name = 'Название A'

if not os.path.exists('../log'):
    os.makedirs('../log')

logging.basicConfig(level='INFO', 
filename="../log/test_filmer.log",
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
filemode="a")



class TestResponseContainsString(unittest.TestCase):
    def setUp(self):
        self.base_url = base_url
        self.flm_name = flm_name
#        self.app = flask.app.test_client()
        self.params = {
            'ff_n': self.flm_name
        }


    def test_01_string_not_present(self):
# Проверяем, что строки нет
        response = requests.get(f'{self.base_url}/perechen', 
        params=self.params)
        try:
            self.assertNotIn(self.flm_name, response.text, 
            "Строки быть не должно")
            logging.info('Строка НЕ найдена в ответе - Ok')
        except:
            logging.error('Строка найдена, возможны последствия \
                 предыдущего проваленого теста', exc_info=True)
#            self.fail("Тест не прошел, останавливаем выполнение")
    
    def test_02_login_auth(self):
        response = session.post(f'{self.base_url}/login', data=login_data)
#        print(response.text)
        if response.ok:
            logging.info('Маршрут для авторизации сработал - Ok')
            try:
                self.assertIn('Вы успешно авторизованы', response.text, 
                "Авторизация состоялась")
                logging.info('Авторизация успешна - Ok')
            except:
                logging.error('Авторизация провалена - аварийный выход')
                self.fail("Тест не прошел, останавливаем выполнение")
        else:
            logging.error('Маршрут авторизации не сработал - аварийный выход')
            self.fail("Тест не прошел, останавливаем выполнение")

    
    def test_03_adding(self):
        with open('test.png', 'rb') as file:
            add_data = {
            'f_name': self.flm_name,
            'f_desc': 'Описание тестового элемента',
            'rel_date': '1871-01-02',
            'janr': '1',
            'regis': '1'
            }
            files = {
            'fileToUpload': ('test.png', file, 'image/png')
            }
            response = session.post(f'{self.base_url}/adding', data=add_data, 
            files=files)
        print(response.text)

    
    def te_st_04_response_contains_string(self):
        response = requests.get(f'{self.base_url}/perechen', params=self.params)
        try:
            self.assertIn(self.flm_name, response.text, 
            "Строка должна быть")
            logging.info('Строка найдена в ответе - Ok')
            
        except AssertionError:
            logging.error('Строка не найдена в ответе', exc_info=True)
#            self.fail("Тест не прошел, останавливаем выполнение")

    def test_05_adding_unit(self):
        print('----')
        pass
            
if __name__ == '__main__':
    unittest.main()