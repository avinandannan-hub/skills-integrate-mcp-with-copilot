
"""
High School Management System API

A simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from pathlib import Path

from .db import init_db, get_session
from .models import Activity, Participant

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities"
)

current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

templates = Jinja2Templates(directory=current_dir / "templates")

init_db()

ACTIVITY_DATA = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    {
        "name": "Basketball Team",
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    {
        "name": "Art Club",
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    {
        "name": "Drama Club",
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    {
        "name": "Math Club",
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    {
        "name": "Debate Team",
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
]


def bootstrap_data():
    with get_session() as session:
        for item in ACTIVITY_DATA:
            statement = select(Activity).where(Activity.name == item["name"])
            result = session.exec(statement).first()
            if result:
                continue
            activity = Activity(
                name=item["name"],
                description=item["description"],
                schedule=item["schedule"],
                max_participants=item["max_participants"],
            )
            session.add(activity)
            session.commit()
            session.refresh(activity)
            for email in item["participants"]:
                participant = Participant(email=email, activity_id=activity.id)
                session.add(participant)
            session.commit()


bootstrap_data()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    with get_session() as session:
        statement = select(Activity)
        activities = session.exec(statement).all()
        result = {}
        for activity in activities:
            result[activity.name] = {
                "description": activity.description,
                "schedule": activity.schedule,
                "max_participants": activity.max_participants,
                "participants": [p.email for p in activity.participants],
            }
        return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    with get_session() as session:
        statement = select(Activity).where(Activity.name == activity_name)
        activity = session.exec(statement).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        if any(p.email == email for p in activity.participants):
            raise HTTPException(status_code=400, detail="Student is already signed up")
        if len(activity.participants) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")
        participant = Participant(email=email, activity_id=activity.id)
        session.add(participant)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    with get_session() as session:
        statement = select(Activity).where(Activity.name == activity_name)
        activity = session.exec(statement).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        participant = next((p for p in activity.participants if p.email == email), None)
        if not participant:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
        session.delete(participant)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
