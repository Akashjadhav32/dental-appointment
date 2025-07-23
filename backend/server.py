from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class TimeSlot(str, Enum):
    SLOT_0900_1000 = "9:00–10:00 AM"
    SLOT_1000_1100 = "10:00–11:00 AM"
    SLOT_1100_1200 = "11:00–12:00 PM"
    SLOT_1200_1300 = "12:00–1:00 PM"
    SLOT_1400_1500 = "2:00–3:00 PM"
    SLOT_1500_1600 = "3:00–4:00 PM"

# Define Models
class AppointmentCreate(BaseModel):
    name: str
    sex: Sex
    age: int
    complaint: str
    time_slot: TimeSlot
    appointment_date: date

    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @validator('complaint')
    def validate_complaint(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Complaint must be at least 5 characters long')
        return v.strip()

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    sex: Sex
    age: int
    complaint: str
    time_slot: TimeSlot
    appointment_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "scheduled"

def validate_appointment_slot(appointment_date: date, time_slot: TimeSlot):
    """Validate if the appointment slot is available based on day restrictions"""
    day_of_week = appointment_date.weekday()  # Monday is 0, Sunday is 6
    
    # Sunday - no appointments allowed
    if day_of_week == 6:
        raise HTTPException(
            status_code=400, 
            detail="Appointments are not available on Sundays"
        )
    
    # Saturday - only until 1:00 PM
    if day_of_week == 5:  # Saturday
        afternoon_slots = [TimeSlot.SLOT_1400_1500, TimeSlot.SLOT_1500_1600]
        if time_slot in afternoon_slots:
            raise HTTPException(
                status_code=400,
                detail="On Saturdays, appointments are only available until 1:00 PM"
            )
    
    # Check for past dates
    if appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointments for past dates"
        )

# Routes
@api_router.get("/")
async def root():
    return {"message": "Dental Clinic Appointment System API"}

@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate):
    """Create a new appointment"""
    try:
        # Validate appointment slot availability
        validate_appointment_slot(appointment_data.appointment_date, appointment_data.time_slot)
        
        # Check if slot is already booked
        existing_appointment = await db.appointments.find_one({
            "appointment_date": appointment_data.appointment_date.isoformat(),
            "time_slot": appointment_data.time_slot.value
        })
        
        if existing_appointment:
            raise HTTPException(
                status_code=400,
                detail="This time slot is already booked for the selected date"
            )
        
        # Create appointment
        appointment_dict = appointment_data.dict()
        appointment_dict["appointment_date"] = appointment_data.appointment_date.isoformat()
        appointment_obj = Appointment(**appointment_dict)
        
        # Save to database
        await db.appointments.insert_one(appointment_obj.dict())
        
        return appointment_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create appointment: {str(e)}")

@api_router.get("/appointments", response_model=List[Appointment])
async def get_appointments():
    """Get all appointments"""
    try:
        appointments = await db.appointments.find().sort("appointment_date", 1).to_list(1000)
        return [Appointment(**appointment) for appointment in appointments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointments: {str(e)}")

@api_router.get("/appointments/available-slots")
async def get_available_slots(appointment_date: str):
    """Get available slots for a specific date"""
    try:
        target_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        day_of_week = target_date.weekday()
        
        # All available slots
        all_slots = [slot.value for slot in TimeSlot]
        
        # Sunday - no slots
        if day_of_week == 6:
            return {"available_slots": [], "message": "No appointments available on Sundays"}
        
        # Saturday - only morning slots
        if day_of_week == 5:
            all_slots = [
                TimeSlot.SLOT_0900_1000.value,
                TimeSlot.SLOT_1000_1100.value,
                TimeSlot.SLOT_1100_1200.value,
                TimeSlot.SLOT_1200_1300.value
            ]
        
        # Get booked slots for the date
        booked_appointments = await db.appointments.find({
            "appointment_date": appointment_date
        }).to_list(1000)
        
        booked_slots = [appointment["time_slot"] for appointment in booked_appointments]
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return {"available_slots": available_slots}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch available slots: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()