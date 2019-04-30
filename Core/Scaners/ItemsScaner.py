from threading import Thread
import time
from Core import db
from Core.models import Items, AssistInfo, SavePetAndItem
from Core.Utilites.Utilites import getJSON, ThredCounter, Reporter, ThreadStopper
from Core.Utilites.AccessToken import getToken, updateToken


class ItemThread(Thread, SavePetAndItem):
    def __init__(self, requestId, counter, access_token):
        Thread.__init__(self)
        self.requestId = requestId
        self.counter = counter
        self.token = access_token

    def run(self):
        self.counter.plus()
        self.saveItem(self.requestId,self.token)
        self.counter.minus()


class ItemScaner(Thread):
    def __init__(self,reporter, stopper, maxItemId, minItemId = 0, countOfThreads = 16, startFromLast = False):
        Thread.__init__(self)
        self.reporter = reporter #type: Reporter
        self.stopper = stopper #type: ThreadStopper
        self.maxItemId = maxItemId
        self.minItemId = minItemId
        self.countOfThreads = countOfThreads
        self.counter = ThredCounter()
        updateToken()
        self.token = getToken()["access_token"]
        if startFromLast is True:
            self.minItemId = int(AssistInfo.query.filter(AssistInfo.key == "LastItem").first().value)
            print("min id {}".format(self.minItemId))
        if self.maxItemId < self.minItemId:
            self.maxItemId = self.maxItemId + 3 * self.countOfThreads
            print("max id {}".format(self.maxItemId))



    def run(self):
        start = self.minItemId
        self.reporter.itemscan["isWork"] = True
        self.reporter.itemscan["total"] = self.maxItemId
        for stop in range(self.minItemId, self.maxItemId, self.countOfThreads):
            self.reporter.itemscan["current"] = stop
            self.reporter.itemscan["percent"] = round(float(stop/self.maxItemId*100), 3)
            for num in range(start, stop):
                self.thread = ItemThread(num, self.counter, self.token)
                self.thread.start()
            while self.counter.num != 0:
                time.sleep(0.01)
            AssistInfo.query.filter(AssistInfo.key == "LastItem").first().value = start
            db.session.commit()
            start = stop
            if self.stopper.is_item_thread_must_stop is True:
                break
        self.reporter.itemscan["isWork"] = False

# r = Reporter()
# s = ThreadStopper()
# i = ItemScaner(r,s, 100000, startFromLast=True)
# i.start()
# s.is_server_thread_must_stop = bool(input("выключить?"))
#
# i.join()