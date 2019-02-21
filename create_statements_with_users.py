"""Populate the propertieswithusers database some initial content.
This application stores Projects with each having
many Properties of various categories.
Five categories are created and some Properties are created
in each category.
This script should only be run on an empty database.
"""

# Import Dependencies from sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the following classes from the file
from database_setup import Base, Project, Property, User

# To know to which database we need to comunicate with
engine = create_engine('sqlite:///propertieswithusers.db')

# Make connections with class definitions with its tables in database itself
Base.metadata.bind = engine

# sessionmaker object
# To establish a link of communication b/w code executions and 
# engine we just created
DBSession = sessionmaker(bind=engine)

# sqlalchemy does operations on db via an interface called session
# Operation doesn't finish until commit
# session is Instance of DBSession
session = DBSession()

# Create dummy user
# Making a new entry into db is like making a new object in python
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://goo.gl/VzhNft')

# User1 will be added to the stagingzone
session.add(User1)

# User1 will be stored in the db
session.commit()

# Residential Properties under various Projects
myFirstProject = Project(user_id=1, project_name="Sagari Apartments")
session.add(myFirstProject)
session.commit()

mySecondProject = Project(user_id=1, project_name="Goteti Apartments")
session.add(mySecondProject)
session.commit()

# Commercial Properties under various Projects
myThirdProject = Project(user_id=1, project_name="D Adress Mall")
session.add(myThirdProject)
session.commit()

myFourthProject = Project(user_id=1, project_name="Life Style")
session.add(myFourthProject)
session.commit()

# Paying Guest Properties under various Projects
myFifthProject = Project(user_id=1, project_name="Lakshmi Boys Hostel")
session.add(myFifthProject)
session.commit()

mySixthProject = Project(user_id=1, project_name="Indhu Girls Hostel")
session.add(mySixthProject)
session.commit()

# Residential Rentals Properties under various Projects
fno_b2 = Property(
    user_id=1,
    property_name="Flat No:B2, Second Floor",
    cost="Rs.10,000/month",
    facilities="This Flat has two bedrooms",
    property_type="Residential Rental",
    project=myFirstProject)
session.add(fno_b2)
session.commit()


fno_g1 = Property(
    user_id=1,
    property_name="Flat No:G1, Ground Floor ",
    cost="Rs.16,00,000/month",
    facilities="This Flat has three bedrooms",
    property_type="Residential Rental",
    project=mySecondProject)
session.add(fno_g1)
session.commit()

# Residential Sales Properties under various Projects
fno_d3 = Property(
    user_id=1,
    property_name="Flat No:D3, Third Floor",
    cost="Rs.6,00,000",
    facilities="This Flat has one bedroom",
    property_type="Residential Sale",
    project=myFirstProject)
session.add(fno_d3)
session.commit()

fno_f4 = Property(
    user_id=1,
    property_name="Flat No:F4, Fourth Floor ",
    cost="Rs.20,00,000",
    facilities="This Flat has four bedrooms",
    property_type="Residential Rental",
    project=mySecondProject)
session.add(fno_f4)
session.commit()

# Commercial Rental Properties under various Projects
area_s1 = Property(
    user_id=1,
    property_name="Second Floor Sector1",
    cost="Rs.5,00,000",
    facilities="It has 10,000 sq.feet of land",
    property_type="Commercial Rental",
    project=myThirdProject)
session.add(area_s1)
session.commit()

area_d1 = Property(
    user_id=1,
    property_name="First Floor Sector0",
    cost="Rs.2,00,000",
    facilities="It has 4,000 sq.feet of land",
    property_type="Commercial Rental",
    project=myFourthProject)
session.add(area_d1)
session.commit()

# Commercial Sale Properties under various Projects
area_t3 = Property(
    user_id=1,
    property_name="Third Floor Sector2",
    cost="Rs.30,00,000",
    facilities="It has 6,000 sq.feet of land",
    property_type="Commercial Sale",
    project=myThirdProject)
session.add(area_t3)
session.commit()

area_d1 = Property(
    user_id=1,
    property_name="Ground Floor Sector3",
    cost="Rs.50,00,000",
    facilities="It has 9,000 sq.feet of land",
    property_type="Commercial Sale",
    project=myFourthProject)
session.add(area_d1)
session.commit()

# Paying Guest Properties under various Projects
pg_f2 = Property(
    user_id=1,
    property_name="Fifth Floor 3 Share Bed Room",
    cost="Rs.10,000/month",
    facilities="Food is available three times a day",
    property_type="Paying Guest",
    project=myFifthProject)
session.add(pg_f2)
session.commit()

pg_s2 = Property(
    user_id=1,
    property_name="sixth Floor 2 Share Bed Room",
    cost="Rs.12,000/month",
    facilities="Food is available three times a day",
    property_type="Paying Guest",
    project=mySixthProject)
session.add(pg_s2)
session.commit()
