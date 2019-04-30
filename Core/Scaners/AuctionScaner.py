from Core.Utilites.Utilites import getJSON, ThredCounter, Reporter, ThreadStopper, timer, Log
from Core.models import Servers, Auctions, servers_auctions
from Core.Utilites.AccessToken import getToken, updateToken
from threading import Thread
import datetime,time,math
from sqlalchemy import func, asc
from Core import db
import traceback


class AuctionsScaner(Thread):
    def __init__(self,reporter, stopper,cycle_time = 40, countOfThreads = 4, lot_limit = None):
        Thread.__init__(self)
        updateToken()
        self.token = getToken()["access_token"]
        self.counter = ThredCounter()
        self.counOfThread = countOfThreads
        self.reporter = reporter #type: Reporter
        self.stopper = stopper #type: ThreadStopper
        self.cycle_time = cycle_time
        self.lot_limit= lot_limit

    def run(self):
        self.reporter.aucscan["isWork"] = True
        self.reporter.aucscan["star_time"] = datetime.datetime.now()
        while self.stopper.is_auc_thread_must_stop is False:
            time_start = datetime.datetime.now()
            cycle_time = datetime.timedelta(minutes=self.cycle_time)
            unique_server = Servers.query.with_entities(Servers.auc, Servers.timestamp).distinct().order_by(asc(Servers.timestamp)).all()
            stop = self.counOfThread
            start = 0
            realms_count = len(list(unique_server))
            self.reporter.aucscan["total"] = realms_count
            for i in range(0, math.ceil(realms_count/self.counOfThread)):
                if stop >= realms_count:
                    stop = realms_count
                for server in unique_server[start:stop]:
                    self.reporter.aucscan["auc_num"] +=1
                    thread = AucThread(lot_limit=self.lot_limit ,auc_link=server.auc,token= self.token,is_must_add_new = True, counter=self.counter, reporter=self.reporter)
                    thread.start()
                    Log.write("Запущен поток AucThread; Name: {}".format(thread.name), "AUC_INFO")
                while self.counter.num != 0:
                    time.sleep(0.01)
                if self.stopper.is_auc_thread_must_stop is True:
                    break
                self.reporter.aucscan["percent"] = round(float(stop/realms_count*100), 1)
                self.reporter.aucscan["current"] = stop
                self.reporter.aucscan["avg_auc"] = round(float(int(self.reporter.aucscan["auc_summ"]) / int(self.reporter.aucscan["auc_num"])))
                self.reporter.aucscan["avg_auc_time"] = str(time.strftime('%H:%M:%S',time.gmtime(
                                                        round(float(int(self.reporter.aucscan["auc_time_summ"])/int(self.reporter.aucscan["auc_num"]))))))
                Log.write("Среднее время скана 1 аука: {}".format(self.reporter.aucscan["avg_auc_time"]), "AUC_INFO")
                Log.write("Среднее количество лотов на аукционах: {}".format(self.reporter.aucscan["avg_auc"]),"AUC_INFO")

                stop += self.counOfThread
                start += self.counOfThread

            if (datetime.datetime.now() - time_start) < cycle_time:
                Log.write("Сон после цикла: {} сек.".format((time_start + cycle_time-datetime.datetime.now())),"AUC_INFO")
                time.sleep((time_start + cycle_time-datetime.datetime.now()).total_seconds())
                Log.write("Сон завершен","AUC_INFO")

            if int(self.reporter.aucscan["number_of_cycles"])%10 == 0:
                updateToken()
                Log.write("Обновлен токен","AUC_INFO")
                self.token = getToken()["access_token"]

            self.reporter.aucscan["cycle_time_summ"] +=round((datetime.datetime.now() - time_start).total_seconds())
            self.reporter.aucscan["number_of_cycles"] +=1
            self.reporter.aucscan["avg_cycle_time"] = str(time.strftime('%H:%M:%S',time.gmtime(
                                                        round(float(int(self.reporter.aucscan["cycle_time_summ"])/int(self.reporter.aucscan["number_of_cycles"]))))))
            Log.write("Время цикла скана всех серверов {}".format(self.reporter.aucscan["avg_cycle_time"]), "AUC_INFO")
        self.reporter.aucscan["isWork"] = False




