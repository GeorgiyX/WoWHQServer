import datetime as datetime

from Core import db
from Core.models import GameClass, GameSpec, Talants, WowToken, AssistInfo, User, Token
from Core.Utilites import AccessToken, Utilites
import copy

def SaveClasses():
    token = AccessToken.getToken()["access_token"]
    api = "https://eu.api.blizzard.com/wow/data/character/classes?locale={}&access_token={}"
    langs = ["ru_RU", "en_GB", "de_DE", "fr_FR", "es_ES"]
    exisist_cls = GameClass.query.all()
    data = {}
    if len(exisist_cls) == 0:
        for lang in langs:
            data[lang] = Utilites.getJSON(api.format(lang, token))["classes"]
        for i in range(0, len(data["ru_RU"])):
            game_cls  = GameClass(name_ru = data[langs[0]][i]["name"],
                 name_en = data[langs[1]][i]["name"],
                 name_de = data[langs[2]][i]["name"],
                 name_fr = data[langs[3]][i]["name"],
                 name_es = data[langs[4]][i]["name"],
                 power_type = data[langs[1]][i]["powerType"])
            print(game_cls)
            db.session.add(game_cls)
            db.session.commit()

def SaveSpecs():
    token = AccessToken.getToken()["access_token"]
    api = "https://eu.api.blizzard.com/wow/data/talents?locale={}&access_token={}"
    langs = ["ru_RU", "en_GB", "de_DE", "fr_FR", "es_ES"]
    data = {}
    exisist_spec = GameSpec.query.all()
    exigame_cls = GameClass.query.all()
    if len(exisist_spec) == 0:
        for lang in langs:
            data[lang] = Utilites.getJSON(api.format(lang, token))
        for cls in exigame_cls:
            # cls_spec=[]
            for i in range(0,len(data[langs[0]][str(str(cls.id))]["specs"])):
                game_spec = GameSpec(g_class=cls,
                                     name_ru = data[langs[0]][str(cls.id)]["specs"][i]["name"],
                                     name_en = data[langs[1]][str(cls.id)]["specs"][i]["name"],
                                     name_de = data[langs[2]][str(cls.id)]["specs"][i]["name"],
                                     name_fr = data[langs[3]][str(cls.id)]["specs"][i]["name"],
                                     name_es = data[langs[4]][str(cls.id)]["specs"][i]["name"],

                                     description_ru = data[langs[0]][str(cls.id)]["specs"][i]["description"],
                                     description_en = data[langs[1]][str(cls.id)]["specs"][i]["description"],
                                     description_de = data[langs[2]][str(cls.id)]["specs"][i]["description"],
                                     description_fr = data[langs[3]][str(cls.id)]["specs"][i]["description"],
                                     description_es = data[langs[4]][str(cls.id)]["specs"][i]["description"],

                                     role = data[langs[1]][str(cls.id)]["specs"][i]["role"],
                                     icon = data[langs[1]][str(cls.id)]["specs"][i]["icon"],
                                     backgroundImage = data[langs[1]][str(cls.id)]["specs"][i]["backgroundImage"],
                                     order = data[langs[1]][str(cls.id)]["specs"][i]["order"])
                print(game_spec)
                # cls_spec.append(copy.deepcopy(game_spec))
                db.session.add(game_spec)
                db.session.commit()
            #
            # for i in range(0,len(data[langs[0]][str(cls.id)]["talents"])): #для всех тиров
            #     for n in range(0, len(data[langs[0]][str(cls.id)]["talents"][i])):#для всех ячеек в тире
            #         for m in range(0, len(data[langs[0]][str(cls.id)]["talents"][i][n])): #для талантов (3 в каждой  ячейке, содержат адрес, спелл, и спек)
            #             cooldown=powerCost=game_range=spec = None
            #             for spec in cls_spec: #находим объект "спек" для данного таланта (т.к. в json они перемешаны)
            #                 if int(spec.order) == int(data[langs[0]][str(cls.id)]["talents"][i][n][m]["spec"]["order"]):
            #                     break
            #
            #             if "range" in data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]:
            #                 game_range = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["range"]
            #             if "powerCost" in data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]:
            #                 powerCost = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["powerCost"]
            #             if "cooldown" in data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]:
            #                 cooldown = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["cooldown"]
            #
            #             talent = Talants(
            #                             g_spec = spec,
            #                             tier=data[langs[1]][str(cls.id)]["talents"][i][n][m]["tier"],
            #                             column = data[langs[1]][str(cls.id)]["talents"][i][n][m]["column"],
            #                             spell_id = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["id"],
            #                             castTime = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["castTime"],
            #                             range = game_range,
            #                             powerCost = powerCost,
            #                             cooldown = cooldown,
            #
            #                             name_ru = data[langs[0]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
            #                             name_en = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
            #                             name_de = data[langs[2]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
            #                             name_fr = data[langs[3]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
            #                             name_es = data[langs[4]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
            #
            #                             description_ru = data[langs[0]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
            #                             description_en = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
            #                             description_de = data[langs[2]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
            #                             description_fr = data[langs[3]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
            #                             description_es = data[langs[4]][str(cls.id)]["talents"][i][n][m]["spell"]["description"])
            #             print(talent)
            #             db.session.add(talent)
            #             db.session.commit()

