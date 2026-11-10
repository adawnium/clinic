"""Clinic — Patients and appointments: the composition root. Day 1: a single service that honors the
contract contracts/clinic.openapi.yaml. It will grow, then be split, over the following days.

This is the only file that knows every layer: it builds the adapters, injects them into the services
and plugs the routers into the FastAPI application.

Day 1: the Patients feature is provided, complete, as the example (app/patients/, one folder per layer); the Appointments
feature is yours, contract first (exercises/d1-afternoon/README.md)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS
from app.patients.adapters.http.router import router as patients_router
from app.patients.adapters.sqlalchemy import SqlAlchemyPatientRepository
from app.patients.application.service import PatientService
from app.shared.adapters.clock import SystemClock
from app.shared.adapters.db import Base, SessionFactory, engine
from app.shared.adapters.http import problems
from app.appointments.adapters.sqlalchemy import SqlAlchemyAppointmentRepository
from app.appointments.application.service import AppointmentService
from app.appointments.adapters.http.router import router as appointments_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)  # day 1: the schema is created at startup; migrations come later
    yield


app = FastAPI(
    title="Clinic — Patients and appointments",
    version="1.0.0",
    description="First service of the clinic. Synthetic data. Reference contract: contracts/clinic.openapi.yaml.",
    lifespan=lifespan,
    redirect_slashes=False,  # /patients/ is not /patients: 404, not a redirect outside the contract
)

# The Vue frontend runs on another origin (port 5173): the browser requires the server to allow it.
# We come back to this on day 4, with security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Location"],
)

# Wiring: outbound adapters into the services, by constructor. The routers find the services on app.state.
clock = SystemClock()

# 1. Instanciation des repositories (ports)
patients_repository = SqlAlchemyPatientRepository(SessionFactory)
appointments_repository = SqlAlchemyAppointmentRepository(SessionFactory)

# 2. Instanciation des services (cas d'usage) attachés à l'état de l'application
# PatientService prend maintenant l'appointment_repository en 3ème argument !
app.state.patients = PatientService(patients_repository, clock, appointments_repository)
app.state.appointments = AppointmentService(appointments_repository)

problems.install(app)
app.include_router(patients_router)
app.include_router(appointments_router)

@app.get("/health", tags=["operations"], summary="Is the service up?")
def health() -> dict[str, str]:
    return {"status": "ok"}