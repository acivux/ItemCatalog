from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc
from database import WineCalories


calories_api = Blueprint('calories_api', __name__)
template_prefix = "calories/"


@calories_api.route('/')
def show():
    session = current_app.config['db']
    items = session.query(WineCalories).order_by(asc(WineCalories.name))
    return render_template(template_prefix+'view.html', items=items)


@calories_api.route('/new', methods=["GET", "POST"])
def new():
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['itemname']
        try:
            item = WineCalories(name=new_name)
            session.add(item)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            item = WineCalories(name=new_name)
            return render_template(template_prefix+'/new_form.html', item=item)

        flash("Successfully Added '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = WineCalories(name="")
        return render_template(template_prefix+'new_form.html', item=item)


@calories_api.route('/<int:item_id>/edit', methods=["GET", "POST"])
def edit(item_id):
    session = current_app.config['db']
    item = session.query(WineCalories).filter_by(id=item_id).one()
    if request.method == "POST":
        new_name = request.form['itemname']
        item.name = new_name
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


@calories_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        item = session.query(WineCalories).filter_by(id=item_id).one()
        c_name = item.name
        session.delete(item)
        session.commit()
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = session.query(WineCalories).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
