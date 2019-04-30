from Core.Utilites.Utilites import *

apiLink = "http://auction-api-eu.worldofwarcraft.com/auction-data/cfd8e4ec08837659a70e7ed1863ebcc6/auctions.json"
apiLink2= "https://jsonplaceholder.typicode.com/todos"
item = "https://eu.api.blizzard.com/wow/item/18803?locale=ru_RU&access_token=USmY7qytFUyk6FCPD2fuXJMEW3c1epj8Hl"
player = "https://eu.api.blizzard.com/wow/character/borean-tundra/Пукон?locale=ru_RU&access_token=USmY7qytFUyk6FCPD2fuXJMEW3c1epj8Hl"

def getItemData(item, region = "eu", locale = "ru_RU", token = "USckX6Mz025udY0md22w40JKIBMwOwZ6LB"):
    itemApi = "https://{}.api.blizzard.com/wow/item/{}?locale={}&access_token={}".format(region, item, locale, token)
    data = getJSON(itemApi)
    try:
        return {"name":data["name"], "description" : data["description"], "icon": data["icon"],  "itemClass" : data["itemClass"], "itemSubClass" : data["itemSubClass"],"itemLevel" : data["itemLevel"], "itemSource" : data["itemSource"]["sourceType"] }
    except:
        return "Something wrong.."

def getFactionByPlayer(name, server, region = "eu", locale = "ru_RU", token = "USckX6Mz025udY0md22w40JKIBMwOwZ6LB"):
    playerApi = "https://{}.api.blizzard.com/wow/character/{}/{}?locale={}&access_token={}".format(region,server,name,locale,token)
    print(playerApi)
    data = getJSON(playerApi)
    try:
        if int(data["faction"]) == 0: return "Alliance"
        elif int(data["faction"]) == 1: return "Horde"
    except:
        return "WrongArgs/NoPlayer"

def getClearAuctinData(server, region = "eu", locale = "ru_RU", token ="USckX6Mz025udY0md22w40JKIBMwOwZ6LB"):

    apiGetLink = "https://{}.api.blizzard.com/wow/auction/data/{}?locale={}&access_token={}".format(region,server,locale,token)
    try:
        urlAndTimeData = getJSON(apiGetLink)
        newData = {"lastModified":urlAndTimeData["files"][0]["lastModified"], "auctions" : []}
        data = getJSON(urlAndTimeData["files"][0]["url"])

        for auction in data["auctions"]:
            newData["auctions"].append({"auc": auction["auc"],"item" : auction["item"],
                                        # "item" : [getItemData(auction["item"], region, locale, token)],
                                        # "faction" : getFactionByPlayer(str(auction["owner"]), server, region, locale, token),
                                        "owner":str(auction["owner"]), "bid": auction["bid"], "buyout" : auction["buyout"],
                                        "quantity":auction["quantity"], "timeLeft":auction["timeLeft"]})
        return newData
    except:
        return "Something wrong.."

def wowTokenPrice():

    apiLink = "https://{}.api.blizzard.com/data/wow/token/index?namespace={}&locale={}&access_token={}"


# max_bid = 0
# max_buyout = 0
# data = getClearAuctinData("borean-tundra")
# for auc in  data["auctions"]:
#    if (max_bid < int(auc["bid"])) and int(auc["bid"]) < 9731726154: max_bid = int(auc["bid"])
#    if (max_buyout < int(auc["buyout"]))and int(auc["buyout"]) < 9731726154: max_buyout = int(auc["buyout"])
#
# print("Max bid: " + str(max_bid))
# print("Max max_buyout: " + str(max_buyout))
# print("Total: " + str(len(data["auctions"])))
#
#
# with timer():
#     with open("auctions.json", "w", encoding='utf-8') as file:
#         jsonData = json.dump(getClearAuctinData("borean-tundra"), file, indent=4,  ensure_ascii=False)