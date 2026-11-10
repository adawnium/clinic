"""Inbound adapter of the Patients feature: HTTP in, use case call, representation out."""

from fastapi import APIRouter, Depends, Query, Request, Response, status

from app.patients.adapters.http.schemas import Patient, PatientCreate, PatientPage, to_representation
from app.patients.application.service import PatientService
from app.shared.adapters.http.pagination import decode, next_cursor
from app.shared.adapters.http.problems import responses

router = APIRouter(prefix="/patients", tags=["patients"])


def service(request: Request) -> PatientService:
    """The service is built once, in app/main.py, and handed to the routes through app.state."""
    return request.app.state.patients


@router.get("", response_model=PatientPage, response_model_exclude_none=True, responses=responses(400, 422))
def list_patients(
    limit: int = Query(default=20, ge=1, le=50),
    cursor: str | None = Query(default=None, min_length=1, max_length=200),
    last_name: str | None = Query(default=None, alias="lastName", min_length=1, max_length=100),
    patients: PatientService = Depends(service),
) -> PatientPage:
    offset = decode(cursor)
    page = patients.list_patients(offset, limit, last_name)
    return PatientPage(items=[to_representation(p) for p in page.items], nextCursor=next_cursor(offset, limit, page.has_more))


@router.post("", response_model=Patient, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED, responses=responses(400, 422))
def create(body: PatientCreate, response: Response, patients: PatientService = Depends(service)) -> Patient:
    patient = patients.create(last_name=body.lastName, first_name=body.firstName, birth_date=body.birthDate, phone=body.phone)
    response.headers["Location"] = f"/patients/{patient.id}"
    return to_representation(patient)


@router.get("/{patient_id}", response_model=Patient, response_model_exclude_none=True, responses=responses(404))
def read(patient_id: str, patients: PatientService = Depends(service)) -> Patient:
    return to_representation(patients.read(patient_id))


@router.put("/{patient_id}", response_model=Patient, response_model_exclude_none=True, responses=responses(400, 404, 422))
def replace(patient_id: str, body: PatientCreate, patients: PatientService = Depends(service)) -> Patient:
    patient = patients.replace(patient_id, last_name=body.lastName, first_name=body.firstName, birth_date=body.birthDate, phone=body.phone)
    return to_representation(patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, responses=responses(404, 409))
def delete(patient_id: str, patients: PatientService = Depends(service)) -> Response:
    patients.delete(patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
