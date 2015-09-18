from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, collate
from database import WineType, WineColor, GlassType, WineCalories, WineABV
from database import Temperature
from flask import session as login_session
import datetime
from auth_api.auth_api import login_required

winetype_api = Blueprint('winetype_api', __name__)
template_prefix = "winetype/"


def get_form_values(request_obj, item=None):
        new_name = request_obj.form['itemname']
        new_color = request_obj.form.get('colorvalue', None)
        new_glass = request_obj.form.get('glassvalue', None)
        new_calorie = request_obj.form.get('calorievalue', None)
        new_abv = request_obj.form.get('abvvalue', None)
        new_temperature = request_obj.form.get('temperaturevalue', None)
        if item:
            item.name = new_name
            item.color_id = new_color
            item.glass_type_id = new_glass
            item.calorie_id = new_calorie
            item.abv_id = new_abv
            item.temperature_id = new_temperature
            item.user_id = login_session['user_id']
            item.date_edited = datetime.datetime.today()
        else:
            item = WineType(name=new_name,
                            color_id=new_color,
                            glass_type_id=new_glass,
                            calorie_id=new_calorie,
                            abv_id=new_abv,
                            temperature_id=new_temperature,
                            user_id=login_session['user_id'],
                            date_created=datetime.datetime.today())
        return item


@winetype_api.route('/')
@login_required
def show():
    session = current_app.config['db']
    winetypes = session\
        .query(WineType.id, WineType.name)\
        .order_by(asc(collate(WineType.name, 'NOCASE')))
    return render_template(template_prefix+'view.html', winetypes=winetypes)


@winetype_api.route('/new', methods=["GET", "POST"])
@login_required
def new():
    session = current_app.config['db']
    if request.method == "POST":
        item = get_form_values(request)
        try:
            session.add(item)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            winecolors = session\
                .query(WineColor)\
                .order_by(asc(collate(WineColor.name, 'NOCASE')))
            glasses = session\
                .query(GlassType)\
                .order_by(asc(collate(GlassType.name, 'NOCASE')))
            calories = session\
                .query(WineCalories)\
                .order_by(asc(collate(WineCalories.name, 'NOCASE')))
            abvs = session\
                .query(WineABV)\
                .order_by(asc(collate(WineABV.name, 'NOCASE')))
            temps = session\
                .query(Temperature)\
                .order_by(asc(collate(Temperature.temp, 'NOCASE')))
            return render_template(template_prefix+'/new_form.html',
                                   winetype=item,
                                   winecolors=winecolors,
                                   glasses=glasses,
                                   calories=calories,
                                   abvs=abvs,
                                   temps=temps)

        flash("Successfully Added '%s'" % (item.name,), 'success')
        return redirect(url_for('.show'))
    else:
        winetype = WineType(name="")
        winecolors = session\
            .query(WineColor)\
            .order_by(asc(collate(WineColor.name, 'NOCASE')))
        glasses = session\
            .query(GlassType)\
            .order_by(asc(collate(GlassType.name, 'NOCASE')))
        calories = session\
            .query(WineCalories)\
            .order_by(asc(collate(WineCalories.name, 'NOCASE')))
        abvs = session\
            .query(WineABV)\
            .order_by(asc(collate(WineABV.name, 'NOCASE')))
        temps = session\
            .query(Temperature)\
            .order_by(asc(collate(Temperature.temp, 'NOCASE')))
        return render_template(template_prefix+'new_form.html',
                               winetype=winetype,
                               winecolors=winecolors,
                               glasses=glasses,
                               calories=calories,
                               abvs=abvs,
                               temps=temps)


@winetype_api.route('/<int:item_id>/edit', methods=["GET", "POST"])
@login_required
def edit(item_id):
    session = current_app.config['db']
    item = session.query(WineType).filter_by(id=item_id).one()

    if item.user_id != login_session['user_id']:
        flash("You are not allowed to edit this wine type", 'danger')
        return redirect(url_for('winetype_api.show'))

    if request.method == "POST":
        item = get_form_values(request, item)
        try:
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            return render_template('edit_form.html', item=item)

        flash("Successfully Edited '%s'" % (item.name,), 'success')
        return redirect(url_for('.show'))
    else:
        winecolors = session.query(WineColor).order_by(
            asc(collate(WineColor.name, 'NOCASE')))
        glasses = session.query(GlassType).order_by(
            asc(collate(GlassType.name, 'NOCASE')))
        calories = session.query(WineCalories).order_by(
            asc(collate(WineCalories.name, 'NOCASE')))
        abvs = session.query(WineABV).order_by(
            asc(collate(WineABV.name, 'NOCASE')))
        temps = session.query(Temperature).order_by(
            asc(collate(Temperature.temp, 'NOCASE')))
        return render_template(template_prefix+'edit_form.html',
                               winetype=item,
                               winecolors=winecolors,
                               glasses=glasses,
                               calories=calories,
                               abvs=abvs,
                               temps=temps)


@winetype_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
@login_required
def delete(item_id):
    """
    Deletion of wine type is allowed. Caution thought that all the reviews
    will be deleted too
    """
    session = current_app.config['db']
    item = session.query(WineType).filter_by(id=item_id).one()

    if item.user_id != login_session['user_id']:
        flash("You are not allowed to delete this wine type", 'danger')
        return redirect(url_for('winetype_api.show'))

    if request.method == "POST":
        c_name = item.name
        session.delete(item)
        session.commit()
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = session.query(WineType).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
