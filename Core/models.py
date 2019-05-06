from Core import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON, BIGINT
from Core.Utilites.Utilites import getJSON, Log
import copy

class User(UserMixin, db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    password_hash = db.Column(db.String(256))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return "User - {}".format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Token(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    access_token = db.Column(db.String(128), index = True, unique = True)
    expires_in = db.Column(db.DateTime)
    client_id = db.Column(db.String(128), index = True, unique = True)
    client_secret = db.Column(db.String(128), index = True, unique = True)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)

    def __init__(self, token, expires, client_id, client_secret):
        self.access_token = token
        self.expires_in = expires
        self.client_id = client_id
        self.client_secret = client_secret

    def __repr__(self):
        return str(self.access_token)

class Items(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    gameId = db.Column(db.Integer, index = True)

    description_ru = db.Column(db.String(512), index = True, unique = False)
    description_en = db.Column(db.String(512), index = False, unique = False)
    description_de = db.Column(db.String(512), index = False, unique = False)
    description_fr = db.Column(db.String(512), index = False, unique = False)

    name_ru = db.Column(db.String(128), index = True, unique = False)
    name_en = db.Column(db.String(128), index = True, unique = False)
    name_de = db.Column(db.String(128), index = True, unique = False)
    name_fr = db.Column(db.String(128), index = True, unique = False)

    icon = db.Column(db.String(128), index = True, unique = False)
    buyPrice = db.Column(db.Integer, index = True)
    itemClass = db.Column(db.Integer, index = True)
    itemSubClass = db.Column(db.Integer, index = True)
    inventoryType = db.Column(db.Integer, index = True)
    equippable = db.Column(db.Boolean, index = True)
    itemLevel = db.Column(db.Integer, index = True)
    sellPrice = db.Column(db.Integer, index = True)
    isAuctionable = db.Column(db.Boolean, index = True)
    sourceId = db.Column(db.String(64), index = True, unique = False)
    sourceType = db.Column(db.String(64), index = True, unique = False)
    nameDescription = db.Column(db.String(128), index = False, unique = False)

    aucs = db.relationship('Auctions', backref = 'item', lazy='dynamic')




    def __init__(self,gameId,description_ru,description_en,description_de,description_fr,name_ru,name_en, name_de, name_fr,icon,buyPrice,itemClass,itemSubClass,inventoryType,equippable,itemLevel,sellPrice,isAuctionable,sourceId,sourceType,nameDescription):
        self.gameId = int(gameId)

        self.description_ru = description_ru
        self.description_en = description_en
        self.description_de =description_de
        self.description_fr = description_fr

        self.name_ru = name_ru
        self.name_en = name_en
        self.name_de = name_de
        self.name_fr = name_fr

        self.icon = icon
        self.buyPrice = int(buyPrice)
        self.itemClass = int(itemClass)
        self.itemSubClass = int(itemSubClass)
        self.inventoryType = int(inventoryType)
        self.equippable = bool(equippable)
        self.itemLevel = int(itemLevel)
        self.sellPrice = int(sellPrice)
        self.isAuctionable = bool(isAuctionable)
        self.sourceId = sourceId
        self.sourceType=sourceType
        self.nameDescription = nameDescription

    def __repr__(self):
        return "Name: {}; Description: {}; Source: {};".format(self.name_ru, self.description_ru, self.sourceType)


class Servers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    bliz_id = db.Column(db.Integer)
    slug = db.Column(db.String(64), index = True, unique = False)
    region = db.Column(db.String(32), index = True, unique = False)
    name = db.Column(db.String(64), index = True, unique = False)
    name_ru = db.Column(db.String(64), index = True, unique = False)
    auc = db.Column(db.String(256), index = True, unique = False)
    timestamp = db.Column(db.DateTime, index = True)


    def __init__(self,bliz_id, slug,region, name, name_ru, auc, timestamp):
        self.bliz_id = int(bliz_id)
        self.slug = slug
        self.region = region
        self.name = name
        self.name_ru = name_ru
        self.auc = auc
        self.timestamp = timestamp

    def __repr__(self):
        return "Name: {}, Slug: {}, Region: {}".format(self.name_ru, self.slug, self.region)

servers_auctions = db.Table('servers_auctions',
                            db.Column('lot_id', db.Integer, db.ForeignKey('auctions.id', ondelete='CASCADE')),
                            db.Column('serv_id', db.Integer, db.ForeignKey('servers.id')))


class SavePetAndItem():
    '''Класс объявляен в моделях, для избежания кругового импорта.'''

    def saveItem(self, id, token, is_run_in_model=False, is_must_add_new=True):
        '''Два ключевых аргумента нужны для использования кода в модели аукциона (при сохранении предмета - лота)'''
        lang = ["ru_RU", "en_GB", "de_DE", "fr_FR"]
        apiLink = "https://eu.api.blizzard.com/wow/item/{}?locale={}&access_token={}"
        item = Items.query.filter(Items.gameId == int(id)).first()  # type: Items

        if item is not None and is_run_in_model is True:
            return item
        if item is None and is_run_in_model is True and is_must_add_new is False:
            return None
        data = getJSON(apiLink.format(id, lang[0], token))

        if data is not False:
            item_local = {"ru_RU": {"description": data["description"], "name": data["name"]}}
            for language in lang[1:4]:
                data = getJSON(apiLink.format(id, language, token))
                item_local[language] = {"description": data["description"], "name": data["name"]}

            if "icon" not in data:
                data["icon"] = "no_icon"

            if item is None:
                item = Items(gameId=data["id"], description_ru=item_local["ru_RU"]["description"],
                             description_en=item_local["en_GB"]["description"],
                             description_de=item_local["de_DE"]["description"],
                             description_fr=item_local["fr_FR"]["description"],
                             name_ru=item_local["ru_RU"]["name"], name_en=item_local["en_GB"]["name"],
                             name_de=item_local["de_DE"]["name"],
                             name_fr=item_local["fr_FR"]["name"],
                             icon=data["icon"], buyPrice=data["buyPrice"], itemClass=data["itemClass"],
                             itemSubClass=data["itemSubClass"], inventoryType=data["inventoryType"],
                             equippable=data["equippable"], itemLevel=data["itemLevel"], sellPrice=data["sellPrice"],
                             isAuctionable=data["isAuctionable"], sourceId=data["itemSource"]["sourceId"],
                             sourceType=data["itemSource"]["sourceType"], nameDescription=data["nameDescription"])

                if is_run_in_model and is_must_add_new:
                    print("Новый (при сохранении лота): {}".format(item))
                    import copy
                    item_copy = copy.deepcopy(item)
                    db.session.add(item)
                    db.session.commit()
                    return item_copy
                print("Новый: {}".format(item))
                db.session.add(item)
                db.session.commit()
            else:
                item.gameId = data["id"];
                item.description_ru = item_local["ru_RU"]["description"];
                item.description_en = item_local["en_GB"]["description"];
                item.description_de = item_local["de_DE"]["description"];
                item.description_fr = item_local["fr_FR"]["description"];
                item.name_ru = item_local["ru_RU"]["name"];
                item.name_en = item_local["en_GB"]["name"];
                item.name_de = item_local["de_DE"]["name"];
                item.name_fr = item_local["fr_FR"]["name"];
                item.icon = data["icon"];
                item.buyPrice = data["buyPrice"];
                item.itemClass = data["itemClass"];
                item.itemSubClass = data["itemSubClass"];
                item.inventoryType = data["inventoryType"],
                item.equippable = data["equippable"];
                item.itemLevel = data["itemLevel"];
                item.sellPrice = data["sellPrice"];
                item.isAuctionable = data["isAuctionable"];
                item.sourceId = data["itemSource"]["sourceId"];
                item.sourceType = data["itemSource"]["sourceType"];
                item.nameDescription = data["nameDescription"]
                print("Обновленный: {}".format(item))
                db.session.commit()

    def savePet(self, pet, token, is_run_in_model=False, is_must_add_new=True):
        speciesApi = "https://eu.api.blizzard.com/wow/pet/species/{}?locale={}&access_token={}"
        langs = ["ru_RU", "en_GB", "de_DE", "fr_FR", "es_ES"]
        lang_data = {}
        abilities_en = []
        pet_from_db = Pets.query.filter(Pets.speciesId == str(pet["stats"]["speciesId"])).first()  # type: Pets
        if pet_from_db is not None and is_run_in_model is True:
            return pet_from_db
        if pet_from_db is None and is_run_in_model is True and is_must_add_new is False:
            return None

        for lang in langs:
            data = getJSON(speciesApi.format(pet["stats"]["speciesId"], lang, token))
            lang_data[lang] = {"description": data["description"], "name": data["name"], "source": data["source"]}
            if lang == "en_GB":
                abilities_en = data["abilities"]
        if pet_from_db is None:
            pet_from_db = Pets(canBattle=pet["canBattle"], creatureId=pet["creatureId"],
                               name_ru=lang_data["ru_RU"]["name"],
                               name_en=lang_data["en_GB"]["name"], name_de=lang_data["de_DE"]["name"],
                               name_fr=lang_data["fr_FR"]["name"],
                               name_es=lang_data["es_ES"]["name"], description_ru=lang_data["ru_RU"]["description"],
                               description_en=lang_data["en_GB"]["description"],
                               description_de=lang_data["de_DE"]["description"],
                               description_fr=lang_data["fr_FR"]["description"],
                               description_es=lang_data["es_ES"]["description"], source_ru=lang_data["ru_RU"]["source"],
                               source_en=lang_data["en_GB"]["source"], source_de=lang_data["de_DE"]["source"],
                               source_fr=lang_data["fr_FR"]["source"],
                               source_es=lang_data["es_ES"]["source"], abilities=abilities_en, family=pet["family"],
                               icon=pet["icon"], speciesId=pet["stats"]["speciesId"],
                               qualityId=pet["qualityId"], breedId=pet["stats"]["breedId"],
                               petQualityId=pet["stats"]["petQualityId"],
                               level=pet["stats"]["level"], health=pet["stats"]["health"], power=pet["stats"]["power"],
                               speed=pet["stats"]["speed"],
                               strongAgainst=pet["strongAgainst"][0], weakAgainst=pet["weakAgainst"][0],
                               typeId=pet["typeId"])
            if is_run_in_model and is_must_add_new:
                print("Новый пет (при сохранении лота): {}".format(pet_from_db))
                import copy
                pet_from_db_copy = copy.deepcopy(pet_from_db)
                db.session.add(pet_from_db)
                db.session.commit()
                return pet_from_db_copy
            print("New пет: {}".format(pet_from_db))
            db.session.add(pet_from_db)
            db.session.commit()
        else:
            pet_from_db.canBattle = pet["canBattle"]
            pet_from_db.creatureId = pet["creatureId"]
            pet_from_db.name_ru = lang_data["ru_RU"]["name"]
            pet_from_db.name_en = lang_data["en_GB"]["name"]
            pet_from_db.name_de = lang_data["de_DE"]["name"]
            pet_from_db.name_fr = lang_data["fr_FR"]["name"]
            pet_from_db.name_es = lang_data["es_ES"]["name"]
            pet_from_db.description_ru = lang_data["ru_RU"]["description"]
            pet_from_db.description_en = lang_data["en_GB"]["description"]
            pet_from_db.description_de = lang_data["de_DE"]["description"]
            pet_from_db.description_fr = lang_data["fr_FR"]["description"]
            pet_from_db.description_es = lang_data["es_ES"]["description"]
            pet_from_db.source_ru = lang_data["ru_RU"]["source"]
            pet_from_db.source_en = lang_data["en_GB"]["source"]
            pet_from_db.source_de = lang_data["de_DE"]["source"]
            pet_from_db.source_fr = lang_data["fr_FR"]["source"]
            pet_from_db.source_es = lang_data["es_ES"]["source"]
            pet_from_db.abilities = abilities_en
            pet_from_db.family = pet["family"]
            pet_from_db.icon = pet["icon"]
            pet_from_db.speciesId = pet["stats"]["speciesId"]
            pet_from_db.qualityId = pet["qualityId"]
            pet_from_db.breedId = pet["stats"]["breedId"]
            pet_from_db.petQualityId = pet["stats"]["petQualityId"]
            pet_from_db.level = pet["stats"]["level"]
            pet_from_db.health = pet["stats"]["health"]
            pet_from_db.power = pet["stats"]["power"]
            pet_from_db.speed = pet["stats"]["speed"]
            pet_from_db.strongAgainst = pet["strongAgainst"][0]
            pet_from_db.weakAgainst = pet["weakAgainst"][0]
            pet_from_db.typeId = pet["typeId"]
            print("Updated: {}".format(pet_from_db))
            db.session.commit()


class Auctions(db.Model, SavePetAndItem):
    id = db.Column(db.Integer, primary_key = True)
    auc = db.Column(db.Integer)

    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable = True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable = True)
    servers = db.relationship('Servers', secondary = servers_auctions, backref = 'aucs')

    timestamp = db.Column(db.DateTime,index = True)
    owner = db.Column(db.String(64), index = True, unique = False)
    ownerRealm = db.Column(db.String(64), index = True, unique = False)
    bid = db.Column(BIGINT, index = True)
    buyout = db.Column(BIGINT, index = True)
    quantity = db.Column(db.Integer, index = True)
    timeLeft = db.Column(db.String(64), index = True, unique = False)
    rand = db.Column(db.String(128), unique = False)
    seed = db.Column(db.String(128), unique = False)
    context = db.Column(db.Integer, index = True)
    bonusLists = db.Column(JSON,nullable = True)
    modifiers = db.Column(JSON,nullable = True)
    petBreedId = db.Column(db.Integer, index = True,nullable = True)
    petLevel = db.Column(db.Integer, index = True,nullable = True)
    petQualityId = db.Column(db.Integer, index = True,nullable = True)

    def __init__(self, auc, itemId,servers, timestamp,owner,ownerRealm,bid,
                 buyout,quantity,timeLeft,rand,seed,context, token,
                 bonusLists = None,modifiers = None,petBreedId = None,petLevel = None,  speciesId = None, is_must_add_new = True):
        self.auc = int(auc)
        self.timestamp = timestamp
        self.owner = owner
        self.ownerRealm = ownerRealm
        self.bid = int(bid)
        self.buyout = int(buyout)
        self.quantity = int(quantity)
        self.timeLeft = timeLeft
        self.rand = rand
        self.seed = seed
        self.context = int(context)
        self.bonusLists = bonusLists
        self.modifiers = modifiers

        if petBreedId is None:
            self.petBreedId = petBreedId
        else:
            self.petBreedId = int(petBreedId)
        if petLevel is None:
            self.petLevel = petLevel
        else:
            self.petLevel = int(petLevel)



        self.pet = self.savePet(speciesId=speciesId, is_must_add_new=is_must_add_new, token=token)
        self.item = self.saveItem(id=itemId, token=token, is_must_add_new=is_must_add_new, is_run_in_model=True)
        self.addServers(servers)

        self.serv_for_repr = servers

    def __repr__(self):
        return "Auc: {}; Servers: {}".format(self.auc, list([s.name_ru for s in self.serv_for_repr]))



    def savePet(self,speciesId, token, is_must_add_new=True):
        apiMasterList = "https://us.api.blizzard.com/wow/pet/?locale=en_US&access_token={}".format(token)
        if speciesId is not None:
            pet_from_db = Pets.query.filter(Pets.speciesId == str(speciesId)).first()  # type: Pets
            if pet_from_db is not None:
                return  pet_from_db
            else: #хоть написаный выше код и повторяется в savePet, но зато нам не надо ради каждого пета обращаться по сети..
                pets = getJSON(apiMasterList)["pets"]
                pet = None
                for pet in pets: #Ищем нужного пета в списке
                    if pet["stats"]["speciesId"] == speciesId:
                        break
                SavePetAndItem.savePet(self, pet= pet, token = token,is_must_add_new=is_must_add_new, is_run_in_model=True)
        else:
            return None

    def addServers(self, servers):
        for server in servers:
            self.servers.append(server)


class Pets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canBattle = db.Column(db.Boolean, index = True)
    creatureId = db.Column(db.Integer, index = True)

    name_ru = db.Column(db.String(128), index = True, unique = False)
    name_en = db.Column(db.String(128), index = True, unique = False)
    name_de = db.Column(db.String(128), index = True, unique = False)
    name_fr = db.Column(db.String(128), index = True, unique = False)
    name_es = db.Column(db.String(128), index = True, unique = False)

    description_ru = db.Column(db.String(550), index = True, unique = False)
    description_en = db.Column(db.String(550), index = True, unique = False)
    description_de = db.Column(db.String(550), index = True, unique = False)
    description_fr = db.Column(db.String(550), index = True, unique = False)
    description_es = db.Column(db.String(550), index = True, unique = False)

    source_ru = db.Column(db.String(450), index = True, unique = False)
    source_en = db.Column(db.String(450), index = True, unique = False)
    source_de = db.Column(db.String(450), index = True, unique = False)
    source_fr = db.Column(db.String(450), index = True, unique = False)
    source_es = db.Column(db.String(450), index = True, unique = False)

    abilities = db.Column(JSON)
    family = db.Column(db.String(64), index = True, unique = False)
    icon = db.Column(db.String(64), index = True, unique = False)
    speciesId = db.Column(db.Integer, index = True)
    qualityId = db.Column(db.Integer, index = True)

    breedId = db.Column(db.Integer, index = True)
    petQualityId = db.Column(db.Integer, index = True)
    level = db.Column(db.Integer, index = True)
    health = db.Column(db.Integer, index = True)
    power = db.Column(db.Integer, index = True)
    speed = db.Column(db.Integer, index = True)

    strongAgainst = db.Column(db.String(64), index = True, unique = False)
    weakAgainst = db.Column(db.String(64), index = True, unique = False)
    typeId = db.Column(db.Integer, index = True)

    aucs = db.relationship('Auctions', backref = 'pet', lazy='dynamic')

    def __init__(self,
                 canBattle,
                 creatureId,

                 name_ru,
                 name_en,
                 name_de,
                 name_fr,
                 name_es,

                 description_ru,
                 description_en,
                 description_de,
                 description_fr,
                 description_es,

                 source_ru,
                 source_en,
                 source_de,
                 source_fr,
                 source_es,

                 abilities,
                 family,
                 icon,
                 speciesId,
                 qualityId,

                 breedId,
                 petQualityId,
                 level,
                 health,
                 power,
                 speed,

                 strongAgainst,
                 weakAgainst,
                 typeId):

        self.canBattle = bool(canBattle)
        self.creatureId = int(creatureId)

        self.name_ru = name_ru
        self.name_en = name_en
        self.name_de = name_de
        self.name_fr = name_fr
        self.name_es = name_es

        self.description_ru = description_ru
        self.description_en = description_en
        self.description_de = description_de
        self.description_fr = description_fr
        self.description_es = description_es

        self.source_ru = source_ru
        self.source_en = source_en
        self.source_de = source_de
        self.source_fr = source_fr
        self.source_es = source_es

        self.abilities = abilities
        self.family = family
        self.icon = icon
        self.speciesId = int(speciesId)
        self.qualityId = int(qualityId)

        self.breedId = int(breedId)
        self.petQualityId = int(petQualityId)
        self.level = int(level)
        self.health = int(health)
        self.power = int(power)
        self.speed = int(speed)

        self.strongAgainst = strongAgainst
        self.weakAgainst = weakAgainst
        self.typeId = int(typeId)

    def __repr__(self):
        return "Name: {}; Desc: {} ".format(self.name_ru, self.description_ru)

class AssistInfo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.String(128), index = True, unique = False)
    value = db.Column(db.String(430), index = True, unique = False)

    def __init__(self, key, value):
        self.key = str(key)
        self.value = str(value)

    def __repr__(self):
        return "Key: {}; Value: {}".format(self.key, self.value)

