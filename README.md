# OM & OR Teaching Tools

A growing collection of interactive, fixed-example demonstrations for
Operations Management and Operations Research algorithms. Each demonstration
reveals the algorithm one decision at a time for classroom discussion.

Before adding or redesigning an algorithm, follow
[CLASSROOM_DISPLAY_GUIDELINES.md](CLASSROOM_DISPLAY_GUIDELINES.md). It defines
the required staged presentation, one-screen classroom workspace, chart-label
rules, calculation detail, and verification checklist established across the
demonstrations, including the Simplex review lessons. `AGENTS.md` makes these standards standing
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
through Sunday. Each employee works five days and receives two consecutive days
off. The demonstration separates each employee assignment into two classroom
steps:

1. Identify and select the consecutive days-off pair.
2. Assign the five working days and update the remaining requirements.

It includes all days at a tied requirement level, compares eligible pair
totals, and states the deterministic Monday-to-Sunday tie assumption. The
Results view shows the complete eight-employee schedule, required versus
scheduled staffing, excess staffing, and the lower-bound argument proving that
eight employees are minimum.

### Single-Processor Sequencing

Six fabrication orders compete for one CNC laser-cutting machine. The
demonstration compares First Come, First Served (FCFS), Shortest Processing Time
(SPT), Earliest Due Date (EDD), Longest Processing Time (LPT), and dynamic
Critical Ratio (CR), showing each sequence, Gantt chart, order-level
calculations, and five performance measures. The CR stage recomputes every
unscheduled order's ratio after each completion. The comparison makes the
fixed-example trade-off explicit: SPT gives the lowest average flow time, while
EDD gives the strongest tardiness-related results.

### VRP: Clarke-Wright

The fixed 23-customer example processes one savings decision per instructor
click. Each Next or Previous action runs inside the browser, so Streamlit does
not rerun between decisions. A browser-native SVG diagram pulses the candidate
customers, emphasizes their current sub-paths, and draws accepted customer
links smoothly. For visual clarity, depot links remain
hidden while the savings list is processed. A separate final click connects
the two end nodes of each completed customer sub-path to the depot. The savings
list uses **S. No.** for its ordered entries rather than calling them algorithm
steps. It remains
visible with accepted rows in green, rejected rows in red, and the current row
automatically centred. Customer demands appear in parentheses inside the nodes.
The final five route loads are 95, 90, 90, 90, and 95.

### Simplex Algorithm - Example 1

The Operations Research section begins with a fixed four-constraint
maximization example. Its 27 teaching states connect equality form, basic
variables, row 0, the ratio test, pivot operations, and optimality to a
synchronized feasible-region graph. Six deliberate pause questions support
classroom discussion. The BFS path is `(0, 0)` to `(4, 0)` to the optimum
`(3, 3/2)`, where `Z = 21`.

The landing page presents the model, then a full-width, left-aligned three-point
overview, then Start. During pivots, the current tableau stays above the next
tableau, matching notebook work; the next tableau develops row by row. The
optimality explanation retains the final tableau and graph. A separate final
Key takeaways state follows. These are reviewed teaching choices, not layouts
to replace automatically with a generic Results screen.

### Transportation Problem - Example 1

The warehouse-to-store example starts by checking that supply and demand both
total 125 cartons. It explains how a zero-cost dummy source or destination
would balance an unequal total. Choose the Northwest Corner Rule (NWCR),
Least Cost Method (LCM), or Vogel’s Approximation Method (VAM) to build an
initial basic feasible solution in the tableau.

Each walkthrough writes the basic-cell equations beside the tableau, fixes one
dual variable to zero, solves for the others one at a time, and computes the
reduced costs for the non-basic cells. The demonstration explains why those
reduced costs stay the same when a different dual variable is fixed for the
same basis. NWCR gives ₹1,180 and LCM gives ₹1,080. Both plans can be improved.
VAM gives ₹1,020, which the reduced-cost test certifies as optimal.

### Transportation Problem - Example 2

The S2–D4 cost drops from ₹7 to ₹5. The VAM walkthrough demonstrates the
tie-breaking order. Among rows and columns tied on penalty, compare the lowest
available transportation costs. Among candidate cells tied on cost, choose the
one permitting the largest allocation. If allocations also tie, choose the
topmost candidate, then the leftmost if needed. The initial solution costs ₹1,130.

Two UV iterations build the adjustment loop, explain how each turn preserves
supply or demand, and use a red dashed line to show where an alternative path
gets stuck. Each iteration lists the donor quantities, highlights the cell
that limits δ, and identifies the entering and leaving variables. The costs
progress from ₹1,130 to ₹1,030 to the optimal ₹1,020. The final note explains
how allowing the zero-reduced-cost variable `x23` to enter the basis gives
an alternate optimal solution at the same cost.

