import os
import uuid
import datetime

from flask import session as login_session
from flask import url_for


def make_safe_filename(oldfilename):
    """
    Returns a unique file name for use in a single folder with other files.
    """
    fn, ext = os.path.splitext(oldfilename)
    return str(uuid.uuid1()).replace('-', '')+ext.lower()


def get_single_postprocessor(instance_id=None, **kw):
    """
    Implements a postprocessor according to Flask-Restless
    Process the API data to return more readable results
    """
    from auth_api.auth_api import get_user_info

    try:
        cd = datetime.datetime.strptime(kw['result']['date_created'],
                                        "%Y-%m-%dT%H:%M:%S")
    except:
        cd = datetime.datetime.strptime(kw['result']['date_created'],
                                        "%Y-%m-%dT%H:%M:%S.%f")

    kw['result']['date_created'] = cd.strftime("%Y-%m-%d")
    if kw['result']['date_edited']:
        cd = datetime.datetime.strptime(kw['result']['date_edited'],
                                        "%Y-%m-%dT%H:%M:%S.%f")
        kw['result']['date_edited'] = cd.strftime("%Y-%m-%d")
    kw['result']['canedit'] = ""
    if kw['result']['user_id'] == login_session['user_id']:
        kw['result']['canedit'] = url_for('winetype_api.edit',
                                          item_id=kw['result']['id'])
    if kw['result']['user_id']:
        user = get_user_info(kw['result']['user_id'])
        kw['result']['user_name'] = user.nickname or user.name
        kw['result']['user_reviews'] = url_for(
            'winebrand_api.list_user_reviews', user_id=kw['result']['user_id'])
