# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, WineType, Temperature
from database import GlassType, WineCalories, WineColor, WineABV, WineBrand
from database import UserReview
import datetime
import random
from testing_user import TESTING_USER

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

ratings = [1, 2, 3, 4, 5, 3, 2, 1]
fake_person_names = ["Joetta Janas", "Richelle Riles", "Marvin Malcom",
                     "Leandra Luick", "Sylvester Schachter", "Dara Doran",
                     "Bradford Bartol", "Tamar Twitchell", "Aracelis Allred",
                     "Margherita Motz", "Tosha Trundy", "Elia Endres",
                     "Candis Carlsen", "Daron Dunnigan", "Nedra Newbill",
                     "France Figeroa", "Lavonne Lemarr", "Maida Mabee",
                     "Carmel Carnahan", "Alleen Armwood", "Myrle Madrid",
                     "Roslyn Railsback", "Lilliana Losee", "Dino Durand",
                     "Nathan Nachman", "Hyo Hendry", "Joyce Johannsen",
                     "Willis Withrow", "Maurita Monterrosa", "Paulita Pavone",
                     "Joeann Junk", "Leo Lotz", "Crystal Calvo",
                     "Cedrick Chait",
                     "Ada Arend", "Kirstie Kamps", "Jayson Jobin",
                     "Tiffanie Tetterton", "Honey Hohn", "Amos Adelman",
                     "Lin Lodi",
                     "Shirleen Seligman", "Bernard Belser", "Erica Etheridge",
                     "Rosario Rottman", "Portia Punch", "Bunny Brownlow",
                     "Tierra Trabue", "Daniele Darling", "Nora Natividad"]

fake_wine_names = ["Peaulet Secco", "Trietage Mousseux", "Egeac", "Naibera",
                   "Trieblis Bianco", "Miancalla", "Trilrimeur",
                   "Ueplochage Blanco", "Trouiccilung Noir",
                   "Grerneaunote Cava", "Trefe Chiaretto", "Oblage", "Keblage",
                   "Zilion Mousseux", "Yiphe Bianco", "Sobbueulo Rich",
                   "Surgiello Rosado", "Loreausson Rosato", "Heimblegeot Doux",
                   "Frortholien Vendimia", "Onon Rich", "Vinais Vie",
                   "Ieumante Dulce", "Hulung Petillant",
                   "Shiabria Cap Classique", "Flueurcheve Classic",
                   "Sousbonas Szaraz", "Giablirnet Fume",
                   "Meaugragnan Acescence", "Xornumeur", "Unti Granvas",
                   "Frilo Petillant", "Bulet Clairet", "Troder Rich",
                   "Wichot Invecchiato", "Curgrarol Frizzante",
                   "Trigruder Adega", "Lumpudange Abboccato",
                   "Blimchuvrey Cepage", "Zeiccisson Adamado"]

fake_images = ['gwb1.png', 'gwb2.png', 'gwb3.png']

