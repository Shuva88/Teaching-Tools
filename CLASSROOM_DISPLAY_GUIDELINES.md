# Classroom Display Guidelines

These standards apply to every algorithm demonstration added to this project.
They capture the display and interaction lessons established while developing
the Johnson's Rule demonstration.

## 1. Separate algorithm logic from presentation

- Keep algorithm, scheduling, and calculation logic outside Streamlit page
  code.
- Generate decisions and results programmatically; do not hard-code displayed
  steps.
- A display redesign must not silently change the algorithm, tie-breaking rule,
  data, or performance calculations.

## 2. Use three staged views

Each demonstration should have mutually exclusive views rather than one page
that continuously expands.

1. **Problem view:** show the context, input data, concise algorithm description,
   and a clear Start button.
2. **Algorithm workspace:** show only the information required for the current
   decision. Keep the working data, partial solution, explanation, progress,
   and navigation controls together within approximately one projector screen.
3. **Results view:** replace the algorithm workspace after the final step. Show
   the final solution, visual schedule or chart, performance measures, and
   numerical calculations without repeating the working table.

Do not require the instructor to scroll between the current decision and the
data needed to explain it.

## 3. Make each interaction correspond to one conceptual step

- Do not combine two important textbook steps into one click.
- Separate identifying or selecting the next item from applying the resulting
  placement or update when those are distinct concepts.
- Use short, textbook-adjacent language that students can follow while looking
  at the visual state.
- Highlight all current candidates, including ties, before applying the
  decision.
- Explain why tied alternatives remain valid and state the deterministic choice
  used by the demonstration.
- Grey out completed items only after their placement or update has occurred.
- Provide Previous, Next, and Restart controls. Keep them beside the current
  explanation rather than below a long history of steps.

## 4. Design for classroom projection

- Prefer a compact two-column algorithm workspace on wide screens: working data
  on one side and the partial solution, explanation, and controls on the other.
- Keep the current state visible; do not append every previous explanation.
- Do not spend vertical space on implementation commentary such as interaction
  mode, click mechanics, animation technology, or page-refresh behavior unless
  it directly teaches the algorithm.
- Preserve enough top clearance for Streamlit's fixed toolbar. The established
  project standard is `.block-container` top padding of `3.75rem !important` on
  desktop and `4rem !important` at widths up to 800px. Do not replace this with
  smaller page-specific padding or add compensating padding to an individual
  title. Check the first heading and adjacent controls below the toolbar at both
  widths.
- Use restrained headings, spacing, and card height so the workspace fits at
  common projector sizes such as 1366 x 768 or 1440 x 900.
- Constrain embedded workspaces to the available viewport and fit the visual's
  coordinate range to its actual content. Avoid blank canvas below or beside
  the data, and use the available horizontal width to separate crowded nodes.
- Reflow columns and sequence slots for narrow screens without clipping or
  horizontal page overflow.
- Use tabs or another staged control for distinct result components instead of
  stacking several large sections vertically.

## 5. Chart and Gantt standards

- Use the same time scale for schedules being compared.
- Place comparison charts side by side on wide screens when they remain
  readable.
- Label jobs directly on bars and keep job colors consistent across charts.
- Use concise axis labels; put fuller descriptions in nearby text or hover
  details.
- Keep reference labels outside the data marks. In particular, place makespan
  text above the plotting area using paper-relative coordinates and reserve
  enough top margin so it never overlaps a resource bar.
- Retain the reference line at the exact calculated value even when its label
  is moved.
- Verify short-duration bars, endpoint labels, and annotations at the actual
  deployed chart width.

## 6. Present results in teaching order

1. Final solution or sequence.
2. Visual schedule or chart comparison.
3. Performance measures and interpretation.
4. Numerical calculations showing the substituted values and result.

Definitions alone are insufficient. Show the actual processing totals,
completion times, denominators, arithmetic, units, and calculated values used
for makespan, idle time, utilization, flow time, or other reported measures.

## 7. Verification before deployment

- Run focused unit tests for the algorithm and expected fixed-example results.
- Exercise every presentation state, including Previous, Next, Restart, ties,
  the final step, and the transition to Results.
- Confirm that Problem, Algorithm, and Results views do not unintentionally
  appear together.
- Inspect the app at projector and narrow widths for overlap, clipping, and
  unnecessary scrolling.
- After changing an imported display component, restart Streamlit before visual
  verification. Do not rely only on hot reload; it may retain an older imported
  module.
- Refresh the browser after the restart and verify the deployed app separately
  after pushing changes.
- Register only released algorithm pages in `app.py`.

## New-algorithm checklist

Before releasing a new demonstration, confirm:

- [ ] Algorithm logic and UI logic are separate.
- [ ] Problem, Algorithm, and Results are staged views.
- [ ] The active decision and its supporting data fit together on one screen.
- [ ] Distinct conceptual steps use distinct interactions.
- [ ] Tie behavior is visible and explained.
- [ ] Charts have readable labels with no overlap.
- [ ] Results show both values and numerical calculations.
- [ ] All navigation states and the final transition have been tested.
- [ ] Streamlit was restarted after shared-component changes.
- [ ] The deployed app was visually checked at its public URL.
