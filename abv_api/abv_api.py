from flask import current_app, Blueprint, jsonify
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, func, collate

from database import WineABV, WineType
from auth_api.auth_api import login_required, admin_required
from json_util import is_json_request

abv_api = Blueprint('abv_api', __name__)
template_prefix = "abv/"


@abv_api.route('/view.json', methods=["GET"])
@abv_api.route('/view', methods=["GET"])
@login_required
@admin_required
def show():
    """
    Entry point for ABV

    :return: JSON or HTML template
    """
    session = current_app.config['db']
    items = session\
        .query(WineABV)\
        .order_by(asc(collate(WineABV.name, 'NOCASE')))
    if is_json_request(request):
        return jsonify(items=[x.serialize for x in items])
    else:
        return render_template(template_prefix+'view.html', items=items)


@abv_api.route('/new', methods=["GET", "POST"])
@login_required
@admin_required
def new():
    """
    Create a new ABV item

    :return: HTML page
    """
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
    """
    Edit an ABV item

    :param item_id: ABV id to edit
    :return: HTML page
    """
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
    """
    Delete an ABV item

    :param item_id: ABV id to edit
    :return: HTML page
    """
    session = current_app.config['db']
    if request.method == "POST":
        used = session.query(func.count(WineType.id).label('count'))\
            .filter_by(abv_id=item_id).scalar()
        item = session.query(WineABV).filter_by(id=item_id).one()
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
        item = session.query(WineABV).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
