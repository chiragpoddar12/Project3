from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalogapp.db')
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

# Create dummy category
category = Category(name="Snowboarding")
session.add(category)
session.commit()

category = Category(name="Soccer")
session.add(category)
session.commit()

category = Category(name="Basketball")
session.add(category)
session.commit()

category = Category(name="Baseball")
session.add(category)
session.commit()

category = Category(name="Foosball")
session.add(category)
session.commit()

category = Category(name="Cricket")
session.add(category)
session.commit()


# Create dummy item
item = Item(user_id=1, category_id = 1, name="Goggles", created_on=datetime.datetime.now())
session.add(item)
session.commit()

# Create dummy category
# category = Category(name="Baseball")
# session.add(category)
# session.commit()

# Create dummy item
item = Item(user_id=1,
            category_id = 2,
            name="Gloves",
            created_on=datetime.datetime.now(),
            desc = "desc1")
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 3,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = "desc2")
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 1,
            name="Snowboard",
            created_on=datetime.datetime.now(),
            desc = 'desc3')
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 4,
            name="Jacket",
            created_on=datetime.datetime.now(),
            desc = 'desc4')
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 5,
            name="Gloves",
            created_on=datetime.datetime.now(),
            desc = "desc1")
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 6,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = "desc2")
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 2,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = 'desc3')
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 1,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = 'desc4')
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 2,
            name="Gloves",
            created_on=datetime.datetime.now(),
            desc = "desc1")
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 6,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = "desc2")
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 5,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = 'desc3')
session.add(item)
session.commit()

item = Item(user_id=1,
            category_id = 4,
            name="Helmet",
            created_on=datetime.datetime.now(),
            desc = 'desc4')
session.add(item)
session.commit()
