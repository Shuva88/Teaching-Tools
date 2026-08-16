# OM & OR Teaching Tools

A growing collection of simple, interactive demonstrations for Operations
Management and Operations Research algorithms. Each demonstration reveals the
algorithm one step at a time for classroom discussion.

Before adding or redesigning an algorithm, follow
[CLASSROOM_DISPLAY_GUIDELINES.md](CLASSROOM_DISPLAY_GUIDELINES.md). It defines
the required staged presentation, one-screen classroom workspace, chart-label
rules, calculation detail, and verification checklist established from the
Johnson's Rule demonstration. `AGENTS.md` makes these standards standing
instructions for future coding sessions in this repository.

Version 1 contains only a fixed, demonstration-mode example of Johnson's Rule
for a two-resource campus print shop.

## Johnson's Rule demonstration

Six jobs pass through:

1. Resource 1: Printing / Photocopying
2. Resource 2: Binding / Finishing

The app programmatically identifies each minimum processing time, explains
whether the selected job belongs in the earliest or latest available position,
handles the A–C tie, and builds the sequence:

**E – A – F – D – C – B**

It then compares this sequence with the original `A – B – C – D – E – F`
sequence using Gantt charts, makespan, idle time, utilization, and average flow
time.

## Project structure

```text
Teaching-Tools/
├── AGENTS.md
├── app.py
├── algorithms/
│   └── johnson.py
├── components/
│   └── gantt.py
├── pages/
│   └── johnson_rule.py
├── tests/
│   └── test_johnson.py
├── CLASSROOM_DISPLAY_GUIDELINES.md
├── requirements.txt
└── README.md
```

Algorithm and scheduling logic are independent from the Streamlit interface so
that the presentation framework can be reused for future demonstrations.

## Run locally on Windows PowerShell

From the project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

Streamlit will print the local URL, normally `http://localhost:8501`.

## Student-facing release control

`app.py` explicitly registers the pages visible in the deployed application.
Only Johnson's Rule is released in Version 1. The GitHub repository can remain
private while the deployed Streamlit Community Cloud app is made public and
shared with students through its app URL.

## Measure definitions

- **Makespan:** completion time of the last job on Resource 2.
- **Idle time:** makespan minus the resource's total processing time.
- **Utilization:** total processing time divided by makespan.
- **Average flow time:** average Resource 2 completion time, with all jobs
  available at time zero.
