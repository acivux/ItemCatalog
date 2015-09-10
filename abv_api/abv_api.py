from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc
from database import WineABV
from auth_api.auth_api import login_required, admin_required


abv_api = Blueprint('abv_api', __name__)
template_prefix = "abv/"


@abv_api.route('/')
@login_required
@admin_required
def show():
    session = current_app.config['db']
    items = session.query(WineABV).order_by(asc(WineABV.name))
    return render_template(template_prefix+'view.html', items=items)


@abv_api.route('/new', methods=["GET", "POST"])
@login_required
@admin_required
def new():
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['itemname']
        try:
            item = WineABV(name=new_name)
            session.add(item)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            item = WineABV(name=new_name)
            return render_template(template_prefix+'/new_form.html', item=item)

        flash("Successfully Added '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = WineABV(name="")
        return render_template(template_prefix+'new_form.html', item=item)


@abv_api.route('/<int:item_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def edit(item_id):
    session = current_app.config['db']
    item = session.query(WineABV).filter_by(id=item_id).one()
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


@abv_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
@login_required
@admin_required
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        item = session.query(WineABV).filter_by(id=item_id).one()
        c_name = item.name
        session.delete(item)
        session.commit()
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = session.query(WineABV).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
