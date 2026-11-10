
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app.appointments.adapters.http.schemas import AppointmentIn, AppointmentOut, AppointmentPage
from app.appointments.application.service import AppointmentService
from app.shared.domain.errors import Conflict, InvalidData, NotFound

# Remarque : j'ai retiré le prefix="/patients" car les routes appointments 
# s'appliquent parfois à /patients/{patient_id} et parfois à /appointments/{appointment_id}
router = APIRouter(tags=["appointments"])


def service(request: Request) -> AppointmentService:
    """The service is built once, in app/main.py, and handed to the routes through app.state."""
    return request.app.state.appointments


@router.post("/patients/{patient_id}/appointments", response_model=AppointmentOut, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
def create_appointment(
    patient_id: str,
    payload: AppointmentIn,
    response: Response,
    appointments: AppointmentService = Depends(service),
) -> AppointmentOut:
    try:
        app = appointments.create(
            patient_id=patient_id,
            start=payload.start,
            duration_minutes=payload.durationMinutes,
            reason=payload.reason,
        )
        response.headers["Location"] = f"/appointments/{app.id}"
        return AppointmentOut(
            id=app.id,
            patientId=app.patient_id,
            start=app.start,
            durationMinutes=app.duration_minutes,
            reason=app.reason,
        )
    except InvalidData as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Conflict as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/patients/{patient_id}/appointments", response_model=AppointmentPage, response_model_exclude_none=True)
def list_appointments(
    patient_id: str,
    appointments: AppointmentService = Depends(service),
    limit: int = Query(default=10, ge=1, le=100),
    after: datetime | None = None,
    cursor: str | None = None,
) -> AppointmentPage:
    page = appointments.list_appointments(patient_id, limit, after, cursor)
    items = [
        AppointmentOut(
            id=a.id,
            patientId=a.patient_id,
            start=a.start,
            durationMinutes=a.duration_minutes,
            reason=a.reason,
        )
        for a in page.items
    ]
    return AppointmentPage(
        items=items, 
        nextCursor=page.items[-1].id if page.has_more else None
    )


@router.get("/appointments/{appointment_id}", response_model=AppointmentOut, response_model_exclude_none=True)
def get_appointment(
    appointment_id: str,
    appointments: AppointmentService = Depends(service),
) -> AppointmentOut:
    try:
        a = appointments.read(appointment_id)
        return AppointmentOut(
            id=a.id,
            patientId=a.patient_id,
            start=a.start,
            durationMinutes=a.duration_minutes,
            reason=a.reason,
        )
    except NotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_appointment(
    appointment_id: str,
    appointments: AppointmentService = Depends(service),
) -> Response:
    try:
        appointments.delete(appointment_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))