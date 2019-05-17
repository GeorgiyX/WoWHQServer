from Core.Utilites.Utilites import getJSON, Reporter,ThreadStopper
from Core.Utilites.AccessToken import getToken, updateToken
from threading import Thread
from Core import db
from Core.models import WowToken
import time, datetime

class WoWTokenScaner(Thread):

    regions = [("us","us"), ("eu","eu"), ("kr","korea"), ("tw","taiwan"), ("cn","china")]
    cn_API = "https://gateway.battlenet.com.cn/data/wow/token/index?namespace=dynamic-cn&locale=en_US&access_token={}"
    API = "https://{}.api.blizzard.com/data/wow/token/index?namespace=dynamic-{}&locale=en_US&access_token={}"
    wowtokenprice_API = "https://wowtokenprices.com/current_prices.json"

    def __init__(self,reporter, stopper, pause_time = 10):
        Thread.__init__(self)
        updateToken()
        self.token = getToken()["access_token"]
        self.pause_time = datetime.timedelta(minutes=pause_time)
        self.reporter = reporter #type: Reporter
        self.stopper = stopper #type: ThreadStopper

    def run(self):
        time_start = datetime.datetime.now()
        self.reporter.wowtokenscan["isWork"] = True
        while self.stopper.is_wowtoken_thread_must_stop is False:
            wtp_data = getJSON(WoWTokenScaner.wowtokenprice_API)
            for region in WoWTokenScaner.regions:
                if region[0] == "cn":
                    blizz_data = getJSON(WoWTokenScaner.cn_API.format(self.token))
                else:
                    blizz_data = getJSON(WoWTokenScaner.API.format(region[0],region[0],self.token))

                token = WowToken.query.filter(WowToken.region == region[0]).first()

                token.current_price_blizzard_api = int(blizz_data["price"]) / 10000,
                token.current_price_wowtokenprices_api = int(wtp_data[region[1]]["current_price"])
                token.timestamp_blizzard_api = datetime.datetime.utcfromtimestamp(int(blizz_data["last_updated_timestamp"]) / 1000)
                token.timestamp_wowtokenprices_api = datetime.datetime.utcfromtimestamp(wtp_data[region[1]]["time_of_last_change_unix_epoch"])
                token.last_change = int(wtp_data[region[1]]["last_change"])
                token.one_day_low = int(wtp_data[region[1]]["1_day_low"])
                token.one_day_high = int(wtp_data[region[1]]["1_day_high"])
                token.seven_day_high = int(wtp_data[region[1]]["7_day_high"])
                token.seven_day_low = int(wtp_data[region[1]]["7_day_low"])
                token.month_low = int(wtp_data[region[1]]["30_day_low"])
                token.month_high = int(wtp_data[region[1]]["30_day_high"])

                print("Получена информация о токене: {}".format(token))
                db.session.commit()

            self.reporter.wowtokenscan["number_of_cycles"] +=1
            self.reporter.wowtokenscan["work_time"] = str((datetime.datetime.now() - time_start))
            time.sleep(self.pause_time.total_seconds())
            if int(self.reporter.wowtokenscan["number_of_cycles"])%30 == 0:
                updateToken()
                self.token = getToken()["access_token"]
        self.reporter.wowtokenscan["isWork"] = False





