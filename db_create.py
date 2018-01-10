import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

engine = create_engine('postgresql://catalog:udacity2018@localhost/catalog')
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

# Create categories
category1 = Category(name="Crossovers")
session.add(category1)
session.commit()

category2 = Category(name="SUVs")
session.add(category2)
session.commit()

category3 = Category(name="Trucks")
session.add(category3)
session.commit()

category4 = Category(name="Sedans")
session.add(category4)
session.commit()

category5 = Category(name="Coupes/Compact")
session.add(category5)
session.commit()

category6 = Category(name="Convertibles")
session.add(category6)
session.commit()

category7 = Category(name="Vans/Minivans")
session.add(category7)
session.commit()

category8 = Category(name="Hatchbacks")
session.add(category8)
session.commit()

category9 = Category(name="Wagons")
session.add(category9)
session.commit()

category10 = Category(name="Sports Cars")
session.add(category10)
session.commit()

category11 = Category(name="Luxury")
session.add(category11)
session.commit()

category12 = Category(name="Hybrid/Electric")
session.add(category12)
session.commit()

category13 = Category(name="Diesel")
session.add(category13)
session.commit()

category14 = Category(name="Commercial")
session.add(category14)
session.commit()

# Create initial user
User1 = User(
    name="John Appleseed",
    email="johnappleseed@gmail.com",
    picture="http://style.anu.edu.au/_anu/4/images/placeholders/person_8x10.png")
session.add(User1)
session.commit()

# Create initial items
Item1 = Item(
    name="2015 Chevrolet Corvette Stingray",
    description="For 2015 is the introduction of the Corvette Z06 all-new eight-speed automatic, Performance Data Recorder, OnStar with 4G LTE and two new design packages. All 2015 Corvette Stingray and Z06 models are offered with an all-new eight-speed paddle-shift automatic transmission designed to enhance performance and efficiency. Developed and built by GM, it delivers world-class shift times that rival the best dual-clutch designs. OnStar with 4G LTE and built-in Wi-Fi hotspot enhances Corvette's connectivity, providing a mobile hub for drivers and passengers with easy access to services that require a high-speed data connection. The all-new, industry-leading Performance Data Recorder enables users to record high-definition video, with telemetry overlays, of their driving experiences on and off the track. It was named Best Automotive Electronics Product at the 2014 Consumer Electronics Show, by Engadget. Along with all that's new with the 2015 Corvette Stingray, it carries over an unmatched combination of performance and efficiency. Power comes from the 6.2L LT1 V-8 rated at 455 horsepower and 460 lb-ft of torque - and 460 horsepower and 465 lb-ft with the available performance exhaust system. The Corvette Stingray's chassis and suspension are designed to take advantage of the lighter, stiffer structure. Its rigidity allowed engineers to more precisely tune the suspension and steering for a more nimble and responsive driving experience. The components and their calibrations - from the brake size and damper rates to the steering system - are identical between coupes and convertible. A racing-proven short/long-arm suspension design is used front and rear, with lightweight complementing components that include hollow lower control arms and aluminum rear toe links. Base model estimated mpg: 17/29 Estimated starting price: $53,000 Compiled by Motor Matters",
    date=datetime.datetime.utcnow(),
    category_id=10,
    user_id=1)
session.add(Item1)
session.commit()

Item2 = Item(
    name="2017 Ford Mustang",
    description="Modeled after the classic fastback, the 2017 Ford Mustang has a sleek, sporty, aerodynamic look, standard HID headlamps, and tri-bar LED taillamps with sequential turn signals. Enthusiast customers will continue to enjoy the original pony car's range of powerful engines. The standard 3.7-liter V6 offers up 300 horsepower and 280 lb.-ft. of torque, while the available 2.3-liter EcoBoost puts out 310 horsepower and 320 lb.-ft. of torque*. Mustang GT's 5.0-liter V8 engine kicks out 435 horsepower and 400 lb.-ft. of torque. All 2017 Ford Mustang models come with a dual exhaust system. The 2017 Mustang chassis features an integral link independent rear suspension that helps minimize body roll and isolate road imperfections for a responsive ride and precise handling. The popular Pony Package includes 19-inch polished aluminum wheels, unique upper grille with classic tri-bar pony logo and side stripes. The available Performance Package includes a 3.55 limited-slip differential, increased-diameter antiroll bars, larger brake rotors, heavy-duty springs and unique chassis tuning. The 2017 Mustang features available SYNC 3 enhanced voice recognition communications and entertainment system. An available 8-inch LCD capacitive touchscreen in the center stack has swipe and pinch-to-zoom capabilities, AppLink, 911 Assist, Apple CarPlay and Android Auto. Mustang car buyers can now opt for three new colors including Lightning Blue, Grabber Blue and White Platinum Metallic Tri-coat. Base model estimated mpg: 22/31 Estimated starting price: $24,915 Compiled by Motor Matters",
    date=datetime.datetime.utcnow(),
    category_id=10,
    user_id=1)
session.add(Item2)
session.commit()

Item3 = Item(
    name="2017 Chevrolet Colorado",
    description="The 2017 Chevrolet Colorado ZR2 is poised to reset expectations for off-road trucks. Chevy's new performance trim for the Colorado lineup features more off-road technology than any other midsize pickup. Compared to a standard Colorado, the ZR2 features a much wider track and a lifted suspension. Functional rockers have been added for better performance over rocks and obstacles, and the front and rear bumpers have been modified for better off-road clearance. Class-exclusive features include front and rear electronic locking differentials, available diesel engine, and the first off-road application of Multimatic Dynamic Suspensions Spool Valve damper technology. As a result, the Colorado ZR2 delivers exceptional performance from technical rock crawling, to tight two-track trails, to high-speed desert running to daily driving. The Colorado ZR2's exterior design was shaped by the desire to improve capability driving over mud, sand and rock. The wider, more aggressive stance, modified front and rear bumpers, and the bed-mounted, spare-tire carrier all improve performance driving over rough terrain. Compared to a Colorado Z71, the ZR2 has a more aggressive side profile, with the suspension lifted 2 inches for greater ground clearance. The steel-tube, functional rocker protectors are standard equipment on the ZR2, and are strong enough to protect the body side while dragging the truck against a rock face. The 3.6L V-6, mated to a class-exclusive Hydra-Matic 8L45 8-speed automatic transmission, yields 308 horsepower and 275 lb-ft of torque, while the class-exclusive Duramax diesel engine produces 181 horsepower and 369 lb-ft of torque. Even with all of the off-roading upgrades the ZR2 can still tow up to 5,000 pounds -- enough to pull a camper, trailer dirt bikes, jet skis, snow mobiles and other toys -- or carry 1,100 pounds of payload. Base model estimated mpg: 17/24 Estimated starting price: TBA Compiled by Motor Matters",
    date=datetime.datetime.utcnow(),
    category_id=3,
    user_id=1)
session.add(Item3)
session.commit()