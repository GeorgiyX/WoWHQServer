import requests


def gethtml():
    url = "https://data.wowtoken.info/wowtoken.json"
    request = requests.get(url=url);
    with open("text.json", "w") as file:
        file.write(request.text)