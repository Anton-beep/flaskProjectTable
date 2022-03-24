from requests import get, post, delete, put
from pprint import pprint

print('ALL' + '-' * 20)
pprint(get('http://localhost:5000/api/users').json())

user_1 = get('http://localhost:5000/api/users/1').json()
user_2 = get('http://localhost:5000/api/users/2').json()

print('USER 1 AND 2' + '-' * 20)
pprint(user_1)
pprint(user_2)

print('DELETE' + '-' * 20)
pprint(delete('http://localhost:5000/api/users/1').json())
pprint(delete('http://localhost:5000/api/users/2').json())

print('POST' + '-' * 20)
pprint(post('http://localhost:5000/api/users', json=user_1['users']).json())
pprint(post('http://localhost:5000/api/users', json=user_2['users']).json())

print('ALL' + '-' * 20)
pprint(get('http://localhost:5000/api/users').json())