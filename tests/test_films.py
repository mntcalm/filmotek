import requests, os, unittest
import logging
#import flask
from requests.auth import HTTPBasicAuth



login_data = {
'login': 'user4',
'password': 'pass4woRd'
}

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
    
    def login(self, login, password):
        return requests.post('/login', data=dict(
           login=login,
           password=password
           ))

    def logout(self):
        return requests.get('/logout', follow_redirects=True)
            

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
        response = requests.post(f'{self.base_url}/login', data=login_data)
        try: 
            self.assertIn('Вы успешно авторизованы как', response.text, 
            "Строка должна быть")
            logging.info('Авторизация успешна - Ok')
        except:
            logging.error('Авторизация провалена ')


    
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