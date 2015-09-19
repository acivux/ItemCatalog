from flask import current_app, Blueprint, jsonify
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, func, collate
from database import WineColor, WineType
from auth_api.auth_api import login_required, admin_required
from json_util import is_json_request

wine_color_api = Blueprint('wine_color_api', __name__)
template_prefix = "color/"


@wine_color_api.route('.json')
@wine_color_api.route('/')
@login_required
@admin_required
def show():
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
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['colorname']
        new_color = request.form['colorvalue']
        color = WineColor(name=new_name, value=new_color[1:].upper())
        session.add(color)
        session.commit()
        flash("Successfully Added Color '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        return render_template(template_prefix+'new_form.html')


@wine_color_api.route('/<int:color_id>/edit.json')
@wine_color_api.route('/<int:color_id>/edit', methods=["GET", "POST"])
@login_required
@admin_required
def edit(color_id):
    session = current_app.config['db']
    color = session.query(WineColor).filter_by(id=color_id).one()
    if request.method == "POST":
        new_name = request.form['colorname']
        new_color = request.form['colorvalue']
        color.name = new_name
        color.value = new_color[1:].upper()
        session.commit()
        flash("Successfully Edited Color '%s'" % (new_name,), 'success')
        return redirect(url_for('.show'))
    else:
        if is_json_request(request):
            return jsonify(color.serialize)
        else:
            return render_template(template_prefix+'edit_form.html',
                                   colortype=color)


@wine_color_api.route('/<int:color_id>/delete', methods=["GET", "POST"])
@login_required
@admin_required
def delete(color_id):
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
