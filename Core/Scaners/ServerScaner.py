from Core import db
from Core.Utilites.AccessToken import getToken, updateToken
from threading import Thread
from Core.models import Servers
from Core.Utilites.Utilites import getJSON, ThredCounter, Reporter, ThreadStopper, timer
from datetime import datetime
import time
import math

class ServerScaner(Thread):
    def __init__(self, reporter, stopper, countOfThreads = 12):
        Thread.__init__(self)
        updateToken()
        self.token = getToken()["access_token"]
        self.regions = ["us", "eu"]
        self.apiServers = "https://{}.api.blizzard.com/data/wow/realm/index?namespace=dynamic-{}&access_token={}"
        self.counter = ThredCounter()
        self.counOfThread = countOfThreads
        self.reporter = reporter #type: Reporter
        self.stopper = stopper #type: ThreadStopper

    def run(self):
        self.reporter.serverscan["isWork"] = True
        for region in self.regions:
            if self.stopper.is_server_thread_must_stop is True:
                break
            self.reporter.serverscan["region"] = region
            realms = getJSON(self.apiServers.format(region, region, self.token))

            stop = self.counOfThread
            start = 0
            realms_count = len(list(realms["realms"]))
            self.reporter.serverscan["total"] = realms_count
            for i in range(1,math.ceil(realms_count/self.counOfThread)+1):
                if stop >= realms_count:
                    stop = realms_count
                for realm in realms["realms"][start:stop]:
                    self.thread = RealmThread(region, realm, self.counter, self.token)
                    self.thread.start()
                while self.counter.num != 0:
                    time.sleep(0.01)
                if self.stopper.is_server_thread_must_stop is True:
                    break
                self.reporter.serverscan["current"] = stop
                self.reporter.serverscan["percent"] = round(float(stop/realms_count*100), 1)
                stop += self.counOfThread
                start+= self.counOfThread
        self.reporter.serverscan["isWork"]= False




class RealmThread(Thread):
    def __init__(self, region, realm, counter, token):
        Thread.__init__(self)
        self.region = region
        self.realm = realm
        self.counter = counter
        self.token = token
        self.apiAuction = "https://{}.api.blizzard.com/wow/auction/data/{}?locale=en_US&access_token={}"


    def run(self):
        self.counter.plus()
        if self.realm["slug"]=="pozzo-delleternità":
            self.realm["slug"] = "pozzo-delleternita"
        elif self.realm["slug"]=="aggra-português":
            self.realm["slug"] = "aggra-portugues"
        try:
            auc_info = getJSON(self.apiAuction.format(self.region, self.realm["slug"], self.token))["files"][0]
        except:
            print(self.apiAuction.format(self.region, self.realm["slug"], self.token))
        server = Servers.query.filter(Servers.slug == str(self.realm["slug"]), Servers.region == self.region).first()  # type: Servers
        if server is None:
            server = Servers(bliz_id=self.realm["id"], slug=self.realm["slug"], region=self.region, name=self.realm["name"]["en_US"],
                             name_ru=self.realm["name"]["ru_RU"], auc=auc_info["url"],
                             timestamp=datetime.utcfromtimestamp(1101168000)) #1546365400 1101168000
            print("New: {}".format(server))
            db.session.add(server)
            db.session.commit()
        else:
            server.bliz_id = self.realm["id"]
            server.slug = self.realm["slug"]
            server.region = self.region
            server.name = self.realm["name"]["en_US"]
            server.name_ru = self.realm["name"]["ru_RU"]
            server.auc = auc_info["url"],
            server.timestamp = datetime.utcfromtimestamp(1101168000)
            print("Updated: {}".format(server))
            db.session.commit()
        self.counter.minus()

if __name__ == '__main__':
    print("Запущен скан сервов самостоятельно")
    s = ThreadStopper()
    s.is_server_thread_must_stop = False
    report = Reporter()
    with timer():
        t = ServerScaner(report, s)
        t.start()
        s.is_server_thread_must_stop = bool(input("выключить?"))

        t.join()
