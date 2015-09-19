from flask import current_app, Blueprint, jsonify
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, func, collate

from database import Temperature, WineType
from auth_api.auth_api import login_required, admin_required
from json_util import is_json_request

temperature_api = Blueprint('temperature_api', __name__)
template_prefix = "temperature/"


@temperature_api.route('/view.json', methods=["GET"])
@temperature_api.route('/view', methods=["GET"])
@login_required
@admin_required
def show():
    session = current_app.config['db']
    items = session\
        .query(Temperature)\
        .order_by(asc(collate(Temperature.temp, 'NOCASE')))
    if is_json_request(request):
        return jsonify(items=[x.serialize for x in items])
    else:
        return render_template(template_prefix+'view.html', items=items)


@temperature_api.route('/new', methods=["GET", "POST"])
@login_required
@admin_required
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
@login_required
@admin_required
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
        if is_json_request(request):
            return jsonify(item.serialize)
        else:
            return render_template(template_prefix+'edit_form.html', item=item)


@temperature_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
@login_required
@admin_required
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        used = session.query(func.count(WineType.id).label('count'))\
            .filter_by(temperature_id=item_id).scalar()
        item = session.query(Temperature).filter_by(id=item_id).one()
        c_name = item.name
        if used == 0:
            session.delete(item)
            session.commit()
            flash("Successfully Deleted '%s'" % (c_name,), 'success')
        else:
            flash("'%s' is still in use and cannot be deleted." % (c_name,),
                  'danger')
        return redirect(url_for('.show'))
    else:
        item = session.query(Temperature).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