review_text = """Lorem ipsum dolor sit amet, in augue legendos dissentias sit, facilis reprehendunt nam te, mel te sint idque prompta. Erant choro accusam eu est, munere reformidans eu nec. Eos possim nonumes gubergren ut, in essent fastidii complectitur vim. Has et exerci semper eloquentiam, maluisset cotidieque qui ne. Ut ridens iisque sit, vel nulla consequat intellegat et. Legere legimus indoctum at mea, primis fabulas detracto sea at.

Ei mediocrem mediocritatem sed, ridens noluisse eos ea. Te pro doctus facilis efficiantur, putant explicari in pri. Vide signiferumque eu mea, populo assueverit vel ne. Suas elit cu nam, et omnis errem verterem mel, altera fabulas id his.

Aliquid sadipscing eam ad, per mutat essent pertinacia te. Quo mutat aperiri ei, diam probatus ut duo. At his admodum fabellas maluisset, te mazim consectetuer cum. Ridens pertinacia pri eu. Pro ne simul pertinacia, eos porro audire postulant te, has prompta aliquam te. Mei quando diceret eu.

Ne mutat scripta albucius sed. Ea his percipitur concludaturque, et qui putent vocibus. Ius ea dicunt deleniti molestiae, vis at recusabo pertinacia, ius te oblique forensibus voluptatum. Sed mutat dictas constituam in, nam et veri volutpat. Pro ut enim cetero constituto.

An doctus inermis corpora sea, ex vix erant laboramus definitiones. Tamquam lucilius detraxit eu nec. Ei nec dicant alienum mediocrem, at lorem inermis interesset qui, et sit principes vituperatoribus. Cu qui inermis graecis, mei an nibh falli. Harum oratio indoctum mea ne, vim at sint nulla aperiam.

Intellegam philosophia reprehendunt ne pri. Ea utroque docendi efficiantur sea. Et eros euripidis voluptaria ius, te stet quaerendum signiferumque nec. Omnis diceret eu sea.

Ne deleniti principes mea, ut mel tamquam fabulas periculis. Alia exerci detracto ea vel. Ex eos habeo persecuti vituperatoribus. Pro id zril tamquam noluisse, essent blandit explicari quo et. Eam no feugiat aliquando, idque aliquando est et, mundi putent ancillae ea est. Ne agam phaedrum nam.

Usu odio ubique numquam eu, ut decore omittantur duo. Ponderum tincidunt consectetuer nam ut. Eam eu clita labore impetus. Omnes eruditi nam ei, mei facilis theophrastus eu.

Id nam idque tamquam fabulas, nam ea veniam fuisset lucilius, ad tantas prodesset nam. Eu ius maiorum mediocrem. Mea ei alii perfecto, impetus lobortis te nam. Elitr vitae putent pro te, ad lucilius constituto moderatius est.

An sed vidit postulant laboramus, summo nominavi assueverit ex ius, mei eu soleat omnium vivendo. Ne usu semper mentitum. Unum regione oportere eos ut, duo ad nibh invenire gubergren, nec ad dicit tempor option. Mucius placerat ullamcorper eos no, autem corpora has ne.
"""

summary_text = """Bacon ipsum dolor amet tail pancetta pastrami, salami venison ribeye landjaeger kevin turducken kielbasa. Salami picanha fatback andouille. Capicola pork belly bacon sirloin shank. Filet mignon pig hamburger doner, leberkas meatball biltong shankle bacon drumstick kielbasa sausage prosciutto chuck pork loin.

Alcatra tenderloin turkey ham hock tongue ball tip turducken. Brisket short ribs jowl swine pig frankfurter rump capicola short loin. Pancetta jerky venison ball tip cow meatball picanha tri-tip. Kielbasa salami beef sirloin, chicken shank tongue cupim. Tri-tip cow ham hock, flank bresaola chuck filet mignon pork chop kevin rump bacon leberkas. Meatloaf turkey hamburger flank. Frankfurter hamburger bacon pork belly shank swine venison short loin rump ham hock porchetta turducken shoulder.

Pork chop chicken andouille short ribs, ball tip ground round meatloaf pork alcatra brisket salami. Turducken pork loin pancetta hamburger. Cow prosciutto landjaeger filet mignon kevin, corned beef pancetta meatball venison doner shankle kielbasa short ribs. Pig leberkas andouille cow, pancetta shankle swine boudin rump shoulder kevin landjaeger pork belly fatback venison.

Frankfurter turducken drumstick, corned beef spare ribs shank andouille. Shoulder ribeye andouille meatball cow. Frankfurter ribeye turkey porchetta, venison short ribs short loin pastrami tongue ball tip pork chop alcatra jerky pork belly cupim. Alcatra sausage brisket ball tip ground round, turducken bresaola chicken pig pork ham hock pancetta.

Sausage alcatra shankle, pork chop rump kevin ham pork flank ball tip. Pastrami ham hock bacon prosciutto, salami pig shoulder cupim chuck venison spare ribs capicola filet mignon chicken leberkas. Hamburger spare ribs tenderloin, ham swine landjaeger meatloaf frankfurter sausage capicola rump. Swine bacon fatback filet mignon shankle tenderloin kevin beef alcatra sirloin spare ribs ground round landjaeger.

Bresaola drumstick sausage pancetta short ribs corned beef biltong ribeye prosciutto porchetta leberkas ground round meatloaf filet mignon. Pig meatball ball tip, hamburger short loin pastrami capicola shank shankle beef ribs. Frankfurter doner boudin pork chop. Ham hock cupim shoulder pork loin, turducken jerky venison salami pancetta fatback tongue pork shankle. Short loin venison pork t-bone bresaola salami ground round pancetta andouille brisket chuck flank.

Beef flank prosciutto jerky ham hock ribeye. Meatball doner brisket flank drumstick rump. Pastrami meatball picanha rump. Beef ribs prosciutto alcatra short loin, tongue swine salami pancetta drumstick.

Shankle biltong kevin doner swine jerky. Fatback chicken meatball alcatra flank. Tri-tip tail filet mignon, shankle meatloaf frankfurter short ribs beef ribs shank pancetta salami sirloin kevin turducken pork. Alcatra pork chop meatloaf, fatback meatball brisket ground round picanha turkey sirloin doner boudin biltong. Pork ground round shoulder capicola.

Boudin andouille prosciutto pork chop shoulder hamburger. Andouille jerky shankle salami tongue bacon bresaola beef landjaeger swine cow. Hamburger shankle jowl pork loin landjaeger short ribs, strip steak kielbasa boudin pig ball tip t-bone. Corned beef landjaeger pastrami ball tip biltong. Frankfurter tongue biltong sausage capicola. Meatball chuck doner alcatra beef ribs landjaeger, ribeye leberkas pork belly pork chop shoulder swine.

Cow turkey biltong, shankle tri-tip fatback rump brisket pastrami ham hock hamburger sirloin alcatra salami capicola. Frankfurter swine bacon kielbasa. Jerky chuck short loin pork shank corned beef meatball t-bone tail filet mignon tongue. Tenderloin tri-tip meatloaf pork chop jerky porchetta.
"""


