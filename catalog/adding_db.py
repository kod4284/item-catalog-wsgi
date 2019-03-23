from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="Daewoong Ko", email="kodw0402@gmail.com")
session.add(User1)
session.commit()

User2 = User(name="Dongsuk Lim", email="dlim0305@gmail.com")
session.add(User2)
session.commit()

# Create dummy catalogs
Category1 = Category(name="Soccer")
session.add(Category1)
session.commit()

Category2 = Category(name="Basketball")
session.add(Category2)
session.commit()

# Create items
Item1 = Item(user_id=1, name="Soccer ball",
             description="This is a Soccer ball", category=Category1)
session.add(Item1)
session.commit()

Item2 = Item(user_id=2, name="Soccer uniform",
             description="This is a Soccer uniform", category=Category1)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1, name="Basketball ball",
             description="This is a Basketball ball", category=Category2)
session.add(Item3)
session.commit()

Item4 = Item(user_id=1, name="Basketball uniform",
             description="This is a Basketball uniform", category=Category2)
session.add(Item4)
session.commit()

print("added categories and items!")
