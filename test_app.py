import unittest
from app import app


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_correct_vector(self):
        response = self.app.post('/deposit/process', json={"date": "31.01.2021", "periods": 3, "amount": 10000, "rate":6})
        assert response.status_code == 200
        assert response.get_json() == {'31.01.2021': 10050, '28.02.2021': 10100.25, '31.03.2021': 10150.75}

    def test_wrong_date(self):
        response = self.app.post('/deposit/process', json={"date": "29.02.2021", "periods": 3, "amount": 10000, "rate":6})
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Key \'date\' error'}

    def test_wrong_schema(self):
        response = self.app.post('/deposit/process', json={"date": "31.01.2021", "amount": 10000, "rate":6})
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Missing key: \'periods\''}

    def test_wrong_method(self):
        response = self.app.get('/deposit/process')
        assert response.status_code == 405
        assert response.get_json() == {'error': 'Method not allowed!'}

    def test_page_not_found(self):
        response = self.app.post('/deposit/proes', json={"date": "31.01.2021", "amount": 10000, "rate":6})
        assert response.status_code == 404
        assert response.get_json() == {'error': 'Page not found!'}

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()