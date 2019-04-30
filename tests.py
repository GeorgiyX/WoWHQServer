
# apiGetLink = "https://{}.api.blizzard.com/wow/auction/data/{}?locale=en_US&access_token=EUrx1Nq3E6xE2Yxeu8YU8nwAddm3JM63DC "
# servers_auctions = []
# servers =  Servers.query.filter(Servers.region == "eu").all()[::8] #type: Servers
# for server in servers[:4]:
#     print(server.slug)
#     data = getJSON(getJSON("https://{}.api.blizzard.com/wow/auction/data/{}?access_token=EUcvCPqDZJlhpXQmAxD4BpFNrbL3kgUoaD".format(server.region,server.slug))["files"][0]["url"])
#     servers_auctions.append(data["realms"])
# print("=======")
# print(servers_auctions)
# with open("auction-servers-EU.txt", "w") as file:
#     for el in servers_auctions:
#         file.write(str(el) + "\n")

# result=[]
# count =0
# data =getJSON("https://eu.api.blizzard.com/wow/pet/?locale=ru_RU&access_token=USAgBaklw2CzVlNz93jvs3NXgT0xs1cgrP")
# for pet in data["pets"]:
#     if len(pet["strongAgainst"])>0:
#         result.append(pet["weakAgainst"])
#     count+=1
#
# print(len(result))
# print(count)


# list = [0,1,2,3,4,5,6,7,8,9]
# print(list[0:len(list)-1])



# from Core.Utilites.Utilites import getJSON
# print(len(getJSON("https://eu.api.blizzard.com/data/wow/realm/index?namespace=dynamic-eu&locale=en_GB&access_token=USERS1aY0P5pQmlGDWAY2Nvc16G75rhd9X")["realms"]))






# from Core import db





# def dateDifferenceChecking(servers):
#     '''Исправляет дату в тех случаях, когда произошол сбой при сохранении даты последнего скана (таблиц серверов)'''
#     scan_data_base = servers[0].timestamp
#     for server in servers:
#         if scan_data_base != server.timestamp:
#             max_data = \
#             Servers.query.with_entities(func.max(Servers.timestamp)).filter(Servers.auc == servers[0].auc).all()[0][0]
#             for s in servers:
#                 s.timestamp = max_data
#                 db.session.commit()
#             print("Исправлено рассинхронизация дат для серверов с auc: {}".format(servers[0].auc))
#             break
#
# servers = Servers.query.all()
# for s in servers:
#     serv = Servers.query.filter(Servers.auc == s.auc)
#     dateDifferenceChecking(servers=serv)
import datetime
from sqlalchemy import asc
import time
from Core.models import Auctions, Servers

# unique_server = Servers.query.with_entities(Servers.auc, Servers.timestamp).distinct().order_by(
#     asc(Servers.timestamp)).all()
#
#
#
# lots = Auctions.query.join(Servers.aucs).filter(Servers.auc == unique_server[0].auc).all()
# lot_id_for_del = list([l.id for l in lots])
# print(unique_server[2].auc)
# print("Количество удаляемых лотов {}".format(len(lots)))
#
#
# old_lots = Auctions.query.filter( Auctions.id.in_(lot_id_for_del)).all()
# print(len(old_lots))
a= Auctions.query.all()
a.close()

