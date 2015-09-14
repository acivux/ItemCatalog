from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, func
from database import WineCalories, WineType
from auth_api.auth_api import login_required, admin_required


calories_api = Blueprint('calories_api', __name__)
template_prefix = "calories/"


@calories_api.route('/')
@login_required
@admin_required
def show():
    session = current_app.config['db']
    items = session.query(WineCalories).order_by(asc(WineCalories.name))
    return render_template(template_prefix+'view.html', items=items)


@calories_api.route('/new', methods=["GET", "POST"])
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        used = session.query(func.count(WineType.id).label('count'))\
            .filter_by(calorie_id=item_id).scalar()
        item = session.query(WineCalories).filter_by(id=item_id).one()
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
        item = session.query(WineCalories).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
