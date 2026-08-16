# OM & OR Teaching Tools

A growing collection of interactive, fixed-example demonstrations for
Operations Management and Operations Research algorithms. Each demonstration
reveals the algorithm one decision at a time for classroom discussion.

Before adding or redesigning an algorithm, follow
[CLASSROOM_DISPLAY_GUIDELINES.md](CLASSROOM_DISPLAY_GUIDELINES.md). It defines
the required staged presentation, one-screen classroom workspace, chart-label
rules, calculation detail, and verification checklist established from the
Johnson's Rule demonstration. `AGENTS.md` makes these standards standing
instructions for future coding sessions in this repository.

## Demonstrations

### Johnson's Rule

Six jobs pass first through Printing / Photocopying and then through Binding /
Finishing. The demonstration programmatically identifies each minimum
processing time, explains earliest-versus-latest placement, handles the A–C
tie, and builds the sequence:

**E – A – F – D – C – B**

The Results view compares this sequence with the original sequence using Gantt
charts, makespan, idle time, utilization, average flow time, and the underlying
calculations.

### Scheduling Consecutive Days Off

A restaurant delivery hub has fixed minimum staffing requirements from Monday
through Sunday. Each partner works five days and receives two consecutive days
off. The demonstration separates each partner assignment into two classroom
steps:

1. Identify and select the consecutive days-off pair.
2. Assign the five working days and update the remaining requirements.

It includes all days at a tied requirement level, compares eligible pair
totals, and states the deterministic Monday-to-Sunday tie assumption. The
Results view shows the complete eight-partner schedule, required versus
scheduled staffing, excess staffing, and the lower-bound argument proving that
eight partners are minimum.

## Project structure

```text
Teaching-Tools/
|-- AGENTS.md
|-- app.py
|-- algorithms/
|   |-- consecutive_days_off.py
|   `-- johnson.py
|-- components/
|   |-- gantt.py
|   `-- staffing.py
|-- pages/
|   |-- consecutive_days_off.py
|   |-- home.py
|   `-- johnson_rule.py
|-- tests/
|   |-- test_consecutive_days_off.py
|   `-- test_johnson.py
|-- CLASSROOM_DISPLAY_GUIDELINES.md
|-- requirements.txt
`-- README.md
```

Algorithm and calculation logic are independent from the Streamlit interface.
This keeps the fixed examples testable and lets future demonstrations reuse the
same presentation framework without embedding calculations in display code.

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

Use the sidebar navigation to switch between demonstrations. Both pages are
fixed demonstration mode: there are no editable inputs, quizzes, downloads, or
authentication.

## Classroom links

The demonstrations appear under **Operations Management** in the sidebar:

- [Operations Management homepage](https://operationsmanagement.streamlit.app/)
- [Johnson's Rule](https://operationsmanagement.streamlit.app/johnsons_rule)
- [Scheduling Consecutive Days Off](https://operationsmanagement.streamlit.app/consecutive_days_off)

## Release and display controls

- `app.py` explicitly registers the pages visible in the application.
- A demonstration uses mutually exclusive Problem, Algorithm Workspace, and
  Results views rather than one continuously expanding page.
- The active working data, current explanation, progress, and controls stay
  together within approximately one projector screen.
- Distinct conceptual actions use distinct clicks; all candidates and tie
  assumptions are shown before the update is applied.
- Chart labels must be reserved space outside data marks and checked at the
  actual display width.
- After changing an imported component, restart Streamlit before visual
  verification so cached modules do not hide the change.

The detailed checklist and durable display rules are in
[CLASSROOM_DISPLAY_GUIDELINES.md](CLASSROOM_DISPLAY_GUIDELINES.md).