def random_date(year_start=1900, year_end=2015):
    """
    This function will return a random datetime between two datetime
    objects.
    ToDo: Attribute in readme
    http://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
    """
    d1 = datetime.datetime.strptime('1/1/'+str(year_start)+' 1:30 PM',
                                    '%m/%d/%Y %I:%M %p')
    d2 = datetime.datetime.strptime('1/1/'+str(year_end)+' 4:50 AM',
                                    '%m/%d/%Y %I:%M %p')
    delta = d2 - d1
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return d1 + datetime.timedelta(seconds=random_second)


def random_vintage():
    return random_date().year


def random_creation_date():
    return random_date(2013, 2015)


def random_user():
    return random.randint(0, len(fake_person_names))


def random_image():
    return random.choice(fake_images)


def make_nickname(user_name):
    return ''.join(random.choice(user_name) for x in xrange(len(user_name)-1))


def random_summary():
    start = random.randint(0, int(len(summary_text)/2))
    end = start + random.randrange(20, 250)
    return summary_text[start:end]


def random_review():
    return review_text[0:random.randint(50, len(review_text))]

# The testing user that match valid Google or Facebook email address
# Create your own User object in testing_user.py
session.add(TESTING_USER)
counter = 2
for name in fake_person_names:
    session.add(User(id=counter,
                     name=name,
                     email="abc"+str(counter)+"@myurl.com",
                     nickname=make_nickname(name),
                     admin=False))
    counter += 1

glasses = [GlassType(id=1, name="Sparkling Wine Flute"),
           GlassType(id=2, name="White Wine Glass"),
           GlassType(id=3, name="Standard Wine Glass"),
           GlassType(id=4, name="Light Red Wine Glass"),
           GlassType(id=5, name="Bold Red Wine Glass"),
           GlassType(id=6, name="Dessert Wine Glass")]
for glass in glasses:
    session.add(glass)

temps = [Temperature(id=1, name="Ice Cold", temp=43),
         Temperature(id=2, name="Cold", temp=48),
         Temperature(id=3, name="Cool", temp=54),
         Temperature(id=4, name="Cellar", temp=62),
         Temperature(id=5, name="Cool Room", temp=68)]
for temp in temps:
    session.add(temp)

cals = [WineCalories(id=1, name="120-160"), WineCalories(id=2, name="110-170"),
        WineCalories(id=3, name="120-180"), WineCalories(id=4, name="150-200"),
        WineCalories(id=5, name="190-290")]
for cal in cals:
    session.add(cal)

colors = [WineColor(id=1, name="Almost Clear", value="F2F5A9"),
          WineColor(id=2, name="Green Yellow", value="D8F781"),
          WineColor(id=3, name="Pale Gold", value="E4DE8A"),
          WineColor(id=4, name="Pale Yellow", value="ECE8A8"),
          WineColor(id=5, name="Pale Gold (Dark)", value="E9D775"),
          WineColor(id=6, name="Deep Gold", value="EDBD3B"),
          WineColor(id=7, name="Pale Salmon", value="F8E0F7"),
          WineColor(id=8, name="Deep Pink", value="F475B7"),
          WineColor(id=9, name="Deep Salmon", value="F78181"),
          WineColor(id=10, name="Pale Ruby", value="D53C65"),
          WineColor(id=11, name="Deep Violet", value="A93252"),
          WineColor(id=12, name="Deep Purple", value="5B0055"),
          WineColor(id=13, name="Tawny", value="CC6600")]