def SaveTalants():
    token = AccessToken.getToken()["access_token"]
    api = "https://eu.api.blizzard.com/wow/data/talents?locale={}&access_token={}"
    langs = ["ru_RU", "en_GB", "de_DE", "fr_FR", "es_ES"]
    data = {}
    exisist_talants = Talants.query.all()
    exigame_cls = GameClass.query.all()
    if len(exisist_talants) == 0:
        for lang in langs:
            data[lang] = Utilites.getJSON(api.format(lang, token))
        for cls in exigame_cls:
            from sqlalchemy.orm import raiseload, joinedload
            cls_spec= GameSpec.query.filter(GameSpec.g_class == cls).options(joinedload(GameSpec.g_class)).all()

            for i in range(0,len(data[langs[0]][str(cls.id)]["talents"])): #для всех тиров
                for n in range(0, len(data[langs[0]][str(cls.id)]["talents"][i])):#для всех ячеек в тире
                    for m in range(0, len(data[langs[0]][str(cls.id)]["talents"][i][n])): #для талантов (3 в каждой  ячейке, содержат адрес, спелл, и спек)

                        def addTalant():
                            cooldown = powerCost = game_range = None
                            if "range" in data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]:
                                game_range = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["range"]
                            if "powerCost" in data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]:
                                powerCost = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["powerCost"]
                            if "cooldown" in data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]:
                                cooldown = data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["cooldown"]

                            talent = Talants(
                                g_spec=spec,
                                tier=data[langs[1]][str(cls.id)]["talents"][i][n][m]["tier"],
                                column=data[langs[1]][str(cls.id)]["talents"][i][n][m]["column"],
                                spell_id=data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["id"],
                                castTime=data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["castTime"],
                                range=game_range,
                                powerCost=powerCost,
                                cooldown=cooldown,

                                name_ru=data[langs[0]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
                                name_en=data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
                                name_de=data[langs[2]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
                                name_fr=data[langs[3]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],
                                name_es=data[langs[4]][str(cls.id)]["talents"][i][n][m]["spell"]["name"],

                                description_ru=data[langs[0]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
                                description_en=data[langs[1]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
                                description_de=data[langs[2]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
                                description_fr=data[langs[3]][str(cls.id)]["talents"][i][n][m]["spell"]["description"],
                                description_es=data[langs[4]][str(cls.id)]["talents"][i][n][m]["spell"]["description"])
                            print(talent)
                            t = db.session.merge(talent)
                            db.session.add(t)
                            db.session.commit()


                        if "spec" not in data[langs[0]][str(cls.id)]["talents"][i][n][m]: #если талант общий для для нескольких спеков то определяем для каких и дублируем талант для каждого спека (хотя это не удовлетворяет реляционной модели)
                            specs_for_one_talants = GameSpec.query.filter(GameSpec.g_class == cls).options(joinedload(GameSpec.g_class)).all()
                            for k in range(0, len(data[langs[0]][str(cls.id)]["talents"][i][n])): #исключаем из списка талантов те что явно указаны
                                if "spec" in data[langs[0]][str(cls.id)]["talents"][i][n][k]:
                                    for spec_to_remove in specs_for_one_talants:
                                        if int(spec_to_remove.order) == int(data[langs[0]][str(cls.id)]["talents"][i][n][k]["spec"]["order"]):
                                            specs_for_one_talants.remove(spec_to_remove)

                            for spec in specs_for_one_talants:
                                addTalant()

                        else:
                            spec = None
                            for spec in cls_spec: #находим объект "спек" для данного таланта (т.к. в json они перемешаны)
                                if int(spec.order) == int(data[langs[0]][str(cls.id)]["talents"][i][n][m]["spec"]["order"]):
                                    break
                            addTalant()

def addWoWToken():
    regions = ["us", "eu", "kr", "tw", "cn"]
    exists_wowtoken = WowToken.query.all()
    if len(exists_wowtoken) == 0:
        for region in regions:
            t = WowToken(region=region,
                         current_price_blizzard_api=0,
                         current_price_wowtokenprices_api =0,
                         timestamp_blizzard_api = datetime.datetime.utcfromtimestamp(1101168000),
                         timestamp_wowtokenprices_api = datetime.datetime.utcfromtimestamp(1101168000),
                         last_change = 0,
                         one_day_low =0,
                         one_day_high =0,
                         seven_day_high =0,
                         seven_day_low =0,
                         month_low =0,
                         month_high =0)
            db.session.add(t)
            db.session.commit()


def addUser(login, password):
    u = User(login, password)
    db.session.add(u)
    db.session.commit()

def addZeroLastItem():
    ai = AssistInfo("LastItem", 0)
    db.session.add(ai)
    db.session.commit()

def addClient(client_id, client_secret):
    t = Token(token="nothiiing", expires=datetime.datetime.now(), client_id = client_id, client_secret = client_secret)
    db.session.add(t)
    db.commit()