class GameClass(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    spec = db.relationship('GameSpec', backref = 'g_class', lazy='dynamic') #dynamic

    name_ru = db.Column(db.String(128), index = True, unique = False)
    name_en = db.Column(db.String(128), index = True, unique = False)
    name_de = db.Column(db.String(128), index = True, unique = False)
    name_fr = db.Column(db.String(128), index = True, unique = False)
    name_es = db.Column(db.String(128), index = True, unique = False)

    power_type = db.Column(db.String(128), index = True, unique = False)

    def __init__(self,
                 name_ru,
                 name_en,
                 name_de,
                 name_fr,
                 name_es,
                 power_type):
        self.name_ru = name_ru
        self.name_en = name_en
        self.name_de = name_de
        self.name_fr = name_fr
        self.name_es = name_es

        self.power_type = power_type

    def __repr__(self):

        return 'Name: {}; Id: {}'.format(self.name_ru, self.id)

class GameSpec(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    class_id = db.Column(db.Integer, db.ForeignKey('game_class.id'), nullable = False)
    spec = db.relationship('Talants', backref = 'g_spec', lazy='dynamic') #Поле нужно переименновать в talant


    name_ru = db.Column(db.String(128), index=True, unique=False)
    name_en = db.Column(db.String(128), index=True, unique=False)
    name_de = db.Column(db.String(128), index=True, unique=False)
    name_fr = db.Column(db.String(128), index=True, unique=False)
    name_es = db.Column(db.String(128), index=True, unique=False)

    description_ru = db.Column(db.String(550), index=True, unique=False)
    description_en = db.Column(db.String(550), index=True, unique=False)
    description_de = db.Column(db.String(550), index=True, unique=False)
    description_fr = db.Column(db.String(550), index=True, unique=False)
    description_es = db.Column(db.String(550), index=True, unique=False)

    role = db.Column(db.String(64), index=True, unique=False)
    icon = db.Column(db.String(64), index=True, unique=False)
    backgroundImage = db.Column(db.String(64), index=True, unique=False)
    order = db.Column(db.Integer, index=True)

    def __init__(self,
                 g_class,
                 name_ru,
                 name_en,
                 name_de,
                 name_fr,
                 name_es,

                 description_ru,
                 description_en,
                 description_de,
                 description_fr,
                 description_es,
                 role,
                 icon,
                 backgroundImage,
                 order
                 ):

        self.g_class = g_class

        self.name_ru = name_ru
        self.name_en = name_en
        self.name_de = name_de
        self.name_fr = name_fr
        self.name_es = name_es

        self.description_ru = description_ru
        self.description_en = description_en
        self.description_de = description_de
        self.description_fr = description_fr
        self.description_es = description_es

        self.role = role
        self.icon = icon
        self.backgroundImage = backgroundImage
        self.order = int(order)

    def __repr__(self):
        return "Spec: {}; Class: {}".format(self.name_ru, self.g_class.name_ru) #Протестить


class Talants(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    spec_id = db.Column(db.Integer, db.ForeignKey('game_spec.id'), nullable = False)

    tier = db.Column(db.Integer, index=True)
    column = db.Column(db.Integer, index=True)
    spell_id = db.Column(db.Integer, index=True)
    castTime = db.Column(db.String(64), index=True, unique=False)
    range = db.Column(db.String(64), index=True, unique=False)
    powerCost = db.Column(db.String(64), index=True, unique=False)
    cooldown = db.Column(db.String(64), index=True, unique=False)

    name_ru = db.Column(db.String(128), index=True, unique=False)
    name_en = db.Column(db.String(128), index=True, unique=False)
    name_de = db.Column(db.String(128), index=True, unique=False)
    name_fr = db.Column(db.String(128), index=True, unique=False)
    name_es = db.Column(db.String(128), index=True, unique=False)

    description_ru = db.Column(db.String(1200), index=True, unique=False)
    description_en = db.Column(db.String(1200), index=True, unique=False)
    description_de = db.Column(db.String(1200), index=True, unique=False)
    description_fr = db.Column(db.String(1200), index=True, unique=False)
    description_es = db.Column(db.String(1200), index=True, unique=False)

    #конструктора нет так как он должен генерится автоматом #Протестить
    def __repr__(self):
        return "Name: {}; Spec: {}; Class: {};".format(self.name_ru, self.g_spec.name_ru, self.g_spec.g_class.name_ru) #протестить
