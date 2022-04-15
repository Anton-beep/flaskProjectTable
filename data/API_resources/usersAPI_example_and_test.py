import requests
from pprint import pprint

API_KEY_JSON = {
    "api-key": "admin"
}

# GET all data about users
print('GET ALL USERS' + '_' * 50)

pprint(requests.get('http://localhost:5000/api/users', json=API_KEY_JSON).json())

# GET one user
user = 1
print(f'GET USER #{user}' + '_' * 50)

pprint(requests.get(f'http://localhost:5000/api/users/{user}', json=API_KEY_JSON).json())

# POST new user
print('POST NEW USER' + '_' * 50)

print('NEW USER DATA')
NEW_USER = {
    "api-key": "admin",
    "id": 900,
    "access_level": 1,
    "email": "bib@bob.com",
    "grade": "",
    "hashed_password": "pbkdf2:sha256:260000$wauhgyUAyrvanXl7$ce5a652e6eea4b58fd6af8c05bbee4864f6e555de54142db20ea8d96fe7e2b04",
    "image": "/static/img/default.png",
    "modified_date": "2022-03-27 21:46:37",
    "name": "bib",
    "patronymic": "bib",
    "surname": "bib",
    "token": "new_token"
}
pprint(NEW_USER)

print('POST')
pprint(requests.post('http://localhost:5000/api/users', json=NEW_USER).json())

# GET NEW USER
print('GET NEW USER' + '_' * 50)

pprint(requests.get('http://localhost:5000/api/users/900', json=API_KEY_JSON).json())

# DELETE NEW USER
print('DELETE NEW USER' + '_' * 50)

pprint(requests.delete('http://localhost:5000/api/users/900', json=API_KEY_JSON).json())

# CHECK RESULTS
print('GET NEW USER' + '_' * 50)

pprint(requests.get('http://localhost:5000/api/users/900', json=API_KEY_JSON).json())

print('GET ALL USERS' + '_' * 50)

pprint(requests.get('http://localhost:5000/api/users', json=API_KEY_JSON).json())