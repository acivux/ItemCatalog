from flask import current_app, Blueprint
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, desc, func, collate
from database import WineBrand, WineType, UserReview
from flask import session as login_session
import datetime
from flaskext.uploads import UploadSet, IMAGES
from utils import make_safe_filename
from auth_api.auth_api import login_required
import os

winebrand_api = Blueprint('winebrand_api', __name__)
template_prefix = "winebrand/"

brandphotos = UploadSet('brandphotos', IMAGES)


@winebrand_api.route('/')
def show():
    session = current_app.config['db']
    wines = session\
        .query(WineType, func.count(WineBrand.id))\
        .join(WineBrand)\
        .group_by(WineType.name)\
        .order_by(asc(collate(WineType.name, 'NOCASE')))
    return render_template(template_prefix+'topview.html', wines=wines)


@winebrand_api.route('/<int:winetype_id>/', methods=["GET"])
def show_brand(winetype_id):
    session = current_app.config['db']

    winetype = session.query(WineType).filter_by(id=winetype_id).one()

    counter = session\
        .query(UserReview.winebrand_id,
               UserReview.rating,
               func.count(UserReview.rating).label('count'))\
        .join(WineBrand)\
        .join(WineType)\
        .filter(WineBrand.winetype_id == winetype_id)\
        .group_by(WineBrand.id, UserReview.rating)\
        .order_by(UserReview.winebrand_id, desc('count'))\
        .subquery()

    maxer = session\
        .query(counter.c.winebrand_id,
               func.max(counter.c.count).label('maxcount'))\
        .group_by(counter.c.winebrand_id)\
        .subquery()

    tops = session\
        .query(UserReview.winebrand_id,
               UserReview.rating,
               func.count(UserReview.rating).label('topcount'))\
        .join(maxer, maxer.c.winebrand_id == UserReview.winebrand_id)\
        .group_by(UserReview.winebrand_id, UserReview.rating)\
        .having(func.count(UserReview.rating) == maxer.c.maxcount)\
        .subquery()

    wines = session\
        .query(WineBrand, tops.c.rating)\
        .outerjoin(tops, WineBrand.id == tops.c.winebrand_id)\
        .filter(WineBrand.winetype_id == winetype_id)\
        .order_by(collate(WineBrand.brand_name, 'NOCASE'), WineBrand.vintage.asc())

    return render_template(template_prefix+'brandsview.html',
                           winetype=winetype,
                           wines=wines)


@winebrand_api.route('/branditem/<int:stockitem_id>/', methods=["GET"])
def show_branditem(stockitem_id):
    session = current_app.config['db']
    item = session\
        .query(WineBrand)\
        .filter_by(id=stockitem_id)\
        .one()
    reviews = session\
        .query(UserReview)\
        .filter_by(winebrand_id=stockitem_id)\
        .order_by(UserReview.date_created.desc())
    return render_template(template_prefix+"brandview.html",
                           item=item,
                           reviews=reviews)


@winebrand_api.route('/new', methods=["GET", "POST"])
@login_required
def new():
    session = current_app.config['db']
    item = WineBrand(brand_name="", vintage=1980)
    maxyear = datetime.date.today().year
    if request.method == "POST":
        item.brand_name = request.form['itemname']
        item.winetype_id = request.form.get('winetypevalue', None)
        item.vintage = request.form.get('vintagevalue', None)
        item.date_created = datetime.datetime.today()
        item.user_id = login_session.get('user_id', None)
        if 'filename' in request.files:
            item.filename = brandphotos.save(
                request.files['filename'],
                name=make_safe_filename(request.files['filename'].filename))
        session.add(item)
        session.commit()
        session.flush()
        winetype = session.query(WineType.name)\
            .filter_by(id=item.winetype_id)\
            .one()
        flash("Successfully Added '%s (%s)'" % (winetype.name, item.brand_name),
              'success')
        return redirect(url_for('.show_branditem', stockitem_id=item.id))
    else:
        winetypes = session\
            .query(WineType)\
            .order_by(asc(collate(WineType.name, 'NOCASE')))\
            .all()
        return render_template(template_prefix+'new_form.html',
                               item=item,
                               winetypes=winetypes,
                               maxyear=maxyear)


