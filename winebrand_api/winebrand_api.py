import os
import datetime

from flask import current_app, Blueprint, jsonify
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import asc, desc, func, collate
from flask import session as login_session
from flaskext.uploads import UploadSet, IMAGES

from database import WineBrand, WineType, UserReview
from utils import make_safe_filename
from auth_api.auth_api import login_required
from json_util import is_json_request

winebrand_api = Blueprint('winebrand_api', __name__)
template_prefix = "winebrand/"

brandphotos = UploadSet('brandphotos', IMAGES)


@winebrand_api.route('/view.json', methods=["GET"])
@winebrand_api.route('/view', methods=["GET"])
def show():
    """
    Shows the wine types and number of each available.

    :return: JSON or HTML page
    """
    from json_util import WineCaveHomeListSchema

    session = current_app.config['db']
    wines = session\
        .query(WineType, func.count(WineBrand.id).label('count'))\
        .join(WineBrand) \
        .group_by(WineType.name, WineType.id, WineType.color_id,
                  WineType.glass_type_id, WineType.calorie_id, WineType.abv_id,
                  WineType.temperature_id, WineType.user_id,
                  WineType.date_created, WineType.date_edited) \
        .order_by(asc(func.lower(WineType.name)))
    if is_json_request(request):
        schema = WineCaveHomeListSchema()
        return jsonify(items=[schema.dump(x).data for x in wines])
    else:
        return render_template(template_prefix+'topview.html', wines=wines)


@winebrand_api.route('/<int:winetype_id>/view.json', methods=["GET"])
@winebrand_api.route('/<int:winetype_id>/view', methods=["GET"])
def show_brand(winetype_id):
    """
    For a wine type, show the brands available. Also returns the most assigned
    rating for each brand.

    :param winetype_id: WineType id
    :return: JSON or HTML page
    """
    from json_util import WineBrandListSchema

    session = current_app.config['db']
    winetype = session.query(WineType).filter_by(id=winetype_id).one()

    # Counts the number of each rating
    counter = session\
        .query(UserReview.winebrand_id,
               UserReview.rating,
               func.count(UserReview.rating).label('count'))\
        .join(WineBrand)\
        .join(WineType)\
        .filter(WineBrand.winetype_id == winetype_id)\
        .group_by(UserReview.winebrand_id, UserReview.rating)\
        .order_by(UserReview.winebrand_id, desc('count'))\
        .subquery()

    # Gets the max of the count
    maxer = session\
        .query(counter.c.winebrand_id,
               func.max(counter.c.count).label('maxcount'))\
        .group_by(counter.c.winebrand_id,counter.c.count)\
        .subquery()

    # Gets the rating that matches max
    tops = session\
        .query(UserReview.winebrand_id,
               UserReview.rating,
               func.count(UserReview.rating).label('topcount'))\
        .join(maxer, maxer.c.winebrand_id == UserReview.winebrand_id)\
        .group_by(UserReview.winebrand_id, UserReview.rating)\
        .having(func.count(UserReview.rating) == maxer.c.maxcount)\
        .subquery()

    # In case multiple winners exists, choose the highest rating
    only_one = session\
        .query(UserReview.winebrand_id,
               func.max(tops.c.rating).label('bestrating'))\
        .outerjoin(tops, UserReview.winebrand_id == tops.c.winebrand_id)\
        .group_by(UserReview.winebrand_id, tops.c.rating)\
        .subquery()

    wines = session\
        .query(WineBrand, only_one.c.bestrating.label('rating'))\
        .outerjoin(only_one, WineBrand.id == only_one.c.winebrand_id)\
        .filter(WineBrand.winetype_id == winetype_id)\
        .order_by(func.lower(WineBrand.brand_name),
                  WineBrand.vintage.asc())

    if is_json_request(request):
        schema = WineBrandListSchema()
        return jsonify({"winetype": winetype.serialize,
                        "items": [schema.dump(x).data for x in wines]})
    else:
        return render_template(template_prefix+'brandsview.html',
                               winetype=winetype,
                               wines=wines)


@winebrand_api.route('/branditem/<int:stockitem_id>/view.json', methods=["GET"])
@winebrand_api.route('/branditem/<int:stockitem_id>/view', methods=["GET"])
def show_branditem(stockitem_id):
    """
    Shows a specific brand item and all the user reviews.
    Includes a  percentage breakdown of the ratings given.

    :param stockitem_id: WineBrand id
    :return: JSON or HTML page
    """
    from json_util import ReviewPercentage

    session = current_app.config['db']
    item = session\
        .query(WineBrand)\
        .filter_by(id=stockitem_id)\
        .one()
    reviews = session\
        .query(UserReview)\
        .filter_by(winebrand_id=stockitem_id)\
        .order_by(UserReview.date_created.desc())

    # Counts and groups the ratings
    totalcount = session\
        .query(func.count(UserReview.rating).label('totalcount'))\
        .filter(UserReview.winebrand_id == stockitem_id)\
        .subquery()

    # Calculate percentages for each rating
    counter = session\
        .query(UserReview.rating,
               ((100.00 * func.count(UserReview.rating)
                 .label('count')) / totalcount.c.totalcount).label('percent'))\
        .filter(UserReview.winebrand_id == stockitem_id)\
        .group_by(UserReview.rating, totalcount.c.totalcount)\
        .order_by(UserReview.rating.desc())

    if is_json_request(request):
        schema = ReviewPercentage()
        return jsonify(
            {"items": [x.serialize for x in reviews],
             "persentages": [schema.dump(x).data for x in counter]
             })
    else:
        return render_template(template_prefix+"brandview.html",
                               item=item,
                               reviews=reviews,
                               counter=counter)


