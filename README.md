# Lab — General practice clinic

Your starting point for the lab of the course "Microservices and REST APIs" (ISEN Toulon): the
software of a general practice clinic, simplified, growing half-day by half-day. **Synthetic data,
never real.** The instructions of each half-day are in the course material, section "Lab"; the
commands are in `exercises/`.

## Your copy, as a group or solo

Work in a group of 3 to 5, or solo. Each group, or each student working solo, works in **its own
fork** of this repository, on GitLab: one member forks it (button **Fork**, into their own namespace,
private is fine), adds the other members as *Developer* if any (**Manage → Members**), and everyone
clones the fork. Procedure in `exercises/d1-afternoon/README.md`.

## Contents

- `services/clinic/` — the clinic service, in a **hexagonal architecture**: the Patients resource is
  complete, as the example to follow; the Appointments resource is yours (Day 1 afternoon). Its
  `README.md` explains the layers.
- `contracts/` — the OpenAPI contract of the clinic service.
- `exercises/` — the material of each lab.

The frontend and the other services of the clinic arrive on the days that need them.

## A single Python environment

At the root of the repository, once for the whole week:

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Every `uvicorn`, `pytest`, `schemathesis` or `python` command in the READMEs assumes this venv is
active.

## Workstation prerequisites

- Python 3.12 or later, Git, `curl`, an editor.
- Node.js **22** or later (the Prism mock needs it from Day 1 afternoon).
- Windows: work in **Git Bash** (shipped with Git for Windows). In PowerShell, `curl` is an alias
  for another command: type `curl.exe`. Activating the venv is written
  `.venv\Scripts\activate`.
