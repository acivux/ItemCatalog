# TODO: remove serialize properties. API was implemented via Flask-Restful
from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy import Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy import create_engine
import colorsys


engine = create_engine('sqlite:///catalog.db')
Base = declarative_base()
Base.metadata.bind = engine


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250), nullable=True)
    nickname = Column(String(250), nullable=True, unique=True)
    admin = Column(Boolean)


class GlassType(Base):
    __tablename__ = 'glasstype'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    filename = Column(String(250), nullable=True, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,

        }


class Temperature(Base):
    __tablename__ = 'temperature'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    temp = Column(Float, nullable=False, unique=True)  # Fahrenheit Only

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'temp': self.temp,
            'id': self.id,
        }


# TODO: Deprecatred. Please delete
class WineCharacter(Base):
    __tablename__ = 'wine_character'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    wine_id = Column(Integer, ForeignKey('wine_type.id'))
    wine = relationship("WineType", backref="characters")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class WineABV(Base):
    __tablename__ = 'wine_abv'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class WineCalories(Base):
    __tablename__ = 'wine_calories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class WineColor(Base):
    __tablename__ = 'wine_color'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    value = Column(String(6), nullable=False, unique=True)  # HTML hex color code

    @property
    def hue(self):
        r, g, b = (int(self.value[i:i+2], 16) / 255.0 for i in xrange(0, 5, 2))
        return colorsys.rgb_to_hsv(r, g, b)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'color': self.color,
            'id': self.id,
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class WineType(Base):
    __tablename__ = 'wine_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(250, convert_unicode=True), nullable=False, unique=True)
    color_id = Column(Integer, ForeignKey('wine_color.id'), nullable=False)
    color = relationship(WineColor)
    glass_type_id = Column(Integer, ForeignKey('glasstype.id'), nullable=False)
    glass = relationship(GlassType)
    calorie_id = Column(Integer, ForeignKey('wine_calories.id'), nullable=False)
    calorie = relationship(WineCalories)
    abv_id = Column(Integer, ForeignKey('wine_abv.id'), nullable=False)
    abv = relationship(WineABV)
    temperature_id = Column(Integer, ForeignKey('temperature.id'), nullable=False)
    temperature = relationship(Temperature)
    filename = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    date_created = Column(DateTime, nullable=False)
    date_edited = Column(DateTime, nullable=True)
    brands = relationship("WineStock", cascade="all,delete", backref="winetype")

    # TODO: add id of creator.
    # TODO: prevent deletion if not creator.
    # TODO: prevent deletion if used in database.
    # TODO: add date created and edited
    # TODO: Add wikipedia link explaining wine type

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class WineStock(Base):
    __tablename__ = 'wine_stock'

    id = Column(Integer, primary_key=True)
    brand_name = Column(String(250), nullable=False)
    winetype_id = Column(Integer, ForeignKey('wine_type.id'), nullable=False)
    vintage = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_edited = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    filename = Column(String(250), nullable=True, unique=True)
    reviews = relationship("UserReview", cascade="all,delete", backref="winestock")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'brand': self.brand,
            'on_hand': self.on_hand,
            'id': self.id,
        }


class UserReview(Base):
    __tablename__ = 'user_review'

    id = Column(Integer, primary_key=True)
    winestock_id = Column(Integer, ForeignKey('wine_stock.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    summary = Column(String(250), nullable=False)
    comment = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'user': self.user_id,
            'comment': self.commnet,
            'id': self.id,
        }

Base.metadata.create_all(engine)