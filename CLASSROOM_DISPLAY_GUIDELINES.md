# Classroom Display Guidelines

These standards apply to every algorithm demonstration added to this project.
They capture the display and interaction lessons established across the project,
including the repeated Simplex reviews. Read this document completely before
changing a demonstration; its checklist is a release gate, not optional advice.

## 1. Separate algorithm logic from presentation

- Keep algorithm, scheduling, and calculation logic outside Streamlit page
  code.
- Generate decisions and results programmatically; do not hard-code displayed
  steps.
- A display redesign must not silently change the algorithm, tie-breaking rule,
  data, or performance calculations.

## 2. Default interaction architecture for fixed-data demonstrations

Apply this architecture by default to every new fixed-data demonstration. Do
not retrofit an existing demonstration unless the user explicitly requests it.

When the tool starts, Python should:

- run the algorithm once and generate the complete sequence of intermediate
  states;
- perform all calculations, validation, and correctness checks; and
- serialize the state sequence to JSON for the display component.

After that initial computation, a browser-side JavaScript/SVG component should:

- handle Previous and Next navigation;
- animate and highlight the current decision; and
- update tables, routes, graphs, and other already-computed visual states.

Do not trigger a Streamlit/Python rerun for every demonstration step. Python
may rerun for initial load, Start or Restart, refresh, navigation, or when a
tool genuinely requires a new computation.

If a future tool has a separate user-input mode, Python may recompute after the
user submits new data. Once that new state sequence has been computed, use
browser-side step playback again wherever practical.

## 3. Use three staged views

Each demonstration should have mutually exclusive views rather than one page
that continuously expands.

1. **Problem view:** show the context, input data, concise algorithm description,
   and a clear Start button.
2. **Algorithm workspace:** show only the information required for the current
   decision. Keep the working data, partial solution, explanation, progress,
   and navigation controls together within approximately one projector screen.
3. **Results view:** normally replace the algorithm workspace after the final step. Show
   the final solution, visual schedule or chart, performance measures, and
   numerical calculations without repeating the working table.

This staging is not permission to change the pedagogy. If the approved teaching
flow needs the final tableau, graph, or other working evidence while explaining
the result, retain it. Simplex keeps the final tableau and graph through the
optimality explanation and then has a separate Key takeaways state.

On a landing page, use the reading order **problem/model → overview → Start**.
Place a multi-point overview in a full-width, left-aligned block below the model,
not squeezed into a right-hand button/action column. Verify its rendered position,
not merely that it precedes Start in the Python source. Allow natural landing-page
scrolling on small screens so the overview cannot hide the Start button.

Do not require the instructor to scroll between the current decision and the
data needed to explain it.

## 4. Make each interaction correspond to one conceptual step

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
- Preserve a reviewed baseline and its question → pause → answer progression.
  Do not target an arbitrary state count, rewrite unaffected explanations, or add
  a click solely to display an empty new table. Add states only when required by
  a requested conceptual distinction.
- Position can convey mathematical process. For successive Simplex tableaus,
  keep the current tableau above the next tableau, including on wide screens;
  reveal the new tableau row by row like notebook work. Do not silently substitute
  side-by-side tables to save space.
- Clarify genuine ambiguities that materially affect learning: revealing an
  answer early, changing table order, hiding evidence at the final state, adding
  terminology, or combining teaching steps. Proceed independently on minor
  spacing fixes; do not seek repeated approvals for them.
- Do not invent explanatory labels. Preserve approved terminology; for example,
  a non-applicable Simplex ratio is a dash, not an added "No bound" label.

## 5. Design for classroom projection

- Prefer a compact two-column algorithm workspace on wide screens: working data
  on one side and the partial solution, explanation, and controls on the other.
  This is a preference, not an override of a pedagogically significant arrangement.
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
- Budget for the browser's usable content height, not the physical monitor's
  resolution. Browser tabs, address/bookmark bars, the taskbar, sidebar, zoom, and
  Streamlit's toolbar reduce available space. Also check a reduced-height laptop
  viewport such as 1280 x 630 with the sidebar expanded.
- Use the actual available iframe/container height. Do not stack a fixed-height
  chart, fixed-height explanation and large controls until they exceed it. Remove
  excess padding and empty card space first; prioritize readable working data,
  a correctly proportioned graph, and complete teaching text over large buttons.
- Keep Previous/Next compact but fully visible and comfortably operable, including
  by touch. Reserve their space before allocating the content area. A button whose
  edge is visible but whose body is below the viewport is a failed layout.
- Constrain embedded workspaces to the available viewport and fit the visual's
  coordinate range to its actual content. Avoid blank canvas below or beside
  the data, and use the available horizontal width to separate crowded nodes.
- Reflow columns and sequence slots for narrow screens without clipping or
  horizontal page overflow.
- At laptop/projector widths, fit every teaching state without page scrolling,
  cropped explanations or hidden navigation. Never use `overflow: hidden` as a
  substitute for fitting the content. At phone widths where the material cannot
  fit legibly, use one controlled vertical content scroll area with navigation
  remaining visible; avoid several nested scrolling panels or tiny type.
- Test Start after scrolling the landing page and Restart after a long state.
  A previous scroll offset must not leave the heading or controls above the screen.
  Apply overflow rules by view; a scrollable landing page and a bounded playback
  workspace have different requirements.
- Use tabs or another staged control for distinct result components instead of
  stacking several large sections vertically.

## 6. Chart and Gantt standards

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
- Preserve graph aspect ratio; do not compress its vertical scale just to fit a
  card. Constraint equations should sit clear of, and where useful parallel to,
  their lines. Reserve space for corner/BFS labels, use restrained point and arrow
  sizes, and check collisions at every visited point, not only the initial graph.

