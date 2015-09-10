from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc
from database import WineColor
from auth_api.auth_api import login_required, admin_required

wine_color_api = Blueprint('wine_color_api', __name__)
template_prefix = "color/"

@wine_color_api.route('/')
@login_required
@admin_required
def show():
    session = current_app.config['db']
    colors = session.query(WineColor).order_by(asc(WineColor.name))
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
        return render_template(template_prefix+'edit_form.html', colortype=color)


@wine_color_api.route('/<int:color_id>/delete', methods=["GET", "POST"])
@login_required
@admin_required
def delete(color_id):
    session = current_app.config['db']
    if request.method == "POST":
        color = session.query(WineColor).filter_by(id=color_id).one()
        c_name = color.name
        session.delete(color)
        session.commit()
        flash("Successfully Deleted Color '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        color = session.query(WineColor).filter_by(id=color_id).one()
        return render_template(template_prefix+'delete_form.html', colortype=color)
