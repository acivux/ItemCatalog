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


class Temperature(Base):
    __tablename__ = 'temperature'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    temp = Column(Float, nullable=False, unique=True)  # Fahrenheit Only


class WineABV(Base):
    __tablename__ = 'wine_abv'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)


class WineCalories(Base):
    __tablename__ = 'wine_calories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)


class WineColor(Base):
    __tablename__ = 'wine_color'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    value = Column(String(6), nullable=False, unique=True)  # HTML hex color code


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


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
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    date_created = Column(DateTime, nullable=False)
    date_edited = Column(DateTime, nullable=True)
    brands = relationship("WineBrand", cascade="all,delete", backref="winetype")


class WineBrand(Base):
    __tablename__ = 'wine_brand'

    id = Column(Integer, primary_key=True)
    brand_name = Column(String(250), nullable=False)
    winetype_id = Column(Integer, ForeignKey('wine_type.id'), nullable=False)
    vintage = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_edited = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    filename = Column(String(250), nullable=True, unique=False)
    reviews = relationship("UserReview", cascade="all,delete", back_populates="winebrand")


class UserReview(Base):
    __tablename__ = 'user_review'

    id = Column(Integer, primary_key=True)
    winebrand_id = Column(Integer, ForeignKey('wine_brand.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    summary = Column(String(250), nullable=False)
    comment = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_edited = Column(DateTime, nullable=True)
    winebrand = relationship("WineBrand", back_populates="reviews")


Base.metadata.create_all(engine)