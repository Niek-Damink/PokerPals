from .models import Events
from .. import db
import datetime
from sqlalchemy import func, cast, Integer

def deleteEvent(id):
    Events.query.filter(Events.id == id).delete(synchronize_session=False)
    db.session.commit()
    return



def getEventsAdmin():
    all_events = Events.query.all()
    return all_events
   
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

def updateEvent(id, name, date):
    Events.query.filter(Events.id == id).update({Events.name: name, Events.date:date})
    db.session.commit()

def addEvent(date, name):
    new_event = Events(date = date, name = name)
    db.session.add(new_event)
    db.session.commit()