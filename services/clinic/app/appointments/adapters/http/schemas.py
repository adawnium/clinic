from datetime import datetime
from pydantic import BaseModel, Field

class AppointmentIn(BaseModel):
    start: datetime
    durationMinutes: int = Field(alias="durationMinutes")
    reason: str | None = None

class AppointmentOut(BaseModel):
    id: str
    patientId: str = Field(alias="patientId")
    start: datetime
    durationMinutes: int = Field(alias="durationMinutes")
    reason: str | None = None
    
    model_config = {"populate_by_name": True}

class AppointmentPage(BaseModel):
    items: list[AppointmentOut]
    nextCursor: str | None = Field(default=None, alias="nextCursor")
    
    model_config = {"populate_by_name": True}