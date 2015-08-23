from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc
from database import Temperature
from sqlite3 import IntegrityError

temperature_api = Blueprint('temperature_api', __name__)
template_prefix = "temperature/"

@temperature_api.route('/')
def show():
    session = current_app.config['db']
    items = session.query(Temperature).order_by(asc(Temperature.temp))
    return render_template(template_prefix+'view.html', items=items)


@temperature_api.route('/new', methods=["GET", "POST"])
def new():
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['itemname']
        new_value = request.form['itemvalue']
        try:
            item = Temperature(name=new_name, temp=new_value)
            session.add(item)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            item = Temperature(name=new_name, temp=new_value)
            return render_template(template_prefix+'/new_form.html', item=item)

        flash("Successfully Added '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = Temperature(name="", temp=32)
        return render_template(template_prefix+'new_form.html', item=item)


@temperature_api.route('/<int:item_id>/edit', methods=["GET", "POST"])
def edit(item_id):
    session = current_app.config['db']
    item = session.query(Temperature).filter_by(id=item_id).one()
    if request.method == "POST":
        new_name = request.form['itemname']
        new_value = request.form['itemvalue']
        item.name = new_name
        item.temp = new_value
        try:
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            return render_template('edit_form.html', item=item)

        flash("Successfully Edited '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        return render_template(template_prefix+'edit_form.html', item=item)


@temperature_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        item = session.query(Temperature).filter_by(id=item_id).one()
        c_name = item.name
        session.delete(item)
        session.commit()
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = session.query(Temperature).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