Both examples use Python to calculate the fixed teaching states and
browser-side playback for Previous and Next. The app embeds the problem data.
Local source slides in `My Teaching Materials/` are excluded from Git.

## Project structure

```text
Teaching-Tools/
|-- AGENTS.md
|-- app.py
|-- algorithms/
|   |-- clarke_wright.py
|   |-- consecutive_days_off.py
|   |-- johnson.py
|   |-- simplex.py
|   |-- single_processor.py
|   `-- transportation.py
|-- components/
|   |-- clarke_wright.py
|   |-- gantt.py
|   |-- simplex.py
|   |-- single_processor_gantt.py
|   |-- staffing.py
|   |-- transportation.py
|   |-- transportation_page.css
|   `-- transportation_player.html
|-- pages/
|   |-- clarke_wright.py
|   |-- consecutive_days_off.py
|   |-- home.py
|   |-- johnson_rule.py
|   |-- operations_research_home.py
|   |-- simplex_algorithm.py
|   |-- single_processor_sequencing.py
|   |-- transportation_problem_example_1.py
|   `-- transportation_problem_example_2.py
|-- tests/
|   |-- test_clarke_wright.py
|   |-- test_consecutive_days_off.py
|   |-- test_johnson.py
|   |-- test_simplex.py
|   |-- test_single_processor.py
|   `-- test_transportation.py
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

To run the app on the local review port without activating the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.headless true
```

Open [the local Simplex page](http://localhost:8502/simplex_algorithm).
Open [the local Transportation Example 1 page](http://localhost:8502/transportation_problem_example_1).
Open [the local Transportation Example 2 page](http://localhost:8502/transportation_problem_example_2).

Use the sidebar navigation to switch between demonstrations. All pages are
fixed demonstration mode: there are no editable inputs, quizzes, downloads, or
authentication.

## Classroom links

The sidebar separates the demonstrations into **Operations Management** and
**Operations Research**.

Operations Management:

- [Operations Management homepage](https://operationsmanagement.streamlit.app/)
- [Johnson's Rule](https://operationsmanagement.streamlit.app/johnsons_rule)
- [Scheduling Consecutive Days Off](https://operationsmanagement.streamlit.app/consecutive_days_off)
- [Single-Processor Sequencing](https://operationsmanagement.streamlit.app/single_processor_sequencing)
- [VRP: Clarke-Wright](https://operationsmanagement.streamlit.app/vrp_clarke_wright)

Operations Research:

- [Operations Research homepage](https://operationsmanagement.streamlit.app/operations_research)
- [Simplex Algorithm - Example 1](https://operationsmanagement.streamlit.app/simplex_algorithm)
- [Transportation Problem - Example 1](https://operationsmanagement.streamlit.app/transportation_problem_example_1)
- [Transportation Problem - Example 2](https://operationsmanagement.streamlit.app/transportation_problem_example_2)

## Release and display controls

- `app.py` explicitly registers the pages visible in the application.
- A demonstration uses staged views rather than one continuously expanding
  page. Preserve topic-specific teaching requirements, including retaining a
  tableau or graph while explaining the result.
- The active working data, current explanation, progress, and controls stay
  together within approximately one projector screen.
- Distinct conceptual actions use distinct clicks; all candidates and tie
  assumptions are shown before the update is applied.
- New fixed-data demonstrations compute and validate their full state sequence
  once in Python, then use browser-side JSON/SVG playback for step navigation
  and animation. Existing tools are not retrofitted unless explicitly requested.
- Chart labels must be reserved space outside data marks and checked at the
  actual display width.
- After changing an imported component, restart Streamlit before visual
  verification so cached modules do not hide the change.
- Verify the actual Streamlit route, not only isolated component screenshots.
  Check every state with realistic browser height and the sidebar both open and
  closed. Keep desktop teaching states on screen; on very small screens, prefer
  one controlled content scroll area with visible navigation to clipped text.

## Maintenance

The temporary scroll-all-states Simplex QA page has been retired. Keep focused
tests and the reusable state-rendering helper for future verification. Generated
review screenshots, temporary browser profiles, and Python caches are not release
assets and may be removed after review. Do not delete fixed-example data,
algorithm/component modules, tests, development configuration, or the local
virtual environment as part of cosmetic cleanup. Do not commit, push, or deploy
without an explicit request.

The detailed checklist and durable display rules are in
[CLASSROOM_DISPLAY_GUIDELINES.md](CLASSROOM_DISPLAY_GUIDELINES.md).
