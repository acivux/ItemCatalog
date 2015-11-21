from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy import Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Sequence

engine = create_engine('postgresql+psycopg2://catalog:horlosie@localhost/catalog')
Base = declarative_base()
Base.metadata.bind = engine


class User(Base):
    """
    User data.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250), nullable=True)
    nickname = Column(String(250), nullable=True, unique=True)
    admin = Column(Boolean)
    # User API not implemented due to privacy concerns


class GlassType(Base):
    """
    Glass type to use with a wine.
    """
    __tablename__ = 'glasstype'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name}


class Temperature(Base):
    """
    Serving temperature for a wine
    """
    __tablename__ = 'temperature'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    temp = Column(Float, nullable=False, unique=True)  # Fahrenheit Only

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "temp": self.temp}


class WineABV(Base):
    """
    Alcohol per Volume of the wine bottle
    """
    __tablename__ = 'wine_abv'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name}


class WineCalories(Base):
    """
    Calories per serving of wine
    """
    __tablename__ = 'wine_calories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name}


class WineColor(Base):
    """
    Color of the wine
    """
    __tablename__ = 'wine_color'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    # HTML hex color code
    value = Column(String(6), nullable=False, unique=True)

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "value": self.value}


class WineType(Base):
    """
    Type of wine.
    """
    __tablename__ = 'wine_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(250, convert_unicode=True), nullable=False,
                  unique=True)
    color_id = Column(Integer, ForeignKey('wine_color.id'), nullable=False)
    color = relationship(WineColor)
    glass_type_id = Column(Integer, ForeignKey('glasstype.id'), nullable=False)
    glass = relationship(GlassType)
    calorie_id = Column(Integer, ForeignKey('wine_calories.id'), nullable=False)
    calorie = relationship(WineCalories)
    abv_id = Column(Integer, ForeignKey('wine_abv.id'), nullable=False)
    abv = relationship(WineABV)
    temperature_id = Column(Integer, ForeignKey('temperature.id'),
                            nullable=False)
    temperature = relationship(Temperature)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    date_created = Column(DateTime, nullable=False)
    date_edited = Column(DateTime, nullable=True)
    brands = relationship("WineBrand", cascade="all,delete", backref="winetype")

    @property
    def serialize(self):
        return {"id": self.id,
                "name": self.name,
                "color": self.color.name,
                "glass": self.glass.name if self.glass else "",
                "calorie": self.calorie.name if self.calorie else "",
                "abv": self.abv.name if self.abv else "",
                "temperature":
                    self.temperature.name if self.temperature else "",
                "date_created": self.date_created,
                "date_edited": self.date_edited
                }


class WineBrand(Base):
    """
    A specific brand of wine.
    """
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
    reviews = relationship("UserReview", cascade="all,delete",
                           back_populates="winebrand")

    @property
    def serialize(self):
        return {"id": self.id,
                "brand_name": self.brand_name,
                "vintage": self.vintage,
                "date_created": self.date_created,
                "date_edited": self .date_edited,
                "user": self.user.nickname or self.user.name,
                "picture": self.filename
                }


class UserReview(Base):
    """
    User reviews
    """
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

    @property
    def serialize(self):
        return {"id": self.id,
                "user": self.user.nickname or self.user.name,
                "summary": self.summary,
                "comment": self.comment,
                "rating": self.rating,
                "date_created": self.date_created,
                "date_edited": self .date_edited,
                "winebrand": self.winebrand.serialize
                }

Base.metadata.create_all(engine)
