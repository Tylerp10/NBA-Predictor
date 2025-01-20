import requests

def import_name(name):
    url = "https://api-nba-v1.p.rapidapi.com/players"

    querystring = {"search": {name}}

    headers = {
        "x-rapidapi-key": "b7ff177dc6msh0354e8083416a13p185307jsndfdc4d061346",
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())

import_name('james')