for color in colors:
    session.add(color)

abvs = [WineABV(id=1, name="9-14%"),
        WineABV(id=2, name="10-15%"),
        WineABV(id=3, name="12-17%"),
        WineABV(id=4, name="14-20%")]
for abv in abvs:
    session.add(abv)

winetypes = [WineType(id=1, name=u"Sparkling Wine", color_id=1, glass_type_id=1,
                      calorie_id=1, abv_id=1, temperature_id=2,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=2, name=u"Sauvignon Blanc", color_id=2,
                      glass_type_id=2, calorie_id=2, abv_id=1, temperature_id=3,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=3, name=u"Albariño", color_id=3, glass_type_id=2,
                      calorie_id=2, abv_id=1, temperature_id=3,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=4, name=u"Chenin Blanc", color_id=4, glass_type_id=2,
                      calorie_id=2, abv_id=1, temperature_id=3,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=5, name=u"Chardonnay", color_id=5, glass_type_id=2,
                      calorie_id=2, abv_id=1, temperature_id=3,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=6, name=u"Noble Rot", color_id=6, glass_type_id=2,
                      calorie_id=2, abv_id=1, temperature_id=3,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=7, name=u"Rosé of Pinot Noir", color_id=7,
                      glass_type_id=3, calorie_id=2, abv_id=1, temperature_id=2,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=8, name=u"Rosé of Merlot", color_id=8, glass_type_id=3,
                      calorie_id=2, abv_id=1, temperature_id=2,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=9, name=u"Rosé of Tempranillo", color_id=9,
                      glass_type_id=3, calorie_id=2, abv_id=1, temperature_id=2,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=10, name=u"Pinot Noir", color_id=10, glass_type_id=4,
                      calorie_id=3, abv_id=2, temperature_id=3,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=11, name=u"Sangiovese", color_id=11, glass_type_id=5,
                      calorie_id=4, abv_id=3, temperature_id=4,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=12, name=u"Cabernet Sauvignon", color_id=12,
                      glass_type_id=5, calorie_id=4, abv_id=3, temperature_id=4,
                      date_created=random_creation_date(),
                      user_id=random_user()),
             WineType(id=13, name=u"Sherry", color_id=13, glass_type_id=6,
                      calorie_id=5, abv_id=4, temperature_id=5,
                      date_created=random_creation_date(),
                      user_id=random_user())]
for wtype in winetypes:
    session.add(wtype)

counter = 1
winebrands = []
for fake_wine_name in fake_wine_names:
    abrand = WineBrand(id=counter, brand_name=fake_wine_name,
                       vintage=random_vintage(),
                       winetype_id=random.choice(winetypes).id,
                       date_created=random_creation_date(),
                       user_id=random_user(), filename=random_image())
    winebrands.append(abrand)
    session.add(abrand)
    counter += 1

for review_id in xrange(1, 4000):
    areview = UserReview(id=review_id,
                         winebrand_id=random.choice(winebrands).id,
                         user_id=random_user(),
                         summary=random_summary(),
                         comment=random_review(),
                         rating=random.choice(ratings),
                         date_created=random_creation_date())
    session.add(areview)

#
# session.add(WineBrand(id=1,
#                       brand_name="Testing 123",
#                       vintage=1990,
#                       winetype_id=13,
#                       date_created=datetime.datetime(2015, 1, 1, 0, 0, 0, 1),
#                       user_id=1,
#                       filename='gwb1.png'))
# session.add(WineBrand(id=2,
#                       brand_name="More Testing 123",
#                       vintage=2000,
#                       winetype_id=12,
#                       date_created=datetime.datetime(2015, 2, 2, 0, 0, 0, 1),
#                       user_id=2,
#                       filename='gwb2.png'))
# session.add(WineBrand(id=3,
#                       brand_name="FiFi",
#                       vintage=2010,
#                       winetype_id=12,
#                       date_created=datetime.datetime(2015, 2, 2, 0, 0, 0, 1),
#                       user_id=3,
#                       filename='gwb3.png'))


session.commit()


