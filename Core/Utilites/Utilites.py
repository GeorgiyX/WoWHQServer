import datetime
import requests
import time
import random
import threading

class timer():
    def __enter__(self):
        self.start = datetime.datetime.now()
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(str(datetime.datetime.now()-self.start))


def getJSON(api, sleep_when_error = 1):
    while True:
        try:
            data = requests.get(api)
            while data.status_code == 429 or data.status_code == 503:
                sleep_when_error +=2*random.random()
                time.sleep(sleep_when_error)
                data = requests.get(api)
                print(data.status_code)
            if data.status_code == 404:
                return False
            return data.json()
            break
        except:
            sleep_when_error += 2 * random.random()
            print("Ошибка в getJSON, сон - {}".format(sleep_when_error))


class ThredCounter():
    '''Позволяет определить количество одновременно работающих потоков'''
    def __init__(self):
        self.__num = 0
    @property
    def num(selfs):
        return selfs.__num
    @num.setter
    def num(self, num):
        if num < 0:
            print("Num can't be less than 0")
        else:
            self.__num = num
    def plus(self):
        self.__num +=1
    def minus(self):
        self.__num -=1

class Reporter():
    def __init__(self):
        self.serverscan = {"isWork": False, "current": 0, "total":0,"percent": 0, "region": None}
        self.itemscan = {"isWork": False, "current": 0, "total":0,"percent": 0}
        self.petscan = {"isWork": False, "current": 0, "total":0, "percent": 0}
        self.aucscan = {"isWork": False, "current": 0, "total":0, "percent": 0, "star_time" : 0,
                        "number_of_cycles": 0, "auc_summ":0, "auc_time_summ":0, "auc_num": 0,
                        "cycle_time_summ":0,"avg_cycle_time":0,"avg_auc": 0, "avg_auc_time": 0}
        self.wowtokenscan = {"isWork": False,"number_of_cycles": 0, "work_time":None}

class ThreadStopper():
    def __init__(self):
        self.is_server_thread_must_stop = True
        self.is_item_thread_must_stop = True
        self.is_pet_thread_must_stop = True
        self.is_auc_thread_must_stop = True
        self.is_wowtoken_thread_must_stop = True



class Log():
    lock = threading.Lock()
    @staticmethod
    def write(message, tag = "test"):
        with Log.lock:
            with open("log.txt", "a+") as f:
                f.write(str(datetime.datetime.now().strftime("%Y-%B-%d %H:%M:%S")) + " ::: " + "[{}] ::: ".format(tag) + message+"\n")








