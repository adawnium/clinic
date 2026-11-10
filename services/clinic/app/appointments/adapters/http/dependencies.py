# Exemple de fonction de dépendance pour FastAPI
from app.appointments.adapters.sqlalchemy import SqlAlchemyAppointmentRepository
from app.appointments.application.service import AppointmentService

def get_appointment_service(session: Session = Depends(get_session)) -> AppointmentService:
    repo = SqlAlchemyAppointmentRepository(session)
    return AppointmentService(repo)