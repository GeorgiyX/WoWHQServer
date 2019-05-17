from Core import app
from flask import render_template, flash, redirect, request, jsonify

from Core.Scaners.AuctionScaner import AuctionsScaner
from Core.Scaners.WoWTokenScaner import WoWTokenScaner
from Core.forms import PasswordForm, ClientForm, ServerForm, ItemForm, PetForm, AucForm, WoWTokenForm
from Core.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from Core.Utilites.AccessToken import updateClientValues, getToken, getClientValues
from Core.Utilites.Utilites import Reporter, ThreadStopper
from Core.Scaners.ServerScaner import ServerScaner
from Core.Scaners.ItemsScaner import ItemScaner
from Core.Scaners.PetsScaner import PetScaner
from Core.API.ToDict import GetDict
import json

stopper = ThreadStopper()
reporter = Reporter()

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/dashbord")
    else:
        form = PasswordForm()
        #тут должно быть разделение на GET и POST, а шаблон обрабатывать залогинен ли пользователь
        if form.validate_on_submit():
            user = User.query.filter_by(username = form.user.data).first()
            if user is None or user.check_password(form.password.data) is not True:
                flash("Введеные данные неверны")
                return redirect("/login")
            else:
                login_user(user, False)
                next_page = request.args.get("next")
                if next_page is None or url_parse(next_page).netloc is not "":
                    return redirect("/dashbord")
                else:
                    return redirect(next_page)
        else:
            return render_template("login_page.html", form = form, title = "Login")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/", methods = ["GET", "POST"])
@app.route("/dashbord", methods = ["GET", "POST"])
@login_required
def dashbord():
    client_form =  ClientForm()
    server_form = ServerForm()
    item_form = ItemForm()
    pet_form = PetForm()
    auc_form = AucForm()
    wowtoken_form = WoWTokenForm()

    if stopper.is_server_thread_must_stop is False:
        server_form.submit.label.text = "Выключить"
    if stopper.is_item_thread_must_stop is False:
        item_form.submit.label.text = "Выключить"
    if stopper.is_pet_thread_must_stop is False:
        pet_form.submit.label.text = "Выключить"
    if stopper.is_auc_thread_must_stop is False:
        auc_form.submit.label.text = "Выключить"
    if stopper.is_wowtoken_thread_must_stop is False:
        wowtoken_form.submit.label.text = "Выключить"

    if request.method == "POST":
        print("In post!")
        print(request.form["form_type"])

        if request.form["form_type"] == "client_form":
            if client_form.validate_on_submit() and client_form.validate_form(client_form.id.data, client_form.secret.data):
                updateClientValues(client_form.id.data, client_form.secret.data)
                flash("Client обновлен")
                return redirect("/dashbord")

        elif request.form["form_type"] == "server_form":
            if server_form.validate_on_submit():
                if reporter.serverscan["isWork"] is False:
                    stopper.is_server_thread_must_stop = False
                    server_therad = ServerScaner(reporter, stopper, countOfThreads=server_form.countOfThreads.data)
                    server_therad.start()
                    flash("Скан серверов запущен!")
                    return redirect("/dashbord")
                else:
                    stopper.is_server_thread_must_stop = True
                    flash("Скан серверов остановлен!")
                    return redirect("/dashbord")

        elif request.form["form_type"] == "item_form":
            if item_form.validate_on_submit():
                if reporter.itemscan["isWork"] is False:
                    count_of_threads = item_form.countOfThreads.data
                    if count_of_threads > 60:
                        count_of_threads = 60
                        flash("Количество потоков снижено до {}!".format(count_of_threads))
                    stopper.is_item_thread_must_stop = False
                    item_therad = ItemScaner(reporter, stopper, maxItemId=item_form.maxItemId.data, minItemId=item_form.minItemId.data,countOfThreads=count_of_threads, startFromLast=item_form.startFromLast.data)
                    item_form.t = True
                    item_therad.start()
                    flash("Скан предметов запущен!")
                    return redirect("/dashbord")
                else:
                    stopper.is_item_thread_must_stop = True
                    item_form.t = False
                    flash("Скан предметов остановлен!")
                    return redirect("/dashbord")

        elif request.form["form_type"] == "pet_form":
            if pet_form.validate_on_submit():
                if reporter.petscan["isWork"] == False:
                    stopper.is_pet_thread_must_stop = False
                    pet_thread = PetScaner(reporter=reporter,stopper=stopper,countOfThreads=pet_form.countOfThreads.data)
                    pet_thread.start()
                    flash("Скан петов запущен!")
                    return redirect("/dashbord")
                else:
                    stopper.is_pet_thread_must_stop = True
                    flash("Скан петов остановлен!")
                    return redirect("/dashbord")

        elif request.form["form_type"] == "auc_form":
            if auc_form.validate_on_submit():
                if reporter.aucscan["isWork"] == False:
                    stopper.is_auc_thread_must_stop = False

                    if auc_form.is_limit.data is True:
                        lot_limit = int(auc_form.lot_limit.data)
                    else:
                        lot_limit = None

                    auc_thread = AuctionsScaner(reporter=reporter,stopper=stopper,countOfThreads=auc_form.countOfThreads.data, lot_limit=lot_limit, cycle_time=auc_form.cycle_time.data)
                    auc_thread.start()
                    flash("Запущен скан аукционов!")
                    return redirect("/dashbord")
                else:
                    stopper.is_auc_thread_must_stop = True
                    flash("Запущен процесс остановки скана аукционов!")
                    return redirect("/dashbord")

        elif request.form["form_type"] == "wowtoken_form":
            if wowtoken_form.validate_on_submit():
                if reporter.wowtokenscan["isWork"] == False:
                    stopper.is_wowtoken_thread_must_stop = False
                    wowtoken_thread = WoWTokenScaner(reporter = reporter, stopper = stopper, pause_time=wowtoken_form.pause_time.data)
                    wowtoken_thread.start()
                    flash("WoWToken сканируется..")
                    return redirect("/dashbord")
                else:
                    stopper.is_wowtoken_thread_must_stop = True
                    flash("Запущен процесс остановки скана WoWToken!")
                    return redirect("/dashbord")


    return render_template("dashbord_page.html", title = "Dashbord", client = {"client_form":client_form, "token" : getToken(), "client":getClientValues()},
                            server = {"server_form":server_form, "reporter": reporter.serverscan},
                            items = {"item_form":item_form, "reporter": reporter.itemscan},
                            pet = {"pet_form":pet_form, "reporter":reporter.petscan},
                            auc = {"auc_form": auc_form, "reporter": reporter.aucscan},
                            wowtoken = {"wowtoken_form": wowtoken_form, "reporter": reporter.wowtokenscan})


