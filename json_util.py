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
    return request_obj.path.lower().endswith(".json")
