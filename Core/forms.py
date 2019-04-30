from flask_wtf import FlaskForm
from flask import flash
from wtforms import PasswordField, SubmitField, StringField, BooleanField, HiddenField, IntegerField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, ValidationError
import requests

class PasswordForm(FlaskForm):
    user = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    form_type = HiddenField(default="client_form")
    submit = SubmitField("Войти")

class ClientForm(FlaskForm):
    id = StringField("client_id:", validators=[DataRequired()])
    secret = StringField("client_secret:", validators=[DataRequired()])
    form_type = HiddenField(default="client_form")
    submit = SubmitField("Обновить")

    def validate_form(self, id, secret):
        auth = (str(id), str(secret))
        token_data = requests.post("https://eu.battle.net/oauth/token", auth=auth,
                                   data={"grant_type": "client_credentials"}).json()
        print(token_data)
        if "access_token" not in token_data:
            flash("Проверьте secret пару.")
            return False
        else:
            return True


class ItemForm(FlaskForm):
    maxItemId = IntegerField("maxItemId:",default=300000, widget=NumberInput(), validators=[DataRequired()])
    minItemId = IntegerField("minItemId:",default=1,widget=NumberInput(),validators=[DataRequired()])
    countOfThreads = IntegerField("countOfThreads:",default=16,widget=NumberInput(), validators=[DataRequired()])
    startFromLast = BooleanField("startFromLast", default=True)
    form_type = HiddenField(default="item_form")
    submit = SubmitField("Начать скан")



class ServerForm(FlaskForm):

    countOfThreads = IntegerField("countOfThreads:", default=12,widget=NumberInput(), validators=[DataRequired()])
    form_type = HiddenField(default="server_form")
    submit = SubmitField("Начать скан")


class PetForm(FlaskForm):
    countOfThreads = IntegerField("countOfThreads:", default=12,widget=NumberInput(), validators=[DataRequired()])
    form_type = HiddenField(default="pet_form")
    submit = SubmitField("Начать скан")



