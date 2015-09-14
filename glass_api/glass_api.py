from utils import make_safe_filename
import os
from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, func
from database import GlassType, WineType
from auth_api.auth_api import login_required, admin_required


glass_api = Blueprint('glass_api', __name__)
template_prefix = "glass/"


@glass_api.route('/')
@login_required
@admin_required
def show():
    session = current_app.config['db']
    items = session.query(GlassType).order_by(asc(GlassType.name))
    return render_template(template_prefix+'view.html', items=items)


@glass_api.route('/new', methods=["GET", "POST"])
@login_required
@admin_required
def new():
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['itemname']
        try:
            item = GlassType(name=new_name)
            session.add(item)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            item = GlassType(name=new_name)
            return render_template(template_prefix+'/new_form.html', item=item)

        flash("Successfully Added '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = GlassType(name="")
        return render_template(template_prefix+'new_form.html', item=item)


@glass_api.route('/<int:item_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def edit(item_id):
    session = current_app.config['db']
    item = session.query(GlassType).filter_by(id=item_id).one()
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
        glass_url = None
        return render_template(template_prefix+'edit_form.html',
                               item=item,
                               glass_url=glass_url)


@glass_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
@login_required
@admin_required
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        used = session.query(func.count(WineType.id).label('count'))\
            .filter_by(glass_type_id=item_id).scalar()
        item = session.query(GlassType).filter_by(id=item_id).one()
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
        item = session.query(GlassType).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
