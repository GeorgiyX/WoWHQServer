from Core import db
from Core.Utilites import AccessToken
from Core.models import Auctions, Items, Servers, Pets, User
from Core.API.ToDict import *

# server = Servers.query.filter(Servers.slug == "borean-tundra", Servers.region == "us").first()
# aucs = Auctions.query.join(Items, Items.id == Auctions.item_id).outerjoin(Pets, Pets.id == Auctions.pet_id).filter(
#     Auctions.servers.contains(server)).paginate(1, 40, False).items
# for auc in aucs:
#     print(str(auc.item.name_ru) + " " + str(auc.auc) + " " )
# print(len(aucs))

# print(Items.query.filter(getattr(Items, "name_{}".format("ru")) == "Фаронаарская шипучка").first())
#
# slugs = Servers.query.with_entities(Servers.slug).distinct(Servers.slug).all()
# with open("slugs", "a", encoding="utf-8") as f:
#     for slug in slugs:
#         f.write("<item>"+(str(slug.slug))+"</item>" + "\n")

# user = User("admin", "T7XsA2A~xaqSOSwjgVl%8hha~oV7%|z6|i}P8rOHOylFtfnUi6oC$Wt")
# db.session.add(user)
# db.session.commit()

import time, datetime

print(datetime.datetime.utcfromtimestamp(1558079641))
print(str(datetime.datetime(2017, 2, 26) -datetime.datetime.now()))