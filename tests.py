from Core.Utilites import AccessToken
from Core.models import Auctions, Items, Servers, Pets
from Core.API.ToDict import *

# server = Servers.query.filter(Servers.slug == "borean-tundra", Servers.region == "us").first()
# aucs = Auctions.query.join(Items, Items.id == Auctions.item_id).outerjoin(Pets, Pets.id == Auctions.pet_id).filter(
#     Auctions.servers.contains(server)).paginate(1, 40, False).items
# for auc in aucs:
#     print(str(auc.item.name_ru) + " " + str(auc.auc) + " " )
# print(len(aucs))

print(Items.query.filter(getattr(Items, "name_{}".format("ru")) == "Фаронаарская шипучка").first())