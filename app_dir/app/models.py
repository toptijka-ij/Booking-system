from sqlalchemy.exc import SQLAlchemyError

from . import db
from .utilities import datetime_list_to_dict, TimeRange, are_ranges_intersect_list


class AddError(SQLAlchemyError):
    pass


# class Waiter(db.Model):
#     __tablename__ = 'waiter'
#
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     tables = db.relationship('Table', backref='tables')
#
#     def add_table(self, table_id):
#         table = Table.query.filter_by(id=table_id).first()
#         table.set_waiter(self)


class Table(db.Model):
    __tablename__ = 'table'

    id = db.Column(db.Integer(), primary_key=True)
    max_guests = db.Column(db.Integer(), nullable=False)
    # waiter = db.Column(db.Integer(), db.ForeignKey('waiter.id'))
    bookings = db.relationship('Booking', backref='bookings')

    # @property
    # def is_visible(self):
    #     return

    # def set_waiter(self, waiter):
    #     self.waiter = waiter

    # def __str__(self):
    #     return f'Table №{self.id}'

    def get_all_busy_time(self):
        return datetime_list_to_dict([(booking.start_datetime, booking.finish_datetime) for booking in self.bookings])

    @staticmethod
    def get_by_id(table_id):
        return Table.query.filter_by(id=table_id).first()

    @staticmethod
    def get_all():
        return Table.query.all()

    @staticmethod
    def filter(num_guests, start_datetime, duration):
        # столики, на которые можно усадить необходимое кол-во гостей
        tables = Table.query.filter(Table.max_guests >= num_guests).order_by(Table.max_guests).all()
        free_tables = []
        # проверяем временные слоты для каждого столика
        for table in tables:
            # преобразуем список в словарь формата ключ-дата: список забронированных слотов времени
            datetime_dict = table.get_all_busy_time()
            # выбираем нужную дату
            time_list = datetime_dict.get(start_datetime.date(), [])
            # формируем промежуток для проверки
            time_range = TimeRange(start=start_datetime.time(), finish=(start_datetime + duration).time())
            # если необходимый промежуток НЕ пересекается с какой-то бронью, тогда рассматриваемый столик свободен
            if not are_ranges_intersect_list(time_range, time_list):
                free_tables.append(table)
        return free_tables

    def get_info_with_date(self, date):
        datetime_dict = self.get_all_busy_time()
        time_list = datetime_dict.get(date, [])
        return {
            'max_guests': self.max_guests,
            'busy_time': time_list
        }


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer(), primary_key=True)
    num_guests = db.Column(db.Integer(), nullable=False)
    table = db.Column(db.Integer(), db.ForeignKey('table.id'))
    guest = db.Column(db.Integer(), db.ForeignKey('guest.id'))
    start_datetime = db.Column(db.DateTime(), nullable=False)
    finish_datetime = db.Column(db.DateTime(), nullable=False)

    @property
    def duration(self):
        return self.finish_datetime - self.start_datetime

    @staticmethod
    def add_booking(num_guests, table, guest, start_datetime, duration):
        try:
            booking = Booking(num_guests=num_guests, table=table, guest=guest.id,
                              start_datetime=start_datetime, finish_datetime=start_datetime + duration)
            db.session.add(booking)
            db.session.commit()
        except:
            raise AddError


class Guest(db.Model):
    __tablename__ = 'guest'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(13), nullable=False, unique=True)
    booking = db.relationship('Booking', backref='booking', uselist=False)

    @staticmethod
    def add_guest(name, phone_number):
        if phone_number[0] == '0':
            phone_number = '+38' + phone_number
        try:
            guest = Guest.query.filter_by(phone_number=phone_number).first()
            if guest is None:
                guest = Guest(name=name, phone_number=phone_number)
                db.session.add(guest)
                db.session.commit()
            return guest
        except:
            raise AddError
