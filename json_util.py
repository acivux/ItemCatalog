"""
json page api endpoints implementation.
Marshmallow is used to where custom fields are returned in queries.
"""

from marshmallow import Schema, fields


class WineTypeListSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class WineBrandSchema(Schema):
    id = fields.Int()
    brand_name = fields.Str()
    vintage = fields.Int()


class WineCaveHomeListSchema(Schema):
    WineType = fields.Nested(WineTypeListSchema)
    count = fields.Int()


class WineBrandListSchema(Schema):
    WineBrand = fields.Nested(WineBrandSchema)
    rating = fields.Int()


def is_json_request(request_obj):
    """
    Returns true if the url ends in .json

    :param request_obj: The request object
    :return: true if json request
    """
    return request_obj.path.lower().endswith(".json")
