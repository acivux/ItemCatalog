from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, func
from database import WineType, WineColor, GlassType, WineCalories, WineABV
from database import Temperature

winetype_api = Blueprint('winetype_api', __name__)
template_prefix = "winetype/"


def get_form_values(request, item=None):
        new_name = request.form['itemname']
        new_color = request.form.get('colorvalue', None)
        new_glass = request.form.get('glassvalue', None)
        new_calorie = request.form.get('calorievalue', None)
        new_abv = request.form.get('abvvalue', None)
        new_temperature = request.form.get('temperaturevalue', None)
        if item:
            item.name = new_name
            item.color_id = new_color
            item.glass_type_id = new_glass
            item.calorie_id = new_calorie
            item.abv_id = new_abv
            item.temperature_id = new_temperature
        else:
            item = WineType(name=new_name,
                            color_id=new_color,
                            glass_type_id=new_glass,
                            calorie_id=new_calorie,
                            abv_id=new_abv,
                            temperature_id=new_temperature)
        return item

@winetype_api.route('/')
def show():
    session = current_app.config['db']
    winetypes = session.query(WineType.id, WineType.name).group_by(WineType.name)
    return render_template(template_prefix+'view.html', winetypes=winetypes)


@winetype_api.route('/new', methods=["GET", "POST"])
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
            winecolors = session.query(WineColor).order_by(asc(WineColor.name))
            glasses = session.query(GlassType).order_by(asc(GlassType.name))
            calories = session.query(WineCalories).order_by(asc(WineCalories.name))
            abvs = session.query(WineABV).order_by(asc(WineABV.name))
            temps = session.query(Temperature).order_by(asc(Temperature.temp))
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
        winecolors = session.query(WineColor).order_by(asc(WineColor.name))
        glasses = session.query(GlassType).order_by(asc(GlassType.name))
        calories = session.query(WineCalories).order_by(asc(WineCalories.name))
        abvs = session.query(WineABV).order_by(asc(WineABV.name))
        temps = session.query(Temperature).order_by(asc(Temperature.temp))
        return render_template(template_prefix+'new_form.html',
                               winetype=winetype,
                               winecolors=winecolors,
                               glasses=glasses,
                               calories=calories,
                               abvs=abvs,
                               temps=temps)


@winetype_api.route('/<int:item_id>/edit', methods=["GET", "POST"])
def edit(item_id):
    session = current_app.config['db']
    item = session.query(WineType).filter_by(id=item_id).one()
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
        winecolors = session.query(WineColor).order_by(asc(WineColor.name))
        glasses = session.query(GlassType).order_by(asc(GlassType.name))
        calories = session.query(WineCalories).order_by(asc(WineCalories.name))
        abvs = session.query(WineABV).order_by(asc(WineABV.name))
        temps = session.query(Temperature).order_by(asc(Temperature.temp))
        return render_template(template_prefix+'edit_form.html',
                               winetype=item,
                               winecolors=winecolors,
                               glasses=glasses,
                               calories=calories,
                               abvs=abvs,
                               temps=temps)


@winetype_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        item = session.query(WineType).filter_by(id=item_id).one()
        c_name = item.name
        session.delete(item)
        session.commit()
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = session.query(WineType).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