class AucThread(Thread):
    def __init__(self, auc_link, token, counter, is_must_add_new, reporter, lot_limit = None):
        Thread.__init__(self)
        self.is_must_add_new = is_must_add_new
        self.counter = counter #type: ThredCounter
        self.reporter = reporter #type: Reporter
        self.token = token
        self.auc_link = auc_link
        self.apiAuction = "https://{}.api.blizzard.com/wow/auction/data/{}?locale=en_US&access_token={}"
        self.lot_limit = lot_limit


    def run(self):
        try:
            self.counter.plus()
            servers = Servers.query.filter(Servers.auc==self.auc_link).all()
            self.dateDifferenceChecking(servers)

            time = servers[0].timestamp
            auc_info = getJSON(self.apiAuction.format(servers[0].region, servers[0].slug, self.token))["files"][0]
            time_new = datetime.datetime.utcfromtimestamp(int(auc_info["lastModified"]) / 1000)
            time_counter_star = datetime.datetime.now()
            if time != time_new:
                auc_data = getJSON(auc_info["url"])
                self.reporter.aucscan["auc_summ"] += int(len(auc_data["auctions"])) #общее количество обработанных лотов
                for auc in auc_data["auctions"][0:self.lot_limit]:
                    bonusLists=modifiers=petBreedId=petLevel=speciesId = None #для элеменетов не всегда встречающихся в auc - json
                    if "bonusLists" in auc:
                        bonusLists = auc["bonusLists"]
                    if "modifiers" in auc:
                        modifiers = auc["modifiers"]
                    if "petBreedId" in auc:
                        petBreedId = auc["petBreedId"]
                    if "petLevel" in auc:
                        petLevel = auc["petLevel"]
                    if "petSpeciesId" in auc:
                        speciesId = auc["petSpeciesId"]

                    auction = Auctions(auc= auc["auc"],itemId= auc["item"], servers=servers, timestamp=time_new, owner=auc["owner"],
                                       ownerRealm=auc["ownerRealm"], bid=auc["bid"],buyout=auc["buyout"],quantity=auc["quantity"],
                                       timeLeft=auc["timeLeft"],rand=auc["rand"], seed=auc["seed"],context=auc["context"], token=self.token,
                                       is_must_add_new=self.is_must_add_new, bonusLists=bonusLists, modifiers=modifiers,
                                       petBreedId=petBreedId,petLevel=petLevel,speciesId=speciesId)
                    print("Новый лот ({}): {}".format(self.name ,auction))
                    db.session.add(auction)
                    db.session.commit()

                lots_for_del = Auctions.query.join(Servers.aucs).filter(Auctions.timestamp < time_new, Servers.auc == servers[0].auc).all()
                list_id_for_del = list([lot.id for lot in lots_for_del])
                print("({})Количество удаляемых лотов {}".format(self.name,len(list_id_for_del)))
                Auctions.query.filter(Auctions.id.in_(list_id_for_del)).delete(synchronize_session=False)
                db.session.commit()
                for server in servers:
                    server.timestamp = time_new
                    db.session.commit()
                self.reporter.aucscan["auc_time_summ"] += round((datetime.datetime.now() - time_counter_star).total_seconds())
        except Exception as e:
            Log.write(str(e), "ERROR")
            Log.write("Трасса:\n==============================" + str(traceback.format_exc()) + "==============================", "traceback".upper())
        finally:
            self.counter.minus()

    def dateDifferenceChecking(self, servers):
        '''Исправляет дату в тех случаях, когда произошол сбой при сохранении даты последнего скана (таблиц серверов)'''
        scan_data_base = servers[0].timestamp
        for server in servers:
            if scan_data_base != server.timestamp:
                max_data = Servers.query.with_entities(func.max(Servers.timestamp)).filter(Servers.auc == servers[0].auc).all()[0][0]
                for s in servers:
                    s.timestamp = max_data
                    db.session.commit()
                Log.write("Исправлено рассинхронизация дат для серверов с auc: {}".format(servers[0].auc), "INFO")
                print("Исправлено рассинхронизация дат для серверов с auc: {}".format(servers[0].auc))
                break



if __name__ == '__main__':
    print("Запущен скан ауков самостоятельно")
    s = ThreadStopper()
    report = Reporter()
    s.is_auc_thread_must_stop = False
    with timer():
        t = AuctionsScaner(report, s, lot_limit = 80)
        t.start()
        s.is_auc_thread_must_stop = bool(input("выключить?"))

        t.join()


