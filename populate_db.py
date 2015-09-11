# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, User, WineType, Temperature
from database import GlassType, WineCalories, WineColor, WineABV, WineStock
import datetime

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


session.add(User(id=1, name="admin", email="admin@myurl.com", nickname="zztop", admin=False))
session.add(User(id=2, name="admin2", email="admin2@myurl.com", nickname="formatc", admin=False))
session.add(User(id=3, name="Jannie van Niekerk", email="acivux@gmail.com", admin=True))

session.add(GlassType(id=1, name="Sparkling Wine Flute"))
session.add(GlassType(id=2, name="White Wine Glass"))
session.add(GlassType(id=3, name="Standard Wine Glass"))
session.add(GlassType(id=4, name="Light Red Wine Glass"))
session.add(GlassType(id=5, name="Bold Red Wine Glass"))
session.add(GlassType(id=6, name="Dessert Wine Glass"))

session.add(Temperature(id=1, name="Ice Cold", temp=43))
session.add(Temperature(id=2, name="Cold", temp=48))
session.add(Temperature(id=3, name="Cool", temp=54))
session.add(Temperature(id=4, name="Cellar", temp=62))
session.add(Temperature(id=5, name="Cool Room", temp=68))

session.add(WineCalories(id=1, name="120-160"))
session.add(WineCalories(id=2, name="110-170"))
session.add(WineCalories(id=3, name="120-180"))
session.add(WineCalories(id=4, name="150-200"))
session.add(WineCalories(id=5, name="190-290"))

session.add(WineColor(id=1, name="Almost Clear", value="F2F5A9"))
session.add(WineColor(id=2, name="Green Yellow", value="D8F781"))
session.add(WineColor(id=3, name="Pale Gold", value="E4DE8A"))
session.add(WineColor(id=4, name="Pale Yellow", value="ECE8A8"))
session.add(WineColor(id=5, name="Pale Gold (Dark)", value="E9D775"))
session.add(WineColor(id=6, name="Deep Gold", value="EDBD3B"))
session.add(WineColor(id=7, name="Pale Salmon", value="F8E0F7"))
session.add(WineColor(id=8, name="Deep Pink", value="F475B7"))
session.add(WineColor(id=9, name="Deep Salmon", value="F78181"))
session.add(WineColor(id=10, name="Pale Ruby", value="D53C65"))
session.add(WineColor(id=11, name="Deep Violet", value="A93252"))
session.add(WineColor(id=12, name="Deep Purple", value="5B0055"))
session.add(WineColor(id=13, name="Tawny", value="CC6600"))

session.add(WineABV(id=1, name="9-14%"))
session.add(WineABV(id=2, name="10-15%"))
session.add(WineABV(id=3, name="12-17%"))
session.add(WineABV(id=4, name="14-20%"))

session.add(WineType(id=1,
                     name=u"Sparkling Wine",
                     color_id=1,
                     glass_type_id=1,
                     calorie_id=1,
                     abv_id=1,
                     temperature_id=2,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=1))
session.add(WineType(id=2,
                     name=u"Sauvignon Blanc",
                     color_id=2,
                     glass_type_id=2,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=3,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=1))
session.add(WineType(id=3,
                     name=u"Albariño",
                     color_id=3,
                     glass_type_id=2,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=3,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=1))
session.add(WineType(id=4,
                     name=u"Chenin Blanc",
                     color_id=4,
                     glass_type_id=2,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=3,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=1))
session.add(WineType(id=5,
                     name=u"Chardonnay",
                     color_id=5,
                     glass_type_id=2,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=3,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=6,
                     name=u"Noble Rot",
                     color_id=6,
                     glass_type_id=2,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=3,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=7,
                     name=u"Rosé of Pinot Noir",
                     color_id=7,
                     glass_type_id=3,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=2,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=8,
                     name=u"Rosé of Merlot",
                     color_id=8,
                     glass_type_id=3,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=2,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=9,
                     name=u"Rosé of Tempranillo",
                     color_id=9,
                     glass_type_id=3,
                     calorie_id=2,
                     abv_id=1,
                     temperature_id=2,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=10,
                     name=u"Pinot Noir",
                     color_id=10,
                     glass_type_id=4,
                     calorie_id=3,
                     abv_id=2,
                     temperature_id=3,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=11,
                     name=u"Sangiovese",
                     color_id=11,
                     glass_type_id=5,
                     calorie_id=4,
                     abv_id=3,
                     temperature_id=4,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=12,
                     name=u"Cabernet Sauvignon",
                     color_id=12,
                     glass_type_id=5,
                     calorie_id=4,
                     abv_id=3,
                     temperature_id=4,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))
session.add(WineType(id=13,
                     name=u"Sherry",
                     color_id=13,
                     glass_type_id=6,
                     calorie_id=5,
                     abv_id=4,
                     temperature_id=5,
                     date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                     user_id=2))

session.add(WineStock(id=1,
                      brand_name="Testing 123",
                      vintage=1990,
                      winetype_id=13,
                      date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
                      user_id=1,
                      filename='gwb1.png'))

session.add(WineStock(id=2,
                      brand_name="More Testing 123",
                      vintage=2000,
                      winetype_id=12,
                      date_created=datetime.datetime(2015, 2, 2, 0, 0, 0, 1),
                      user_id=2,
                      filename='gwb2.png'))

session.commit()
