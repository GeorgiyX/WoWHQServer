from Core import db
from Core.models import Token
from datetime import datetime
import requests

def getToken():
    token = Token.query.get(1)
    return {"access_token":token.access_token, "time" :str(token.timestamp)}

def updateToken():
    token = Token.query.get(1)
    auth = (str(token.client_id), str(token.client_secret))
    token_data = requests.post("https://eu.battle.net/oauth/token", auth = auth, data={"grant_type" :"client_credentials"}).json()
    token.access_token = token_data["access_token"]
    token.expires_in = datetime.utcfromtimestamp(int(token_data["expires_in"]))
    token.timestamp = datetime.now()
    db.session.commit()

def getClientValues():
    token = Token.query.get(1)
    return {"client_id":token.client_id, "client_secret":token.client_secret}

def updateClientValues(client_id, client_secret):
    token = Token.query.get(1)
    token.client_id = str(client_id)
    token.client_secret = str(client_secret)
    db.session.commit()
    updateToken()