@winebrand_api.route('/branditem/<int:stockitem_id>/delete',
                     methods=["GET", "POST"])
@login_required
def delete_branditem(stockitem_id):
    session = current_app.config['db']
    item = session.query(WineBrand)\
        .filter_by(id=stockitem_id)\
        .one()

    if item.user_id != login_session['user_id']:
        flash("You cannot delete this item",
              'danger')
        return redirect(url_for(".show_branditem", stockitem_id=stockitem_id))

    if request.method == "POST":
        try:
            os.remove(brandphotos.path(item.filename))
        except:
            # unable to remove old file, leave it be.
            pass
        c_name = item.brand_name
        session.delete(item)
        session.commit()
        flash("Successfully Deleted '%s'" % (c_name,), 'success')
        return redirect(url_for('.show'))
    else:
        return render_template(template_prefix+'delete_form.html', item=item)


@winebrand_api.route('/branditem/<int:stockitem_id>/edit',
                     methods=["GET", "POST"])
@login_required
def edit_branditem(stockitem_id):
    session = current_app.config['db']
    maxyear = datetime.date.today().year
    item = session.query(WineBrand)\
        .filter_by(id=stockitem_id)\
        .one()

    if item.user_id != login_session['user_id']:
        flash("You cannot edit this item",
              'danger')
        return redirect(url_for(".show_branditem", stockitem_id=stockitem_id))

    if request.method == "POST":
        item.brand_name = request.form['itemname']
        item.winetype_id = request.form.get('winetypevalue', None)
        item.vintage = request.form.get('vintagevalue', None)
        item.date_edited = datetime.datetime.today()
        item.user_id = login_session.get('user_id', None)
        if request.files.get('filename', None):
            oldfilename = item.filename
            item.filename = brandphotos.save(
                request.files['filename'],
                name=make_safe_filename(request.files['filename'].filename))
            try:
                os.remove(brandphotos.path(oldfilename))
            except:
                # unable to remove old file, leave it be.
                pass
        session.add(item)
        session.commit()
        session.flush()
        winetype = session.query(WineType.name)\
            .filter_by(id=item.winetype_id)\
            .one()
        flash("Successfully Added '%s (%s)'" % (winetype.name, item.brand_name),
              'success')
        return redirect(url_for('.show_branditem', stockitem_id=item.id))
    else:
        winetypes = session.query(WineType)\
            .order_by(asc(collate(WineType.name, 'NOCASE')))\
            .all()
        return render_template(template_prefix+'edit_form.html',
                               item=item,
                               winetypes=winetypes,
                               maxyear=maxyear)


@winebrand_api.route('/branditem/<int:stockitem_id>/rating/new',
                     methods=["POST"])
@login_required
def new_review(stockitem_id):
    session = current_app.config['db']
    if request.method == "POST":
        reviewitem = UserReview(
            winebrand_id=stockitem_id,
            summary=request.form.get('summary', None),
            comment=request.form.get('reviewtext', None),
            rating=request.form.get('star', 1),
            date_created=datetime.datetime.today(),
            user_id=login_session.get('user_id', None)
        )
        session.add(reviewitem)
        session.commit()
        flash("Successfully added a review", 'success')
        return redirect(url_for('.show_branditem', stockitem_id=stockitem_id))

# ToDo: Edit / Delete Reviews!?
@winebrand_api.route('/reviews/<int:user_id>', methods=["GET"])
def list_user_reviews(user_id):
    session = current_app.config['db']
    reviews = session.query(UserReview)\
        .filter_by(user_id=user_id)\
        .order_by(UserReview.date_created.desc())
    return render_template(template_prefix+"user_reviews_list.html",
                           reviews=reviews)
