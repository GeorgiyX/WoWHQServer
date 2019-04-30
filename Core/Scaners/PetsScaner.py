from threading import Thread
import time, math
from Core import db
from Core.models import Pets, SavePetAndItem
from Core.Utilites.Utilites import getJSON, ThredCounter, Reporter, ThreadStopper
from Core.Utilites.AccessToken import getToken, updateToken

class PetScaner(Thread):
    def __init__(self, reporter, stopper, countOfThreads = 12):
        Thread.__init__(self)
        updateToken()
        self.token = getToken()["access_token"]
        self.counter = ThredCounter()
        self.counOfThread = countOfThreads
        self.reporter = reporter #type: Reporter
        self.stopper = stopper #type: ThreadStopper
        self.apiMasterList = "https://us.api.blizzard.com/wow/pet/?locale=en_US&access_token={}".format(self.token)

    def run(self):
        pets = getJSON(self.apiMasterList)["pets"]
        pet_count = len(pets)
        start = 0
        stop = self.counOfThread
        self.reporter.petscan["isWork"] = True
        self.reporter.petscan["total"] = pet_count
        for i in range(0, math.ceil(pet_count/self.counOfThread)):
            if stop >= pet_count:
                stop = pet_count
            for pet in pets[start:stop]:
                thread = PetThread(pet = pet, token=self.token, counter=self.counter)
                thread.start()
            while self.counter.num != 0:
                time.sleep(0.01)
            if self.stopper.is_pet_thread_must_stop is True:
                break
            self.reporter.petscan["current"] = stop
            self.reporter.petscan["percent"] = round(float(stop/pet_count*100), 1)
            stop += self.counOfThread
            start += self.counOfThread
        self.reporter.petscan["isWork"] = False


class PetThread(Thread, SavePetAndItem):
    def __init__(self, pet, token, counter):
        Thread.__init__(self)
        self.pet = pet
        self.token = token
        self.counter = counter #type: ThredCounter

    def run(self):
        self.counter.plus()
        self.savePet(self.pet,self.token)
        self.counter.minus()

# s = ThreadStopper()
# r = Reporter()
# with timer():
#     m = PetScaner(stopper=s, reporter=r)
#     m.start()
#     s.is_pet_thread_must_stop = bool(input("Стопнуть?"))
#     print(r.petscan["percent"])
#     m.join()
