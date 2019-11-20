import pytest
from flask import g, session
from application import mongo

# def test_register(client, app):
#     # test that viewing the page renders without template errors
#     assert client.get('/signup').status_code == 405
#
#     # test that successful registration redirects to the login page
#     response = client.post(
#         '/signup', data={'name': 'a', 'F_pwd': 'a','S_pwd': 'a'}
#     )
#     assert 'http://localhost/signup' == response.headers['Location']
#
#     # test that the user was inserted into the database
#     with app.app_context():
#         assert mongo.db.user.find_one({'name':'a'}) is not None


@pytest.mark.parametrize(('name', 'F_pwd', 'S_pwd','message'), (
    ('', '','', b'Post can not be empty!'),
    ('a', 'b','v', b'Inconsistent passwords!'),
    ('test', 'test','test', b'User name is existed!')

))


def test_register_validate_input(client, name, F_pwd,S_pwd, message):
    response = client.post(
        '/signup',
        data={'name': name, 'F_pwd': F_pwd,'S_pwd':S_pwd}
    )
    assert message in response.data



@pytest.mark.parametrize(('name', 'pwd', 'message'), (
    ('sjfdks', 'test', b'Invalid username!'),
    ('test', 'a', b'Invalid password!'),
    ('yhma', 'test',b'Login successfully!')
))
def test_login_validate_input(client,name,pwd, message):
    response = client.post(
        '/login',
        data={'name': name, 'pwd':pwd}
    )
    assert message in response.data


def test_logout(client):
    message = b'You have logout !'
    response = client.get('/logout')
    assert message in response.data