## 7. Typography and mathematical explanations

- Use consistent font sizes, line heights, and weights for each role: page title,
  state heading, body text, equations, table cells, and graph labels. Do not make
  whole explanations bold. Use selective emphasis for the current decision.
- Do not solve overflow by shrinking crucial mathematics while leaving headings,
  padding, buttons or empty canvas oversized. Keep table entries and graph labels
  readable together; reflow before sacrificing legibility.
- Keep subscript, fraction, and equation rendering coherent throughout. Check
  line wrapping, operators, punctuation, and spaces around words such as "or".
  Put equivalent equations on one line when they fit; let them wrap naturally on
  a phone without running words into the mathematics.
- Indentation and row labels should connect calculations to their source rows.
  Preserve the approved explanation and use spacing/grouping to clarify it;
  layout work does not authorize adding teaching content.

## 8. Present results in teaching order

1. Final solution or sequence.
2. Visual schedule or chart comparison.
3. Performance measures and interpretation.
4. Numerical calculations showing the substituted values and result.

Definitions alone are insufficient. Show the actual processing totals,
completion times, denominators, arithmetic, units, and calculated values used
for makespan, idle time, utilization, flow time, or other reported measures.

## 9. Verification before handoff or deployment

- Run focused unit tests for the algorithm and expected fixed-example results.
- Exercise every presentation state, including Previous, Next, Restart, ties,
  the final step, and the transition to Results.
- Confirm that Problem, Algorithm, and Results views do not unintentionally
  appear together.
- Inspect the app at projector and narrow widths for overlap, clipping, and
  unnecessary scrolling.
- Review the actual live Streamlit route and its embedded component, not only
  standalone HTML, a scroll-all-states review page, or screenshots from another
  server/port. An HTTP 200 response proves availability, not visual correctness.
- Check every state forward and backward, including the longest explanation,
  stacked pivot tables, final graph/labels and results. Wait for transitions to
  settle before captures. Check both open and closed sidebars, representative
  laptop/projector, tablet and phone widths, and browser zoom/display scaling.
- Check the entire viewport in captures: toolbar clearance, graph proportions,
  complete description text, and fully visible controls. Source inspection and
  bounding-box checks complement visual review; neither replaces it.
- Report precisely what was checked. Emulated phone/tablet widths are responsive
  browser checks, not proof that a physical device was tested. Never claim public
  deployment verification from a local screenshot.
- Streamlit Community Cloud adds a hosting iframe and a bottom-right creator
  badge/popover that local runs do not have. Check real pointer clicks, not forced
  or scripted DOM clicks: the badge can intercept navigation even when its button
  is within the viewport. Reserve hosted-only footer clearance where needed; do
  not hide the hosting badge or change the local layout to compensate.
- After changing an imported display component, restart Streamlit before visual
  verification. Do not rely only on hot reload; it may retain an older imported
  module.
- Refresh the browser after the restart. Check the public app separately after
  an authorized deployment; do not commit, push, or deploy merely to verify work.
- Register only released algorithm pages in `app.py`.

## 10. Simplex review lessons and safe maintenance

These recurring failures explain why the preceding requirements are mandatory:

| Observed failure | Required correction |
| --- | --- |
| Overview stranded at the far right | Full-width overview below the model, followed by Start. |
| Toolbar clipping, or excessive blank space above the work | Container-level clearance; verify actual usable height rather than adding arbitrary title padding. |
| Description cut off and navigation barely clickable | Reserve compact control space, remove empty padding, and fit the complete text; never mask overflow. |
| Graph flattened while cards remain mostly empty | Preserve graph proportions and allocate space based on content. |
| Pivot tables moved side by side | Restore vertical notebook order and progressive row development. |
| Unrequested wording, labels or extra states | Preserve reviewed content; clarify consequential ambiguities instead of redesigning the lesson. |
| Inconsistent bolding, fractions or equation spacing | Consistent typographic roles, selective emphasis, and explicit equation-spacing checks. |
| QA screenshots differ from the instructor's page | Verify the actual route, sidebar, available height, zoom and settled state. |

Update these guidelines when a durable correction is learned, and keep README
and `AGENTS.md` aligned so future tasks explicitly read and apply them. Do not
turn topic-specific content into a universal teaching requirement.

After review, remove obsolete temporary screenshots, extraction files, browser
profiles and QA-only pages/registrations. Inspect references before deleting.
Retain finalized source/data, focused tests, required configuration and the local
environment. Do not refactor working algorithms or responsive components merely
for cosmetic cleanup; generated artifacts can be regenerated, deleted untracked
source cannot be recovered from Git.

## New-algorithm checklist

Before releasing a new demonstration, confirm:

- [ ] Algorithm logic and UI logic are separate.
- [ ] New fixed-data tools precompute states in Python and use browser-side
      step playback without per-step Streamlit reruns.
- [ ] Problem, Algorithm, and Results are staged views.
- [ ] Landing overview is in the intended reading order and not trapped in an
      action column; Start is reachable on small screens.
- [ ] The active decision and its supporting data fit together on one screen.
- [ ] Full explanations and compact controls are visible; graphs are not flattened.
- [ ] Pedagogically significant positioning and question/answer order are preserved.
- [ ] Typography, emphasis and mathematical spacing are coherent across all states.
- [ ] Distinct conceptual steps use distinct interactions.
- [ ] Tie behavior is visible and explained.
- [ ] Charts have readable labels with no overlap.
- [ ] Results show both values and numerical calculations.
- [ ] All navigation states and the final transition have been tested.
- [ ] Streamlit was restarted after shared-component changes.
- [ ] Actual local route checked with realistic height, open/closed sidebar,
      and laptop/projector, tablet and phone widths.
- [ ] Public app visually checked after deployment, when deployment is authorized.
