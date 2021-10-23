from datetime import date, time, timedelta

from flask_wtf import FlaskForm
from wtforms import TimeField, DateField, IntegerField, SelectField, ValidationError, StringField, SubmitField
from wtforms.validators import DataRequired, Regexp
from wtforms_components import widgets

from app_dir.app.models import Table

MAX_DAYS_FOR_BOOKING = 4
OPENING_TIME = time(hour=9)
STOP_BOOKING_TIME = time(hour=20)
POSSIBLE_VISIT_DURATION = (
    (time(hour=1), '1 час'),
    (time(hour=1, minute=30), '1 час 30 минут'),
    (time(hour=2), '2 часа'),
    (time(hour=2, minute=30), '2 часа 30 минут'),
    (time(hour=3), '3 часа'),
    (time(hour=3, minute=30), '3 часа 30 минут',),
    (time(hour=4), '4 часа'),
)
DATA_REQUIRED_MESSAGE = 'Данное поле необходимо заполнить!'


class OnlyDate(FlaskForm):
    date = DateField('Дата', validators=[DataRequired(message=DATA_REQUIRED_MESSAGE)], widget=widgets.DateInput())

    def validate_date(form, field):
        if field.data < date.today():
            raise ValidationError(
                'Недопустимая дата бронирования! Невозможно совершить бронь на дату раньше сегодняшней')
        if field.data > date.today() + timedelta(days=MAX_DAYS_FOR_BOOKING):
            raise ValidationError(
                f'Недопустимая дата бронирования! Невозможно совершить бронь более чем на {MAX_DAYS_FOR_BOOKING} дня вперед')


class NewBookingFormWithoutDate(FlaskForm):
    time = TimeField('Время', validators=[DataRequired(message=DATA_REQUIRED_MESSAGE)], widget=widgets.TimeInput(),
                     description='Количество минут должно быть кратно 15',
                     render_kw={'placeholder': 'Количество минут должно быть кратно 15'})
    num_guests = IntegerField('Количество гостей', validators=[DataRequired(message=DATA_REQUIRED_MESSAGE)])
    duration = SelectField('Продолжительность визита', choices=POSSIBLE_VISIT_DURATION, default='2 часа')
    submit = SubmitField('Продолжить')

    def validate_num_guests(form, field):
        if field.data <= 0:
            raise ValidationError('Число гостей не может быть неположительным')

    def validate_time(form, field):
        # if field.data > (datetime.now() + timedelta(minutes=30)).time():
        #     raise ValidationError(
        #         'Недопустимое время бронирования! Невозможно совершить бронь менее чем за полчаса от текущего времени')
        if not OPENING_TIME <= field.data <= STOP_BOOKING_TIME:
            raise ValidationError(
                'Недопустимое время бронирования! Невозможно совершить бронь ранее открытия ресторана и менее чем за час до закрытия')
        if field.data.minute % 15 != 0:
            raise ValidationError('Недопустимое время бронирования! Количество минут должно быть кратно 15')


class NewBookingFormWithDate(NewBookingFormWithoutDate, OnlyDate):
    pass


class DateTableForm(OnlyDate):
    table = SelectField('Номер столика', choices=[(table.id, f'{table.id}') for table in Table.get_all()])
    submit = SubmitField('Продолжить')


class NewGuest(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(message=DATA_REQUIRED_MESSAGE)])
    phone_number = StringField('Номер телефона',
                               validators=[DataRequired(message=DATA_REQUIRED_MESSAGE), Regexp('^(?:\+38)?0[0-9]{9}$')],
                               render_kw={'placeholder': '+380XXXXXXXXX'})
    submit = SubmitField('Продолжить')
