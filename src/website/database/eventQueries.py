from .models import Events
from .. import db
import datetime
from sqlalchemy import func, cast, Integer

#deletes event with id = id
def deleteEvent(id):
    Events.query.filter(Events.id == id).delete(synchronize_session=False)
    db.session.commit()
    return

#gets all events
def getEventsAdmin():
    all_events = Events.query.all()
    return all_events
   
#gets all events after/equal to the current date
def getEvents():
    year = datetime.datetime.today().strftime('%Y'); month = datetime.datetime.today().strftime('%m'); day = datetime.datetime.today().strftime('%d')
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    today = today.strftime('%d/%m/%Y')
    tomorrow = tomorrow.strftime('%d/%m/%Y')
    all_events = Events.query.filter((cast(func.substr(Events.date, 7, 10),Integer) > year) |
                                      ((cast(func.substr(Events.date, 4, 5), Integer) > month) & (cast(func.substr(Events.date, 7, 10) == year, Integer))) | 
                                      ((cast(func.substr(Events.date, 1, 2), Integer) >= day) & (cast(func.substr(Events.date, 4, 5), Integer) == month) & (cast(func.substr(Events.date, 7, 10), Integer) == year))).order_by(cast(func.substr(Events.date, 7, 10),Integer).asc(), cast(func.substr(Events.date, 4, 5),Integer).asc(), cast(func.substr(Events.date, 1, 2),Integer).asc()).all()
    for event in all_events:
        if event.date == today:
            event.date = "Today"
        elif event.date == tomorrow:
            event.date = "Tomorrow"
    return all_events

#updates an event with the given name and date
def updateEvent(id, name, date):
    Events.query.filter(Events.id == id).update({Events.name: name, Events.date:date})
    db.session.commit()

#adds a new event to the database
def addEvent(date, name):
    new_event = Events(date = date, name = name)
    db.session.add(new_event)
    db.session.commit()