import unittest
from unittest.mock import patch
from config import SNOWFLAKE_CONNECTOR

 
conn = SNOWFLAKE_CONNECTOR

def librarian_exists(username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM librarians WHERE username = %s", (username,))
    librarian = cursor.fetchone()
    cursor.close()
    return librarian is not None


def librarian_signup(request):
    data = request.get_json()
    username = data['username']
    password = data['password']
    # Assuming librarian_exists is a global function
    if librarian_exists(username):  # Mock this function to return True or False
        return {'message': 'Librarian with this username already exists'}, 400
   
    # Mock conn object to insert data into database
    cursor = conn.cursor()
    cursor.execute("INSERT INTO librarians (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cursor.close()
    
    return {'message': 'Librarian signed up successfully'}, 200


class MockRequest:
    def get_json(self):
        return {'username': 'testuser', 'password': 'testpassword'}

class TestLibrarianSignup(unittest.TestCase):
    def test_valid_signup(self):
        # Call the function and check the response
        response = librarian_signup(MockRequest())
        self.assertEqual(response[0]['message'], 'Librarian signed up successfully')

    def test_existing_username(self):
        # Mock the librarian_exists function to return True
        def mock_librarian_exists(username):
            return True

        # Call the function and check the response
        with patch('__main__.librarian_exists', side_effect=mock_librarian_exists):
            response = librarian_signup(MockRequest())
            self.assertEqual(response[0]['message'], 'Librarian with this username already exists')
            self.assertEqual(response[1], 400)

    def test_missing_username_or_password(self):
        # Mock the request data with missing username
        class MockRequestMissingUsername:
            def get_json(self):
                return {'password': 'testpassword'}

        mock_request_missing_username = MockRequestMissingUsername()
        response = librarian_signup(mock_request_missing_username)
        self.assertEqual(response[1], 400)

        # Mock the request data with missing password
        class MockRequestMissingPassword:
            def get_json(self):
                return {'username': 'testuser'}

        mock_request_missing_password = MockRequestMissingPassword()
        response = librarian_signup(mock_request_missing_password)
        self.assertEqual(response[1], 400)

    def test_valid_signup_confirmation(self):
        # Call the function and check the response
        response = librarian_signup(MockRequest())
        self.assertEqual(response[0]['message'], 'Librarian signed up successfully')
        self.assertEqual(response[1], 200)

    def test_database_error(self):
        # Mock cursor.execute to raise an exception
        class MockCursor:
            def execute(self, *args, **kwargs):
                raise Exception('Database error')

        def mock_cursor():
            return MockCursor()

        # Call the function and check the response
        with patch('__main__.conn.cursor', side_effect=mock_cursor):
            response = librarian_signup(MockRequest())
            self.assertEqual(response[1], 500)

if __name__ == '__main__':
    unittest.main()