@winebrand_api.route('/new', methods=["GET", "POST"])
@login_required
def new():
    """
    Creates a new brand for reviewing

    :return: HTML page
    """
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
    """
    Deletes a brand item. To simply the project, all the reviews
    are deleted too.

    :param stockitem_id: WineBrand id
    :return: HTML page
    """
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
            # Unable to remove old file, leave it be.
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
    """
    Edits a brand item.

    :param stockitem_id: WineBrand id
    :return: HTML page
    """
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
                # Unable to remove old file, leave it be.
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
    """
    Creates a new review.

    :param stockitem_id: WineBrand id to attache the review to.
    :return: HTML page
    """
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


@winebrand_api.route('/reviews/<int:user_id>/view.json', methods=["GET"])
@winebrand_api.route('/reviews/<int:user_id>/view', methods=["GET"])
def list_user_reviews(user_id):
    """
    Returns the current logged in user reviews.

    :param user_id: User id to return reviews for.
    :return: JSON or HTML page
    """
    session = current_app.config['db']
    reviews = session.query(UserReview)\
        .filter_by(user_id=user_id)\
        .order_by(UserReview.date_created.desc())
    if is_json_request(request):
        return jsonify(items=[x.serialize for x in reviews])
    else:
        return render_template(template_prefix+"user_reviews_list.html",
                               reviews=reviews)


@winebrand_api.route('/wines/<int:user_id>/view.json', methods=["GET"])
@winebrand_api.route('/wines/<int:user_id>/view', methods=["GET"])
def list_user_wines(user_id):
    """
    Returns the current logged in user created wines

    :param user_id: User id to return wines for
    :return: JSON or HMTL page
    """
    from json_util import WineBrandListSchema

    session = current_app.config['db']

    # Counts the number of each rating
    counter = session\
        .query(UserReview.winebrand_id,
               UserReview.rating,
               func.count(UserReview.rating).label('count'))\
        .join(WineBrand)\
        .join(WineType)\
        .filter(WineBrand.user_id == user_id)\
        .group_by(UserReview.winebrand_id, UserReview.rating)\
        .order_by(UserReview.winebrand_id, desc('count'))\
        .subquery()

    # Gets max for each rating
    maxer = session\
        .query(counter.c.winebrand_id,
               func.max(counter.c.count).label('maxcount'))\
        .group_by(counter.c.winebrand_id, counter.c.count)\
        .subquery()

    # Select the top rating
    tops = session\
        .query(UserReview.winebrand_id,
               UserReview.rating,
               func.count(UserReview.rating).label('topcount'))\
        .join(maxer, maxer.c.winebrand_id == UserReview.winebrand_id)\
        .group_by(UserReview.winebrand_id, UserReview.rating, maxer.c.maxcount)\
        .having(func.count(UserReview.rating) == maxer.c.maxcount)\
        .distinct()\
        .subquery()

    # In case multiple top ratings exist, choose the highest rating
    only_one = session\
        .query(UserReview.winebrand_id,
               func.max(tops.c.rating).label('bestrating'))\
        .outerjoin(tops, UserReview.winebrand_id == tops.c.winebrand_id)\
        .group_by(UserReview.winebrand_id, tops.c.rating)\
        .subquery()

    wines = session\
        .query(WineBrand, only_one.c.bestrating.label('rating'))\
        .outerjoin(only_one, WineBrand.id == only_one.c.winebrand_id)\
        .filter(WineBrand.user_id == user_id)\
        .order_by(func.lower(WineBrand.brand_name),
                  WineBrand.vintage.asc())

    if is_json_request(request):
        schema = WineBrandListSchema()
        return jsonify(items=[schema.dump(x).data for x in wines])
    else:
        return render_template(template_prefix+"user_wines_list.html",
                               wines=wines)


@winebrand_api.route('/reviews/<int:review_id>/delete',
                     methods=["GET", "POST"])
@login_required
def delete_review(review_id):
    """
    Deletes a review.

    :param review_id: UserReview id
    :return: HTML page
    """
    session = current_app.config['db']
    review = session\
        .query(UserReview)\
        .filter_by(id=review_id)\
        .one()

    if review.user_id != login_session['user_id']:
        flash("You cannot delete this item",
              'danger')
        return redirect(url_for(".list_user_reviews", user_id=review.user_id))

    if request.method == "POST":
        session.delete(review)
        session.commit()
        flash("Successfully deleted '%s'" % (review.summary,), 'success')
        return redirect(url_for(".list_user_reviews", user_id=review.user_id))
    else:
        return render_template(template_prefix+'delete_review.html',
                               item=review)


@winebrand_api.route('/reviews/<int:review_id>/edit',
                     methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    """
    Edit a review

    :param review_id: UserReview id
    :return: HTML page
    """
    session = current_app.config['db']
    review = session\
        .query(UserReview)\
        .filter_by(id=review_id)\
        .one()

    if review.user_id != login_session['user_id']:
        flash("You cannot edit this item",
              'danger')
        return redirect(url_for(".list_user_reviews", user_id=review.user_id))

    if request.method == "POST":
        review.summary = request.form.get('summary', None)
        review.comment = request.form.get('reviewtext', None)
        review.rating = request.form.get('star', 1)
        review.date_edited = datetime.datetime.today()
        session.add(review)
        session.commit()
        session.flush()
        flash("Successfully edited '%s'" % (review.summary,), 'success')
        return redirect(url_for(".list_user_reviews", user_id=review.user_id))
    else:
        return render_template(template_prefix+'edit_review.html',
                               item=review)
