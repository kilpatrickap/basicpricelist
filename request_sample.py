import requests

# Request materials data from API
request = requests.get('https://mm-api-rz05.onrender.com')
print(request.json())
