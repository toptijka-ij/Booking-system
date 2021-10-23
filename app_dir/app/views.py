from datetime import datetime

from flask import render_template, request, redirect, url_for, session, flash

from . import app
from .forms import NewBookingFormWithDate, NewBookingFormWithoutDate, NewGuest, DateTableForm
from .models import Booking, Guest, Table
from .utilities import from_str_to_timedelta


@app.route('/')
def home():
    return render_template('etc/home.html')


@app.route('/time_booking/enter_time', methods=['GET', 'POST'])
def datetime_people_duration_form():
    form = NewBookingFormWithDate()
    if request.method == 'POST':
        if form.validate_on_submit():
            session['booking_data'] = {
                'start_datetime': datetime.strptime(request.form['date'] + ' ' + request.form['time'],
                                                    '%Y-%m-%d %H:%M'),
                'duration': request.form['duration'],
                'num_guests': request.form['num_guests'],
            }
            return redirect(url_for('choose_filter_table'))
        else:
            flash('Данные не валидны', 'error')
            return render_template('booking/datetime_peoplenum_duration_form.html', form=form)
    else:
        return render_template('booking/datetime_peoplenum_duration_form.html', form=form)


@app.route('/time_booking/choose_table', methods=['GET', 'POST'])
def choose_filter_table():
    if request.method == 'POST':
        session['booking_data'] = session.get('booking_data') | {'table': request.form['table']}
        return redirect(url_for('guest_data_form'))
    else:
        free_tables = Table.filter(num_guests=session['booking_data']['num_guests'],
                                   start_datetime=session['booking_data']['start_datetime'],
                                   duration=from_str_to_timedelta(session['booking_data']['duration']))

        return render_template('booking/map_tables.html', free_tables=free_tables)


@app.route('/table_booking/choose_table', methods=['GET', 'POST'])
def choose_date_table():
    form = DateTableForm()
    if request.method == 'POST':
        session['booking_data'] = {'table': request.form['table'],
                                   'date': datetime.strptime(request.form['date'], '%Y-%m-%d')}
        return redirect(url_for('time_people_duration_form'))
    else:
        return render_template('booking/map_tables_date.html', form=form)


@app.route('/table_booking/enter_time', methods=['GET', 'POST'])
def time_people_duration_form():
    form = NewBookingFormWithoutDate()
    booking_data = session.get('booking_data')
    info = Table.get_by_id(table_id=booking_data['table']).get_info_with_date(date=booking_data['date'].date())
    if request.method == 'POST':
        if form.validate_on_submit():
            num_guests = request.form['num_guests']
            start_datetime = datetime.combine(booking_data['date'].date(),
                                              datetime.strptime(request.form['time'], '%H:%M').time())
            duration = request.form['duration']
            free_tables = Table.filter(num_guests=num_guests,
                                       start_datetime=start_datetime,
                                       duration=from_str_to_timedelta(duration))
            if Table.get_by_id(booking_data['table']) in free_tables:
                session['booking_data'] = {'start_datetime': start_datetime,
                                           'duration': duration,
                                           'num_guests': num_guests,
                                           'table': booking_data['table']}
                return redirect(url_for('guest_data_form'))
            else:
                flash('К сожалению, мы не можем зарегистрировать бронь в соответствии с вашими данными. '
                      'Пожалуйста, проверьте ещё раз введенные данные.', 'error')
        else:
            flash('Данные не валидны', 'error')
        return render_template('booking/time_peoplenum_duration_form.html', form=form, info=info)
    else:
        return render_template('booking/time_peoplenum_duration_form.html', form=form, info=info)


@app.route('/booking/enter_guest_data', methods=['GET', 'POST'])
def guest_data_form():
    form = NewGuest()
    if request.method == 'POST':
        if form.validate_on_submit():
            session['booking_data'] = session.get('booking_data') | {'name': request.form['name']} | {
                'phone_number': request.form['phone_number']}
            return redirect(url_for('booking_confirmation'))
        else:
            flash('Данные не валидны', 'error')
            return render_template('booking/guest_form.html', form=form)
    else:
        return render_template('booking/guest_form.html', form=form)


@app.route('/booking_confirmation', methods=['GET', 'POST'])
def booking_confirmation():
    booking_data = dict(reversed(list(session['booking_data'].items())))
    labels = ('Номер столика', 'Дата и время визита', 'Номер телефона', 'Количество гостей',
              'Столик заказан на имя', 'Продолжительность визита')
    if request.method == 'POST':
        new_guest = Guest.add_guest(booking_data['name'], booking_data['phone_number'])
        del booking_data['name'], booking_data['phone_number']
        booking_data['guest'] = new_guest
        booking_data['duration'] = from_str_to_timedelta(booking_data['duration'])
        Booking.add_booking(**booking_data)
        del session['booking_data']
        return render_template('booking/success_booking.html')
    else:
        booking_data = zip(labels, booking_data.values())
        return render_template('booking/booking_confirmation.html', booking_data=booking_data, labels=labels)

#
# @app.errorhandler(400)
# def page_not_found():
#     return render_template('errors/400.html'), 400
#
#
# @app.errorhandler(404)
# def page_not_found():
#     return render_template('errors/404.html'), 404
#
#
# @app.errorhandler(500)
# def page_not_found():
#     return render_template('errors/500.html'), 500
