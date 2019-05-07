from copy import copy

from Core.models import GameClass, Talants, GameSpec, Auctions, Servers, Items, Pets


class GetDict:
    langs = ["ru", "en", "de", "fr", "es"]

    @staticmethod
    def getClasses(lang):
        data = []
        if lang in GetDict.langs:
            clss = GameClass.query.all()
            for cls in clss:
                data.append({"id": cls.id, "name" : getattr(cls, "name_{}".format(lang))})
            return data
        else:
            return {"error" : "no lang"}

    @staticmethod
    def getSpecs(lang):
        data = []
        if lang in GetDict.langs:
            clss = GameClass.query.all()
            for cls in clss:
                for spec in cls.spec:
                    data.append({"class_id": cls.id, "id": spec.id, "spec_order": spec.order,"name": getattr(spec, "name_{}".format(lang)),
                                                                         "description":getattr(spec, "description_{}".format(lang)),
                                                                         "icon": spec.icon})
            return  data
        else:
            return {"error" : "no lang"}

    @staticmethod
    def getClassSpecDict(lang):
        data = {}
        if lang in GetDict.langs:
            clss = GameClass.query.all()
            for cls in clss:
                data[getattr(cls, "name_{}".format(lang))] = {"id": cls.id,
                                                              "specs":[{"name": getattr(spec, "name_{}".format(lang)),
                                                                         "description":getattr(spec, "description_{}".format(lang)),
                                                                         "icon": spec.icon, "id": spec.id} for spec in cls.spec]}
            return  data
        else:
            return {"error" : "no lang"}

    @staticmethod
    def getTalent(cls, spec, lang):
        data = {}
        talants = Talants.query.join(GameSpec, GameSpec.id == Talants.spec_id).join(GameClass, GameClass.id == GameSpec.class_id).filter(GameClass.id == int(cls),GameSpec.order == int(spec)).order_by(Talants.id.asc()).all()
        if lang in GetDict.langs:
            data["talents"] = [{"id" : t.id, "spec_id" : t.spec_id,"name": getattr(t,"name_{}".format(lang)), "description": getattr(t, "description_{}".format(lang)),
                                "castTime":t.castTime, "range": t.range, "powerCost": t.powerCost, "cooldown":t.cooldown,
                                "row":t.tier, "col":t.column} for t in talants]
            return data
        else:
            return {"error": "no lang"}

    @staticmethod
    def getAuctionsAll(slug, region, lang, page = 1, is_for_deals = False, itemId = None, petId = None, bid = None, buyout = None, time_left = None):
        data = {}
        server = Servers.query.filter(Servers.slug == str(slug), Servers.region == str(region)).first()

        if is_for_deals is False:
            aucs = Auctions.query.join(Items, Items.id == Auctions.item_id).outerjoin(Pets, Pets.id == Auctions.pet_id).filter(
                Auctions.servers.contains(server)).paginate(page, 40, False).items

        if is_for_deals is True:
            item = Items.query.filter(Items.gameId == itemId).first()
            if petId is None:
                aucs = Auctions.query.join(Items, Items.id == Auctions.item_id).outerjoin(Pets, Pets.id == Auctions.pet_id).filter(
                    Auctions.servers.contains(server), Auctions.item == item,Auctions.timeLeft.in_(time_left), Auctions.bid <= bid, Auctions.buyout<=buyout).all()
            else:
                pet = Pets.query.filter(Pets.speciesId == petId).first()
                aucs = Auctions.query.join(Items, Items.id == Auctions.item_id).outerjoin(Pets, Pets.id == Auctions.pet_id).filter(
                    Auctions.servers.contains(server), Auctions.item == item, Auctions.pet == pet,
                    Auctions.timeLeft.in_(time_left), Auctions.bid <= bid, Auctions.buyout<=buyout).all()


        def getDictElem(lot):
            if lot.item.gameId ==82800:
                item = "Pet:" + str(getattr(lot.pet, "name_{}".format(lang))) + ", lvl: " + str(lot.petLevel)
                pet = lot.pet.speciesId
                key_pet = "pet"
            else:
                item = str(getattr(lot.item, "name_{}".format(lang)))
                pet = None
                key_pet = None

            data = {"item": item, "gameId": lot.item.gameId, key_pet:pet ,"icon":lot.item.icon ,"bid": lot.bid, "buyout": lot.buyout, "owner": lot.owner, "time:": lot.timeLeft}
            return data

        print(len(aucs))
        if len(aucs) != 0:
            if lang in GetDict.langs:
                data["auctions"] = list(map(getDictElem, aucs))
                return data
            else:
                return {"error": "no lang"}
        else:
            return {"error": "no auctions"}

    @staticmethod
    def getDeals(json, lang):
        data = {"auctions":[]}
        if json is None:
            return {"error": "no data in json"}
        else:
            for item in json["best_lot"]:
                time_list = ["VERY_LONG", "LONG","MEDIUM", "SHORT"]

                if item["time_left"] == "ANY" or item["time_left"] =="VERY_LONG": #?
                    time_left = copy(time_list)[0:None]
                elif item["time_left"] == "LONG":
                    time_left = copy(time_list)[1:None]
                elif item["time_left"] == "MEDIUM":
                    time_left = copy(time_list)[2:None]
                elif item["time_left"] == "SHORT":
                    print("==")
                    time_left = copy(time_list)[3:None]

                print(time_left)
                if "pet_id" in item:
                    pet_id = item["pet_id"]
                else:
                    pet_id = None

                aucs = GetDict.getAuctionsAll(is_for_deals=True, slug=item["server"],
                                                               region=item["region"], time_left=time_left,lang = lang,
                                                               itemId=item["item_game_id"], petId=pet_id, bid=item["bid"],
                                                               buyout=item["buyout"])

                if "auctions" in aucs:
                    data["auctions"].append(aucs["auctions"])

            if len(data["auctions"]) == 0:  data = {"error": "no auctions"}
            return data


    @staticmethod
    def getOneItemOrPetOrNone(name, type, lang):
        data = {}
        if lang in GetDict.langs:
            if type == "item":
                item = Items.query.filter(getattr(Items, "name_{}".format(lang)) == name).first()
                if item is None:
                    return {"error": "not found"}
                else:
                    data["item"] = { "game_id": item.gameId, "item": str(getattr(item, "name_{}".format(lang))), "description" :str(getattr(item, "description_{}".format(lang))), "icon": item.icon}
                    return data
            elif type == "pet":
                pet = Pets.query.filter(getattr(Pets, "name_{}".format(lang)) == name).first()
                if pet is None:
                    return {"error": "not found"}
                else:
                    data["pet"] = {"speciesId": pet.speciesId,"pet": str(getattr(pet, "name_{}".format(lang))), "description" :str(getattr(pet, "description_{}".format(lang))), "icon": pet.icon}
                    return data
            else:
                return {"error": "no type"}
        else:
            return {"error": "no lang"}



