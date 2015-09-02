from utils import make_safe_filename
import os
from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, exc
from database import GlassType
from flaskext.uploads import UploadSet, IMAGES


glass_api = Blueprint('glass_api', __name__)
template_prefix = "glass/"

glassphotos = UploadSet('glassphotos', IMAGES)


@glass_api.route('/')
def show():
    session = current_app.config['db']
    items = session.query(GlassType).order_by(asc(GlassType.name))
    return render_template(template_prefix+'view.html', items=items)


@glass_api.route('/new', methods=["GET", "POST"])
def new():
    session = current_app.config['db']
    if request.method == "POST":
        new_name = request.form['itemname']
        try:
            glassimagefilename = None
            if 'filename' in request.files:
                glassimagefilename = glassphotos.save(
                    request.files['filename'],
                    name=make_safe_filename(request.files['filename'].filename))
            item = GlassType(name=new_name, filename=glassimagefilename)
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
def edit(item_id):
    session = current_app.config['db']
    item = session.query(GlassType).filter_by(id=item_id).one()
    if request.method == "POST":
        new_name = request.form['itemname']
        item.name = new_name
        if 'filename' in request.files:
            item.filename = glassphotos.save(
                request.files['filename'],
                name=make_safe_filename(request.files['filename'].filename))
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
        if item.filename:
            glass_url = glassphotos.url(item.filename)
        return render_template(template_prefix+'edit_form.html',
                               item=item,
                               glass_url=glass_url)


@glass_api.route('/<int:item_id>/delete', methods=["GET", "POST"])
def delete(item_id):
    session = current_app.config['db']
    if request.method == "POST":
        item = session.query(GlassType).filter_by(id=item_id).one()
        c_name = item.name
        session.delete(item)
        session.commit()
        if item.filename:
            os.remove(glassphotos.path(item.filename))
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        item = session.query(GlassType).filter_by(id=item_id).one()
        return render_template(template_prefix+'delete_form.html', item=item)
