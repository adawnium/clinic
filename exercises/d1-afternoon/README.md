# Day 1, afternoon — the contract, then the service

Full instructions in the course material, chapter "Designing a REST contract", section "Afternoon
lab". Here, the material and the commands.

## 0. Your copy of the repository, as a group or solo

One member of the group, or you if you work solo, once: on GitLab, open this repository and click
**Fork** (into your own namespace; private is fine). In a group, then **Manage → Members**: add the
other members with the *Developer* role. Everyone, then:

```bash
git clone <url-of-the-fork> clinic && cd clinic
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Group or solo, the work happens on a `d1` branch created from `main`:
`git switch -c d1 && git push -u origin d1`. In a group, one member creates it and the others run
`git fetch && git switch d1`. Commit small and often; push at the end.

## The need

We spent a morning behind the reception desk. What the receptionist does, in her words:

- "A new patient walks in: I take their name and date of birth, and open a folder." Register a patient.
- "Someone calls for an appointment: I find them, then I look for a free slot." Find a patient, book a slot.
- "Two appointments at the same time is my nightmare." A slot that overlaps another is refused.
- "I need to see what Mrs Martin has coming up, and cancel when she calls." A patient's upcoming
  appointments; cancel one.
- Not asked for today: invoices, reminders, a mobile app. They come when they are needed, not before.

Patients is provided. Today you build the appointments: book, list what is coming up, cancel, and
refuse the overlap.

## User story and acceptance criteria

**As** the receptionist, **I want** to book an appointment for a patient, **so that** the
practitioner's day is planned without double bookings.

```gherkin
Scenario: a free slot is booked
  Given patient Léa Martin exists
  And nothing is booked on 2026-03-14 between 09:30 and 10:00
  When I book 09:30 for 30 minutes for Léa Martin
  Then the appointment is created
  And it shows in her upcoming appointments

Scenario: an overlapping slot is refused
  Given an appointment on 2026-03-14 from 09:30 to 10:00
  When I book 09:45 for 30 minutes, for any patient
  Then the booking is refused as a conflict
  And the agenda is unchanged
```

Each scenario becomes a unit test of the service, then a check of the contract. Write the other
scenarios yourself before coding: cancelling, listing what is coming up, a slot for an unknown
patient, a slot without a time zone.

## What is provided, what you write

The clinic service follows a **hexagonal architecture**, explained in `services/clinic/README.md`:
business rules in the domain, use cases in a service, HTTP and the database in adapters, wiring in
`app/main.py`, and unit tests that run without HTTP or database. The **Patients** resource is
complete across every layer, as the example to follow: its contract in
`contracts/clinic.openapi.yaml`, its package `services/clinic/app/patients/` (`domain/`, `ports/`,
`application/`, `adapters/`) and its tests
`services/clinic/tests/test_patients_service.py`. Read them first: this is the model, and the
constraint. Your code follows the same layers; a rule written in a router or a repository is a
mistake, and `lint-imports` says so.

Your turn with the **Appointments** resource, for the need above. The clinic has a single practitioner: a slot that overlaps another one is refused
(`409`), whatever the patient; a past appointment is accepted. Deleting a patient who has upcoming
appointments is refused (`409`, to add in `patients/application/service.py`).

The representation of an appointment:

| Field | Type | Rule |
|---|---|---|
| `id` | string | opaque, assigned by the server (`r_` + 8 hex characters) |
| `patientId` | string | the patient of the URL |
| `start` | string, `date-time` | with a time zone; year between 1900 and 2100 |
| `durationMinutes` | integer | 5 to 240 |
| `reason` | string | optional, 200 characters at most |

To create one, the client sends `start`, `durationMinutes` and optionally `reason`; nothing else.
The operations:

| Operation | Success | Errors |
|---|---|---|
| `GET /patients/{patientId}/appointments?limit&cursor&after` | `200`, a page (`items`, `nextCursor`) sorted by `start` | `400`, `404`, `422` |
| `POST /patients/{patientId}/appointments` | `201` + `Location` + the appointment | `400`, `404`, `409`, `422` |
| `GET /appointments/{appointmentId}` | `200` | `404` |
| `DELETE /appointments/{appointmentId}` | `204` | `404` |

In this order: the contract; then `appointments/domain/appointment.py` (the entity and its rules),
`appointments/ports/repository.py` (the port), `appointments/application/service.py` (the use cases),
`appointments/adapters/memory.py` (the port in a dictionary) with the unit tests in
`tests/test_appointments_service.py`, `appointments/adapters/sqlalchemy.py` (the table and the
repository), `appointments/adapters/http/schemas.py` and `router.py`, the wiring in `app/main.py`;
finally your package in the `lint-imports` contracts of `pyproject.toml`.

## 1. The contract, by hand, without AI

Complete `contracts/clinic.openapi.yaml`: the paths and schemas of appointments, modeled on those
of patients and on the tables above. A complete contract is also right in front of you: the Patients
part of the same file, and the `/docs` page of the running service, generated from the code.

Check that your document can be read by a tool, with a mock:

```bash
prism mock contracts/clinic.openapi.yaml       # a fake server on http://127.0.0.1:4010
curl -i http://127.0.0.1:4010/patients
curl -i http://127.0.0.1:4010/patients/p_7f3a1c2e/appointments
```

Have another group read it: can they write a client without talking to you?

## 2. The service, layer by layer, tests included

```bash
cd services/clinic                                # root venv active
pytest                                            # the unit tests: green before you start, green when you finish
lint-imports                                      # the layers: green before, green after
uvicorn app.main:app --reload                     # http://localhost:8000, documentation on /docs
```

The uvicorn terminal stays busy with the service: open a second one for what follows.

The database is a SQLite file created at startup (`clinic.db`). `DATABASE_URL` lets you change it
without touching the code. AI is allowed for writing the Appointments slice, on two conditions:
everyone must be able to explain the code delivered, and nothing gets committed without `pytest`
green. The rules (time zone, year range, duration, overlap) live in `appointments/domain/appointment.py` and
are tested in `tests/test_appointments_service.py`, which you create, against
`appointments/adapters/memory.py`, your in-memory adapter of the port, like the patients' rules against
theirs. `lint-imports` stays green: no FastAPI, Pydantic or SQLAlchemy inside `domain/`, `ports/` or
`application/`.

## 3. Conformance tests: done when everything is green

Schemathesis reads **your contract**, generates requests and checks that the service answers as the
contract promises. For today, the four basic checks:

```bash
# in a second terminal, at the root of the repository, venv active
schemathesis run contracts/clinic.openapi.yaml --url http://localhost:8000 \
  --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance
```

Read in order: no server error; every status code returned is documented; every `Content-Type`
is documented (errors are `application/problem+json`); every body follows its schema. Each
failure gives the request that caused it, to replay with `curl`. Either the contract promises too
much, or the service keeps its promise poorly.

The harder checks (`negative_data_rejection`: invalid data must be rejected) come on Day 4.
Curious? `--checks all --exclude-checks positive_data_acceptance`.

**Done when**: `pytest` is green with your appointment tests, the four Schemathesis checks are green
with your contract, and your `d1` branch is pushed.