@app.route("/api/", methods = ["GET"])
def root():
    return json.dumps({"name":"hi!!! its wowhqAPI"}, ensure_ascii=False)

@app.route("/api/cls_spec/<string:lang>",  methods = ["GET"])
def cls_spec(lang):
    # return jsonify(getClassSpecDict(lang))
    return json.dumps(GetDict.getClassSpecDict(lang), ensure_ascii=False,indent=4)

@app.route("/api/talents/<int:cls>/<int:spec>/<string:lang>",  methods = ["GET"])
def talents(cls,spec, lang):
    # return jsonify(getClassSpecDict(lang))
    return json.dumps(GetDict.getTalent(cls=cls, spec=spec, lang=lang), ensure_ascii=False,indent=4)

@app.route("/api/allauc/<string:slug>/<string:region>/<string:lang>/<int:page>",  methods = ["GET"])
def allAuctions(slug, region, lang, page):
    return json.dumps(GetDict.getAuctionsAll(slug=slug, region = region, lang=lang, page=page), ensure_ascii=False,indent=4)

@app.route("/api/<string:type>/<string:name>/<string:lang>",  methods = ["GET"])
def oneItemOrPet(type, name, lang):
    return json.dumps(GetDict.getOneItemOrPetOrNone(type=type, name=name, lang=lang), ensure_ascii=False,indent=4)

@app.route("/api/bestaucs/<string:lang>",  methods = ["POST"])
def dealsAuctions(lang):
    return json.dumps(GetDict.getDeals(lang=lang, json= request.json), ensure_ascii=False,indent=4)

@app.route("/api/classes/<string:lang>",  methods = ["GET"])
def getClasses(lang):
    return json.dumps(GetDict.getClasses(lang=lang), ensure_ascii=False,indent=4)

@app.route("/api/specs/<string:lang>",  methods = ["GET"])
def getSpecs(lang):
    return json.dumps(GetDict.getSpecs(lang=lang), ensure_ascii=False,indent=4)

@app.route("/api/wowtoken/<string:region>",  methods = ["GET"])
def getWoWToken(region):
    return json.dumps(GetDict.getMinMaxCurrentWoWToken(region=region), ensure_ascii=False,indent=4)