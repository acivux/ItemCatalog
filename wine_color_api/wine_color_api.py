from flask import current_app, Blueprint, jsonify
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc, func, collate

from database import WineColor, WineType
from auth_api.auth_api import login_required, admin_required
from json_util import is_json_request

wine_color_api = Blueprint('wine_color_api', __name__)
template_prefix = "color/"


@wine_color_api.route('/view.json', methods=["GET"])
@wine_color_api.route('/view', methods=["GET"])
@login_required
@admin_required
def show():
    """
    Shows list of color available

    :return: JSON or HTML template
    """
    session = current_app.config['db']
    colors = session.query(WineColor).order_by(
        asc(collate(WineColor.name, 'NOCASE')))
    if is_json_request(request):
        return jsonify(items=[x.serialize for x in colors])
    else:
        return render_template(template_prefix+'view.html', colortypes=colors)


@wine_color_api.route('/new', methods=["GET", "POST"])
@login_required
@admin_required
def new():
    """
    Creates a new color. No duplicates Allowed

    :return: HTML page
    """
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['colorname']
        new_color = request.form['colorvalue']
        color = WineColor(name=new_name, value=new_color[1:].upper())
        try:
            session.add(color)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            return render_template(template_prefix+'/new_form.html', item=color)
        flash("Successfully Added Color '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        return render_template(template_prefix+'new_form.html')


@wine_color_api.route('/<int:color_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def edit(color_id):
    """
    Edit a color.

    :param color_id: Color id
    :return: HTML page
    """
    session = current_app.config['db']
    color = session.query(WineColor).filter_by(id=color_id).one()
    if request.method == "POST":
        new_name = request.form['colorname']
        new_color = request.form['colorvalue']
        color.name = new_name
        color.value = new_color[1:].upper()
        try:
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            flash("Duplicate values!", 'danger')
            return render_template(template_prefix+'/edit_form.html',
                                   item=color)
        flash("Successfully Edited Color '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        return render_template(template_prefix+'edit_form.html',
                               colortype=color)


@wine_color_api.route('/<int:color_id>/delete', methods=["GET", "POST"])
@login_required
@admin_required
def delete(color_id):
    """
    Deletes a color if not in use.

    :param color_id: Color id
    :return: HTML page
    """
    session = current_app.config['db']
    if request.method == "POST":
        used = session\
            .query(func.count(WineType.id).label('count'))\
            .filter_by(color_id=color_id)\
            .scalar()
        color = session.query(WineColor).filter_by(id=color_id).one()
        c_name = color.name
        if used == 0:
            session.delete(color)
            session.commit()
            flash("Successfully Deleted Color '%s'" % (c_name,), 'success')
        else:
            flash("'%s' color still in use and cannot be deleted." % (c_name,),
                  'danger')
        return redirect(url_for('.show'))
    else:
        color = session.query(WineColor).filter_by(id=color_id).one()
        return render_template(template_prefix+'delete_form.html',
                               colortype=color)
