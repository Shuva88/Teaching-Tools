"""Exact state generation for Simplex Algorithm - Example 1."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

COLUMNS = ("Z", "x1", "x2", "s1", "s2", "s3", "s4", "RHS")


@dataclass(frozen=True)
class Tableau:
    basic_variables: tuple[str, ...]
    rows: tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class BasicFeasibleSolution:
    values: tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]
    objective: Fraction
    label: str

    @property
    def x1(self) -> Fraction:
        return self.values[0]

    @property
    def x2(self) -> Fraction:
        return self.values[1]


@dataclass(frozen=True)
class HighlightSpec:
    row_zero: bool = False
    entering_column: str | None = None
    leaving_row: str | None = None
    pivot_row: str | None = None
    pivot_column: str | None = None
    transformed_rows: tuple[str, ...] = ()
    ratio_rows: tuple[str, ...] = ()
    excluded_rows: tuple[str, ...] = ()
    basic_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class TeachingState:
    state_id: str
    section: str
    title: str
    kind: str
    body_html: str
    tableau: Tableau | None
    panel_title: str
    panel_html: str | None
    highlights: HighlightSpec
    ratios: tuple[tuple[str, str], ...]
    path: tuple[BasicFeasibleSolution, ...]
    reference_tableau: Tableau | None = None
    revealed_rows: tuple[str, ...] = ()
    workspace_hidden: bool = False
    is_final: bool = False


@dataclass(frozen=True)
class SimplexDemonstration:
    states: tuple[TeachingState, ...]
    initial_tableau: Tableau
    first_tableau: Tableau
    final_tableau: Tableau
    first_pivot_stages: tuple[Tableau, ...]
    second_pivot_stages: tuple[Tableau, ...]


ORIGINAL_MODEL_HTML = """
<div class="equation-card">
  <div class="model-line objective"><span>max</span><span>Z = 5x<sub>1</sub> + 4x<sub>2</sub></span></div>
  <div class="model-line"><span class="model-operator">s.t.</span><span>6x<sub>1</sub> + 4x<sub>2</sub> &le; 24</span></div>
  <div class="model-line"><span></span><span>x<sub>1</sub> + 2x<sub>2</sub> &le; 6</span></div>
  <div class="model-line"><span></span><span>-x<sub>1</sub> + x<sub>2</sub> &le; 1</span></div>
  <div class="model-line"><span></span><span>x<sub>2</sub> &le; 2</span></div>
  <div class="model-line"><span></span><span>x<sub>1</sub>, x<sub>2</sub> &ge; 0</span></div>
</div>
"""

EQUALITY_FORM_HTML = """
<div class="equation-card compact-equations">
  <div class="objective-row first-equation">Z - 5x<sub>1</sub> - 4x<sub>2</sub> = 0</div>
  <div>6x<sub>1</sub> + 4x<sub>2</sub> + s<sub>1</sub> = 24</div>
  <div>x<sub>1</sub> + 2x<sub>2</sub> + s<sub>2</sub> = 6</div>
  <div>-x<sub>1</sub> + x<sub>2</sub> + s<sub>3</sub> = 1</div>
  <div>x<sub>2</sub> + s<sub>4</sub> = 2</div>
</div>
"""


def _f(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def initial_tableau() -> Tableau:
    return Tableau(
        basic_variables=("Z", "s1", "s2", "s3", "s4"),
        rows=tuple(
            tuple(_f(value) for value in row)
            for row in (
                (1, -5, -4, 0, 0, 0, 0, 0),
                (0, 6, 4, 1, 0, 0, 0, 24),
                (0, 1, 2, 0, 1, 0, 0, 6),
                (0, -1, 1, 0, 0, 1, 0, 1),
                (0, 0, 1, 0, 0, 0, 1, 2),
            )
        ),
    )


def _replace_row(
    tableau: Tableau,
    row_index: int,
    new_row: Iterable[Fraction],
    *,
    new_basic_variable: str | None = None,
) -> Tableau:
    rows = list(tableau.rows)
    rows[row_index] = tuple(new_row)
    basic_variables = list(tableau.basic_variables)
    if new_basic_variable is not None:
        basic_variables[row_index] = new_basic_variable
    return Tableau(tuple(basic_variables), tuple(rows))


def _scale_row(
    tableau: Tableau,
    row_index: int,
    multiplier: Fraction,
    *,
    new_basic_variable: str | None = None,
) -> Tableau:
    return _replace_row(
        tableau,
        row_index,
        (value * multiplier for value in tableau.rows[row_index]),
        new_basic_variable=new_basic_variable,
    )


def _add_row_multiple(
    tableau: Tableau,
    target_index: int,
    source_index: int,
    multiplier: Fraction,
) -> Tableau:
    return _replace_row(
        tableau,
        target_index,
        (
            left + multiplier * right
            for left, right in zip(tableau.rows[target_index], tableau.rows[source_index])
        ),
    )


def first_pivot_tableaus(tableau: Tableau | None = None) -> tuple[Tableau, ...]:
    start = tableau or initial_tableau()
    row_one = _scale_row(start, 1, Fraction(1, 6), new_basic_variable="x1")
    row_zero = _add_row_multiple(row_one, 0, 1, Fraction(5))
    row_two = _add_row_multiple(row_zero, 2, 1, Fraction(-1))
    row_three = _add_row_multiple(row_two, 3, 1, Fraction(1))
    row_four = _add_row_multiple(row_three, 4, 1, Fraction(0))
    return row_one, row_zero, row_two, row_three, row_four


def second_pivot_tableaus(tableau: Tableau) -> tuple[Tableau, ...]:
    row_two = _scale_row(tableau, 2, Fraction(3, 4), new_basic_variable="x2")
    row_zero = _add_row_multiple(row_two, 0, 2, Fraction(2, 3))
    row_one = _add_row_multiple(row_zero, 1, 2, Fraction(-2, 3))
    row_three = _add_row_multiple(row_one, 3, 2, Fraction(-5, 3))
    row_four = _add_row_multiple(row_three, 4, 2, Fraction(-1))
    return row_two, row_zero, row_one, row_three, row_four


def _state(
    state_id: str,
    section: str,
    title: str,
    kind: str,
    body_html: str,
    *,
    tableau: Tableau | None,
    path: tuple[BasicFeasibleSolution, ...],
    panel_title: str = "Simplex tableau",
    panel_html: str | None = None,
    highlights: HighlightSpec | None = None,
    ratios: tuple[tuple[str, str], ...] = (),
    reference_tableau: Tableau | None = None,
    revealed_rows: tuple[str, ...] = (),
    workspace_hidden: bool = False,
    is_final: bool = False,
) -> TeachingState:
    return TeachingState(
        state_id=state_id,
        section=section,
        title=title,
        kind=kind,
        body_html=body_html,
        tableau=tableau,
        panel_title=panel_title,
        panel_html=panel_html,
        highlights=highlights or HighlightSpec(),
        ratios=ratios,
        path=path,
        reference_tableau=reference_tableau,
        revealed_rows=revealed_rows,
        workspace_hidden=workspace_hidden,
        is_final=is_final,
    )


def _build_reviewed_baseline() -> SimplexDemonstration:
    initial = initial_tableau()
    first_stages = first_pivot_tableaus(initial)
    first = first_stages[-1]
    second_stages = second_pivot_tableaus(first)
    final = second_stages[-1]

    origin = BasicFeasibleSolution(
        (Fraction(0), Fraction(0), Fraction(24), Fraction(6), Fraction(1), Fraction(2)),
        Fraction(0), "(0, 0)",
    )
    first_bfs = BasicFeasibleSolution(
        (Fraction(4), Fraction(0), Fraction(0), Fraction(2), Fraction(5), Fraction(2)),
        Fraction(20), "(4, 0)",
    )
    optimum = BasicFeasibleSolution(
        (Fraction(3), Fraction(3, 2), Fraction(0), Fraction(0), Fraction(5, 2), Fraction(1, 2)),
        Fraction(21), "(3, 3/2)",
    )
    no_path: tuple[BasicFeasibleSolution, ...] = ()
    at_origin = (origin,)
    first_path = (origin, first_bfs)
    full_path = (origin, first_bfs, optimum)

    first_ratios = (
        ("s1", "24 / 6 = 4"), ("s2", "6 / 1 = 6"),
        ("s3", "—"), ("s4", "—"),
    )
    second_ratios = (
        ("x1", "4 / (2/3) = 6"), ("s2", "2 / (4/3) = 3/2"),
        ("s3", "5 / (5/3) = 3"), ("s4", "2 / 1 = 2"),
    )

    states = (
        _state(
            "S01", "Problem", "Original linear program", "observation",
            "The shaded region contains the decision-space points that satisfy all four structural constraints and nonnegativity.",
            tableau=None, panel_title="Original model", panel_html=ORIGINAL_MODEL_HTML, path=no_path,
        ),
        _state(
            "S02", "Initial solution", "Equality form and the initial BFS", "explanation",
            "Equality form makes an initial BFS easy to obtain. Taking x<sub>1</sub> = x<sub>2</sub> = 0 as the nonbasic variables gives s<sub>1</sub> = 24, s<sub>2</sub> = 6, s<sub>3</sub> = 1, and s<sub>4</sub> = 2 as the initial basic variables.<div class=\"bfs-equation\">(x<sub>1</sub>,x<sub>2</sub>,s<sub>1</sub>,s<sub>2</sub>,s<sub>3</sub>,s<sub>4</sub>) = (0,0,24,6,1,2) &nbsp; · &nbsp; Z = 0</div>",
            tableau=None, panel_title="Equality form", panel_html=EQUALITY_FORM_HTML, path=at_origin,
        ),
        _state(
            "S03", "Initial tableau", "The tableau records the equations", "explanation",
            "The tableau is another representation of the equations: each entry is the coefficient of the variable at the top of its column, and the right-hand side appears under RHS. Its row operations are the familiar operations used to solve simultaneous equations: multiply a complete equation by a number, then add or subtract complete equations without changing the solution represented by the system.",
            tableau=initial, path=at_origin,
        ),
        _state(
            "S04", "Initial tableau", "Recognize the basic-variable columns", "explanation",
            "Each current basic-variable column has a 1 in the row represented by that variable and 0 everywhere else. This structure lets us read each basic variable directly from the RHS when the nonbasic variables are zero. We will deliberately create the same structure when a new variable enters the basis.",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(basic_columns=("s1", "s2", "s3", "s4")),
        ),
        _state(
            "S05", "First iteration", "Why can a negative row-0 coefficient indicate improvement?", "question",
            "<b>Why can a negative coefficient in row 0 indicate that the objective can be improved?</b><span class=\"pause\">Pause and think before pressing Next.</span>",
            tableau=initial, path=at_origin, highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S06", "First iteration", "x₁ enters the basis", "explanation",
            "Rewrite Z - 5x<sub>1</sub> - 4x<sub>2</sub> = 0 as <b>Z = 5x<sub>1</sub> + 4x<sub>2</sub></b>. Starting from x<sub>1</sub> = x<sub>2</sub> = 0, increasing either variable increases Z. A one-unit increase in x<sub>1</sub> improves Z by 5, compared with 4 for x<sub>2</sub>. Therefore x<sub>1</sub>, with the most negative row-0 coefficient, enters.",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(row_zero=True, entering_column="x1"),
        ),
        _state(
            "S07", "First ratio test", "Why can x₁ not keep increasing?", "question",
            "<b>If increasing x<sub>1</sub> improves Z, why can we not keep increasing x<sub>1</sub>?</b><span class=\"pause\">Pause and think before pressing Next.</span>",
            tableau=initial, path=at_origin, highlights=HighlightSpec(entering_column="x1"),
        ),
        _state(
            "S08", "First ratio test", "Nonnegativity creates the allowable increase", "explanation",
            """
<div class="ratio-explanation">
  <div><b>s<sub>1</sub> = 24 - 6x<sub>1</sub></b><br>s<sub>1</sub> ≥ 0 ⇒ x<sub>1</sub> ≤ 4</div>
  <div><b>s<sub>2</sub> = 6 - x<sub>1</sub></b><br>s<sub>2</sub> ≥ 0 ⇒ x<sub>1</sub> ≤ 6</div>
  <div><b>s<sub>3</sub> = 1 + x<sub>1</sub></b><br>It increases, so it creates no upper bound.</div>
  <div><b>s<sub>4</sub> = 2</b><br>It is unaffected, so it creates no upper bound.</div>
</div>
The x<sub>1</sub> column is 6, 1, -1, 0. A positive entry means the basic variable decreases and may reach zero; a negative entry here means it increases; a zero means it is unaffected. Thus only 24/6 = 4 and 6/1 = 6 are valid bounds. The minimum, 4, keeps every current basic variable nonnegative. Row 0 is excluded because it describes objective change, whereas the constraint rows protect basic-variable feasibility. The ratio test accounts for nonnegativity conditions that are not separate tableau rows.
""",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(
                row_zero=True, entering_column="x1", ratio_rows=("s1", "s2"),
                excluded_rows=("s3", "s4"),
            ), ratios=first_ratios,
        ),
        _state(
            "S09", "First ratio test", "s₁ leaves and x₁ enters", "explanation",
            "The smallest valid ratio is 4, so x<sub>1</sub> can increase only to 4. Then <b>s<sub>1</sub> = 24 - 6(4) = 0</b>. s<sub>1</sub> is the first current basic variable to reach zero; therefore s<sub>1</sub> leaves, x<sub>1</sub> enters, and the pivot element is 6.",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(
                entering_column="x1", leaving_row="s1", pivot_row="s1",
                pivot_column="x1", ratio_rows=("s1", "s2"), excluded_rows=("s3", "s4"),
            ), ratios=first_ratios,
        ),
        _state(
            "S10", "First pivot", "Make the pivot entry equal to 1", "operation",
            "x<sub>1</sub> is becoming basic, so its column must have a 1 in its own row and 0 everywhere else. The pivot is 6, so first use <b>R<sub>1</sub>′ = (1/6)R<sub>1</sub></b> to make that entry 1.",
            tableau=first_stages[0], path=at_origin,
            highlights=HighlightSpec(
                entering_column="x1", pivot_row="x1", pivot_column="x1",
                transformed_rows=("x1",),
            ),
        ),
        _state(
            "S11", "First pivot", "Make the row-0 entry equal to 0", "operation",
            "Now make every other x<sub>1</sub>-column entry 0, working downward. First use <b>R<sub>0</sub>′ = R<sub>0</sub> + 5R<sub>1</sub>′</b>. These are the same elimination operations used with simultaneous equations: complete rows are transformed while the solution set is preserved.",
            tableau=first_stages[1], path=at_origin,
            highlights=HighlightSpec(entering_column="x1", transformed_rows=("Z",)),
        ),
        _state(
            "S12", "First pivot", "Continue down the x₁ column", "operation",
            "Use <b>R<sub>2</sub>′ = R<sub>2</sub> - R<sub>1</sub>′</b>. The x<sub>1</sub> entry in the s<sub>2</sub> row is now 0.",
            tableau=first_stages[2], path=at_origin,
            highlights=HighlightSpec(entering_column="x1", transformed_rows=("s2",)),
        ),
        _state(
            "S13", "First pivot", "Complete the x₁ column and read the new BFS", "operation",
            "Use <b>R<sub>3</sub>′ = R<sub>3</sub> + R<sub>1</sub>′</b>; R<sub>4</sub>′ = R<sub>4</sub> because its x<sub>1</sub> entry is already 0. The x<sub>1</sub> column is now 0, 1, 0, 0, 0.<div class=\"bfs-equation\">Current BFS: (x<sub>1</sub>,x<sub>2</sub>,s<sub>1</sub>,s<sub>2</sub>,s<sub>3</sub>,s<sub>4</sub>) = (4,0,0,2,5,2) &nbsp; · &nbsp; Z = 20</div>x<sub>1</sub> has entered and s<sub>1</sub> has left. Geometrically, the new BFS is the adjacent corner point (4, 0).",
            tableau=first, path=first_path,
            highlights=HighlightSpec(entering_column="x1", transformed_rows=("s3", "s4")),
        ),
        _state(
            "S14", "Second iteration", "Have we reached the optimum?", "question",
            "<b>Have we reached the optimum?</b><span class=\"pause\">Pause and think before pressing Next.</span>",
            tableau=first, path=first_path, highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S15", "Second iteration", "x₂ can still improve the objective", "explanation",
            "Row 0 is Z - (2/3)x<sub>2</sub> + (5/6)s<sub>1</sub> = 20. Rewrite it as <b>Z = 20 + (2/3)x<sub>2</sub> - (5/6)s<sub>1</sub></b>. x<sub>2</sub> is nonbasic and currently zero; increasing it can still increase Z. Therefore the current BFS is not optimal and x<sub>2</sub> enters.",
            tableau=first, path=first_path,
            highlights=HighlightSpec(row_zero=True, entering_column="x2"),
        ),
        _state(
            "S16", "Second ratio test", "s₂ leaves and x₂ enters", "explanation",
            "The valid ratios are 4/(2/3) = 6, 2/(4/3) = 3/2, 5/(5/3) = 3, and 2/1 = 2. The smallest is <b>3/2</b>, so s<sub>2</sub> reaches zero first. Therefore s<sub>2</sub> leaves, x<sub>2</sub> enters, and the pivot element is 4/3.",
            tableau=first, path=first_path,
            highlights=HighlightSpec(
                entering_column="x2", leaving_row="s2", pivot_row="s2",
                pivot_column="x2", ratio_rows=("x1", "s2", "s3", "s4"),
            ), ratios=second_ratios,
        ),
        _state(
            "S17", "Second pivot", "Make the second pivot entry equal to 1", "operation",
            "x<sub>2</sub> is becoming basic, so its column must have a 1 in the x<sub>2</sub> row and 0 everywhere else. First use <b>R<sub>2</sub>″ = (3/4)R<sub>2</sub>′</b> to make the pivot entry 1.",
            tableau=second_stages[0], path=first_path,
            highlights=HighlightSpec(
                entering_column="x2", pivot_row="x2", pivot_column="x2",
                transformed_rows=("x2",),
            ),
        ),
        _state(
            "S18", "Second pivot", "Create zeros from row 0 downward", "operation",
            "Use <b>R<sub>0</sub>″ = R<sub>0</sub>′ + (2/3)R<sub>2</sub>″</b>, then <b>R<sub>1</sub>″ = R<sub>1</sub>′ - (2/3)R<sub>2</sub>″</b>. The row-0 and x<sub>1</sub>-row entries in the x<sub>2</sub> column are now 0.",
            tableau=second_stages[2], path=first_path,
            highlights=HighlightSpec(entering_column="x2", transformed_rows=("Z", "x1")),
        ),
        _state(
            "S19", "Second pivot", "Complete the x₂ column and the simplex path", "operation",
            "Use <b>R<sub>3</sub>″ = R<sub>3</sub>′ - (5/3)R<sub>2</sub>″</b> and <b>R<sub>4</sub>″ = R<sub>4</sub>′ - R<sub>2</sub>″</b>. The x<sub>2</sub> column is now 0, 0, 1, 0, 0. The completed path is (0,0) → (4,0) → (3,3/2).",
            tableau=final, path=full_path,
            highlights=HighlightSpec(entering_column="x2", transformed_rows=("s3", "s4")),
        ),
        _state(
            "S20", "Final tableau", "Reconstruct the equations before reading the solution", "explanation",
            """
<div class="final-equations">
  <div>Z + (3/4)s<sub>1</sub> + (1/2)s<sub>2</sub> = 21</div>
  <div>x<sub>1</sub> + (1/4)s<sub>1</sub> - (1/2)s<sub>2</sub> = 3</div>
  <div>x<sub>2</sub> - (1/8)s<sub>1</sub> + (3/4)s<sub>2</sub> = 3/2</div>
  <div>s<sub>3</sub> + (3/8)s<sub>1</sub> - (5/4)s<sub>2</sub> = 5/2</div>
  <div>s<sub>4</sub> + (1/8)s<sub>1</sub> - (3/4)s<sub>2</sub> = 1/2</div>
</div>
The basic variables are x<sub>1</sub>, x<sub>2</sub>, s<sub>3</sub>, and s<sub>4</sub>; the nonbasic variables are s<sub>1</sub> and s<sub>2</sub>. Setting s<sub>1</sub> = s<sub>2</sub> = 0 gives x<sub>1</sub> = 3, x<sub>2</sub> = 3/2, s<sub>3</sub> = 5/2, and s<sub>4</sub> = 1/2. Each basic-variable column has a 1 in its own row and zeros elsewhere, so its value is the RHS when the nonbasic variables are zero.
""",
            tableau=final, path=full_path,
            highlights=HighlightSpec(basic_columns=("x1", "x2", "s3", "s4")),
        ),
        _state(
            "S21", "Optimality", "How do we know this solution is optimal?", "question",
            "<b>How do we know this solution is optimal?</b><span class=\"pause\">Pause and think before pressing Next.</span>",
            tableau=final, path=full_path, highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S22", "Optimality", "Optimal solution and takeaway", "result",
            """
<div class="result-strip"><b>x<sub>1</sub> = 3</b><b>x<sub>2</sub> = 3/2</b><b>Z = 21</b><span>s<sub>1</sub> = 0, s<sub>2</sub> = 0, s<sub>3</sub> = 5/2, s<sub>4</sub> = 1/2</span></div>
<div class="optimality">Z + (3/4)s<sub>1</sub> + (1/2)s<sub>2</sub> = 21, so Z = 21 - (3/4)s<sub>1</sub> - (1/2)s<sub>2</sub>. Increasing either nonbasic variable from zero would decrease Z. Equivalently, row 0 has no negative coefficient, so no nonbasic variable can improve the objective.</div>
<div class="takeaway-grid">
  <div>Equality form gives a convenient initial BFS.</div>
  <div>The tableau is another representation of the equations.</div>
  <div>Row 0 chooses the entering variable; the ratio test preserves nonnegativity.</div>
  <div>Pivot operations create a basic-variable column with one 1 and zeros elsewhere.</div>
  <div>When no nonbasic variable can improve the objective, the current BFS is optimal.</div>
</div>
""",
            tableau=final, path=full_path,
            highlights=HighlightSpec(row_zero=True), is_final=True,
        ),
    )

    return SimplexDemonstration(
        states, initial, first, final, first_stages, second_stages,
    )


def build_simplex_demonstration() -> SimplexDemonstration:
    """Apply the requested focused revisions to the reviewed 22-state baseline."""

    baseline = _build_reviewed_baseline()
    original = baseline.states
    initial = baseline.initial_tableau
    first = baseline.first_tableau
    final = baseline.final_tableau
    first_stages = baseline.first_pivot_stages
    second_stages = baseline.second_pivot_stages

    no_path = original[0].path
    at_origin = original[1].path
    first_path = original[12].path
    full_path = original[18].path

    first_ratios = (
        ("s1", "24 / 6 = 4"),
        ("s2", "6 / 1 = 6"),
        ("s3", "—"),
        ("s4", "—"),
    )
    positive_ratios = (
        ("s1", "24 / 6 = 4"),
        ("s2", "6 / 1 = 6"),
    )
    second_ratios = (
        ("x1", "4 / (2/3) = 6"),
        ("s2", "2 / (4/3) = 3/2"),
        ("s3", "5 / (5/3) = 3"),
        ("s4", "2 / 1 = 2"),
    )

    states = (
        original[0],
        _state(
            "S02", "Initial solution", "Start from an initial basic feasible solution (BFS)", "explanation",
            """
Equality form makes an initial BFS easy to obtain. Taking x<sub>1</sub> = x<sub>2</sub> = 0 as the nonbasic variables gives s<sub>1</sub> = 24, s<sub>2</sub> = 6, s<sub>3</sub> = 1, and s<sub>4</sub> = 2 as the initial basic variables.
<div class="bfs-equation">(x<sub>1</sub>, x<sub>2</sub>, s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>, s<sub>4</sub>) = (0, 0, 24, 6, 1, 2)<br>Z = 0</div>
""",
            tableau=None, panel_title="Equality form", panel_html=EQUALITY_FORM_HTML, path=at_origin,
        ),
        _state(
            "S03", "Initial tableau", "The tableau records the equations", "explanation",
            "Note that the tableau is just another representation of these equations. Each number is the coefficient of the variable named at the top of its column; the right-hand side remains in the RHS column.<br><br>The row operations that we will use are the same type of operations used to solve simultaneous equations by elimination: we multiply a complete equation by a number or add/subtract complete equations without changing the solution.",
            tableau=initial, path=at_origin,
        ),
        _state(
            "S04", "Initial tableau", "Recognize the basic-variable columns", "explanation",
            "Notice the columns of the current basic variables s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub> and s<sub>4</sub>. Each has a 1 in the row represented by that variable and 0 everywhere else. When a new variable enters the basis, we will create the same 1-and-0 column structure for it.<div class=\"concept-note\"><b>Note about Z:</b> Z is an auxiliary variable used to represent the objective equation in the tableau. It remains in the basis throughout, but we do not count it among the basic variables of the BFS. Its row tracks the objective value and helps identify improving nonbasic variables.</div>",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(basic_columns=("s1", "s2", "s3", "s4")),
        ),
        _state(
            "S05", "First iteration", "We now need to choose an incoming variable (i.e., a nonbasic variable) to enter the basis", "question",
            'Why can a negative coefficient in row 0 indicate improvement for a maximization objective?<span class="pause">Pause and think before pressing Next.</span>',
            tableau=initial, path=at_origin, highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S06", "First iteration", "x₁ enters the basis", "explanation",
            "Row 0 represents the equation Z - 5x<sub>1</sub> - 4x<sub>2</sub> = 0, which can be rewritten as Z = 5x<sub>1</sub> + 4x<sub>2</sub>.<br><br>Clearly, an increase in x<sub>1</sub> or x<sub>2</sub> increases Z. The slack variables s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub> and s<sub>4</sub> have coefficient 0 in the objective and therefore do not directly increase Z.<br><br>In our tableau convention, x<sub>1</sub> and x<sub>2</sub> therefore appear with negative coefficients in row 0.<br><br>A one-unit increase in x<sub>1</sub> improves Z by 5, compared with 4 for x<sub>2</sub>. Therefore x<sub>1</sub>, corresponding to the most negative row-0 coefficient, enters the basis.",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(row_zero=True, entering_column="x1"),
        ),
        _state(
            "S07", "First ratio test", "Choose an outgoing basic variable to leave the basis", "question",
            'Why can x₁ not keep increasing?<span class="pause">Pause and think before pressing Next.</span>',
            tableau=initial, path=at_origin, highlights=HighlightSpec(entering_column="x1"),
        ),
        _state(
            "S08", "First ratio test", "How do the positive coefficients restrict x₁?", "explanation",
            """
The first, second, third and fourth constraint rows of the tableau represent the equations for s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub> and s<sub>4</sub> respectively.
<br><br>At the current BFS, x<sub>1</sub> = x<sub>2</sub> = 0. We now increase x<sub>1</sub> while keeping the other nonbasic variable x<sub>2</sub> at 0.
<div class="ratio-explanation two-cards">
  <div><div class="ratio-row-label">From Row 1 we have:</div><div class="ratio-equations">6x<sub>1</sub> + 4x<sub>2</sub> + s<sub>1</sub> = 24<br>With x<sub>2</sub> = 0:<br>s<sub>1</sub> = 24 - 6x<sub>1</sub><br>Since s<sub>1</sub> &ge; 0:<br>x<sub>1</sub> &le; 4<br>Tableau ratio: 24/6 = 4</div></div>
  <div><div class="ratio-row-label">From Row 2 we have:</div><div class="ratio-equations">x<sub>1</sub> + 2x<sub>2</sub> + s<sub>2</sub> = 6<br>With x<sub>2</sub> = 0:<br>s<sub>2</sub> = 6 - x<sub>1</sub><br>Since s<sub>2</sub> &ge; 0:<br>x<sub>1</sub> &le; 6<br>Tableau ratio: 6/1 = 6</div></div>
</div>
The positive entries 6 and 1 in the x<sub>1</sub> column mean that s<sub>1</sub> and s<sub>2</sub> decrease as x<sub>1</sub> increases. Thus, s<sub>1</sub> and s<sub>2</sub> restrict how far x<sub>1</sub> can increase and, in this case, the limit is 4; that is, x<sub>1</sub> &le; 4.
""",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(entering_column="x1", ratio_rows=("s1", "s2")),
            ratios=positive_ratios,
        ),
        _state(
            "S09", "First ratio test", "Why are the other entries not used in the ratio test?", "explanation",
            """
<div class="ratio-explanation two-cards">
  <div><div class="ratio-row-label">From Row 3 we have:</div><div class="ratio-equations">-x<sub>1</sub> + x<sub>2</sub> + s<sub>3</sub> = 1<br>With x<sub>2</sub> = 0:<br>s<sub>3</sub> = 1 + x<sub>1</sub></div><div class="ratio-conclusion">As x<sub>1</sub> increases, s<sub>3</sub> increases. Therefore this row does not restrict how far x<sub>1</sub> can increase. This corresponds to the -1 entry in the x<sub>1</sub> column.</div></div>
  <div><div class="ratio-row-label">From Row 4 we have:</div><div class="ratio-equations">x<sub>2</sub> + s<sub>4</sub> = 2<br>With x<sub>2</sub> = 0:<br>s<sub>4</sub> = 2</div><div class="ratio-conclusion">Changing x<sub>1</sub> does not change s<sub>4</sub>. Therefore this row also does not restrict how far x<sub>1</sub> can increase. This corresponds to the 0 entry in the x<sub>1</sub> column.</div></div>
</div>
<div class="ratio-note">Note that Row 0 is excluded from the ratio test because it tracks the objective, not a basic variable. The ratio test uses only constraint rows to ensure that the current basic variables remain nonnegative, as required by the model's non-negativity constraints.</div>
<div class="ratio-note">Thus, since the minimum ratio is 4 in this case, x<sub>1</sub> can increase only up to 4 without making a current basic variable negative.</div>
""",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(
                row_zero=True, entering_column="x1", ratio_rows=("s1", "s2"),
                excluded_rows=("s3", "s4"),
            ),
            ratios=first_ratios,
        ),
        _state(
            "S10", "First ratio test", "s₁ leaves and x₁ enters", "explanation",
            "When x<sub>1</sub> reaches 4,<br><br>s<sub>1</sub> = 24 - 6(4) = 0.<br><br>Thus s<sub>1</sub> is the first current basic variable to reach zero.<br><br>Therefore s<sub>1</sub> leaves the basis and x<sub>1</sub> enters the basis. The pivot element is 6.",
            tableau=initial, path=at_origin,
            highlights=HighlightSpec(
                entering_column="x1", leaving_row="s1", pivot_row="s1",
                pivot_column="x1", ratio_rows=("s1", "s2"), excluded_rows=("s3", "s4"),
            ),
            ratios=first_ratios,
        ),
        _state(
            "S11", "First pivot", "Make the pivot entry equal to 1", "operation",
            "x<sub>1</sub> is becoming a basic variable. Its column must therefore have a 1 in the x<sub>1</sub> row and 0 everywhere else, just like the columns of the existing basic variables.<br><br>The pivot entry is 6. First make it equal to 1.<div class=\"decision-equation\">R<sub>1</sub>&prime; = (1/6)R<sub>1</sub></div><br>These are the same row operations used when solving two simultaneous equations by elimination. We operate on the complete equations so that the solution represented by the system is preserved.",
            tableau=first_stages[0], reference_tableau=initial, revealed_rows=("x1",), path=at_origin,
            highlights=HighlightSpec(
                entering_column="x1", pivot_row="s1", pivot_column="x1",
                transformed_rows=("x1",),
            ),
        ),
        _state(
            "S12", "First pivot", "Make the row-0 entry equal to 0", "operation",
            "Now start from row 0 and make the remaining entries in the x<sub>1</sub> column equal to 0.<br><br>The current x<sub>1</sub> entry in the Z row (i.e., row 0) is -5, while the pivot-row entry is 1. Add 5 times the pivot row so that<div class=\"decision-equation\">-5 + 5(1) = 0</div>Therefore, use<div class=\"decision-equation\">R<sub>0</sub>&prime; = R<sub>0</sub> + 5R<sub>1</sub>&prime;</div><div class=\"concept-note\"><b>General idea:</b> use the pivot row to cancel the current entry in the incoming-variable column.</div>",
            tableau=first_stages[1], reference_tableau=initial, revealed_rows=("x1", "Z"), path=at_origin,
            highlights=HighlightSpec(entering_column="x1", transformed_rows=("Z",)),
        ),
        _state(
            "S13", "First pivot", "Continue down the x₁ column", "operation",
            "The current x<sub>1</sub> entry in the s<sub>2</sub> row (i.e., row 2) is 1. Subtract the pivot row so that<div class=\"decision-equation\">1 - 1(1) = 0</div>Therefore, use<div class=\"decision-equation\">R<sub>2</sub>&prime; = R<sub>2</sub> - R<sub>1</sub>&prime;</div>",
            tableau=first_stages[2], reference_tableau=initial, revealed_rows=("x1", "Z", "s2"), path=at_origin,
            highlights=HighlightSpec(entering_column="x1", transformed_rows=("s2",)),
        ),
        _state(
            "S14", "First pivot", "Complete the x₁ column", "operation",
            "The current x<sub>1</sub> entry in the s<sub>3</sub> row (i.e., row 3) is -1. Add the pivot row so that<div class=\"decision-equation\">-1 + 1(1) = 0</div>Therefore, use<div class=\"decision-equation\">R<sub>3</sub>&prime; = R<sub>3</sub> + R<sub>1</sub>&prime;</div>Finally, the current x<sub>1</sub> entry in the s<sub>4</sub> row (i.e., row 4) is already 0, so no row operation is needed:<div class=\"decision-equation\">R<sub>4</sub>&prime; = R<sub>4</sub></div>",
            tableau=first_stages[4], reference_tableau=initial,
            revealed_rows=("x1", "Z", "s2", "s3", "s4"), path=at_origin,
            highlights=HighlightSpec(entering_column="x1", transformed_rows=("s3", "s4")),
        ),
        _state(
            "S15", "Current solution", "How do we read the current solution?", "question",
            '<span class="pause">Pause and think before pressing Next.</span>',
            tableau=first, path=at_origin,
            highlights=HighlightSpec(basic_columns=("x1", "s2", "s3", "s4")),
        ),
        _state(
            "S16", "Current solution", "Read the neighbouring BFS: Z has improved", "explanation",
            """
<div class="equation-reading">
<div>Note that the new tableau represents the following five equations:</div>
<div class="equation-list">
  <div>Z - (2/3)x<sub>2</sub> + (5/6)s<sub>1</sub> = 20</div>
  <div>x<sub>1</sub> + (2/3)x<sub>2</sub> + (1/6)s<sub>1</sub> = 4</div>
  <div>s<sub>2</sub> + (4/3)x<sub>2</sub> - (1/6)s<sub>1</sub> = 2</div>
  <div>s<sub>3</sub> + (5/3)x<sub>2</sub> + (1/6)s<sub>1</sub> = 5</div>
  <div>s<sub>4</sub> + x<sub>2</sub> = 2</div>
</div>
<div>The current nonbasic variables are x<sub>2</sub> and s<sub>1</sub>. Setting x<sub>2</sub> = s<sub>1</sub> = 0 gives <b>Z = 20, x<sub>1</sub> = 4, s<sub>2</sub> = 2, s<sub>3</sub> = 5, s<sub>4</sub> = 2.</b></div>
<div>Therefore, <b>(x<sub>1</sub>, x<sub>2</sub>, s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>, s<sub>4</sub>) = (4, 0, 0, 2, 5, 2)</b>.</div>
<div>This is why the values of the basic variables can be read directly from the RHS column: once the nonbasic variables are set to zero, each basic-variable row reduces to <b>basic variable = RHS</b>. The corresponding corner point in the decision-variable space is <b>(4, 0)</b>.</div>
</div>
""",
            tableau=first, path=first_path,
            highlights=HighlightSpec(basic_columns=("x1", "s2", "s3", "s4")),
        ),
        _state(
            "S17", "Second iteration", "Have we reached the optimum?", "question",
            '<span class="pause">Pause and think before pressing Next.</span>',
            tableau=first, path=first_path, highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S18", "Second iteration", "Continue: choose x₂ as the next incoming variable", "explanation",
            "No. The current solution is not optimal because row 0 still contains a negative coefficient for the nonbasic variable x<sub>2</sub>.<div class=\"decision-equation equation-pair\"><span>Z - (2/3)x<sub>2</sub> + (5/6)s<sub>1</sub> = 20</span> <span>or Z = 20 + (2/3)x<sub>2</sub> - (5/6)s<sub>1</sub></span></div>Since x<sub>2</sub> is currently 0, increasing x<sub>2</sub> can still increase Z. Therefore x<sub>2</sub> enters the basis.",
            tableau=first, path=first_path,
            highlights=HighlightSpec(row_zero=True, entering_column="x2"),
        ),
        _state(
            "S19", "Second ratio test", "s₂ leaves and x₂ enters", "explanation",
            "But what is the maximum value that the incoming variable x<sub>2</sub> can take? We compute the ratios again using the constraint rows shown in the tableau.<br><br>The minimum ratio is 3/2. Therefore, s<sub>2</sub> reaches zero first, so s<sub>2</sub> leaves the basis and x<sub>2</sub> enters. The pivot element now is 4/3.",
            tableau=first, path=first_path,
            highlights=HighlightSpec(
                entering_column="x2", leaving_row="s2", pivot_row="s2",
                pivot_column="x2", ratio_rows=("x1", "s2", "s3", "s4"),
            ),
            ratios=second_ratios,
        ),
        _state(
            "S20", "Second pivot", "Make the second pivot entry equal to 1", "operation",
            "x<sub>2</sub> is becoming a basic variable. Its column must therefore have a 1 in the x<sub>2</sub> row and 0 everywhere else.<br><br>The pivot entry is 4/3. Multiply the pivot row by 3/4 so that<div class=\"decision-equation\">(3/4)(4/3) = 1</div>Therefore, use<div class=\"decision-equation\">R<sub>2</sub>&prime; = (3/4)R<sub>2</sub></div>",
            tableau=second_stages[0], reference_tableau=first, revealed_rows=("x2",), path=first_path,
            highlights=HighlightSpec(
                entering_column="x2", pivot_row="s2", pivot_column="x2",
                transformed_rows=("x2",),
            ),
        ),
        _state(
            "S21", "Second pivot", "Create zeros from row 0 downward", "operation",
            "The current x<sub>2</sub> entry in the Z row (i.e., row 0) is -2/3. Add 2/3 of the pivot row so that<div class=\"decision-equation\">-2/3 + (2/3)(1) = 0</div>Therefore, use <b>R<sub>0</sub>&prime; = R<sub>0</sub> + (2/3)R<sub>2</sub>&prime;</b>.<br><br>The current x<sub>2</sub> entry in the x<sub>1</sub> row (i.e., row 1) is 2/3. Subtract 2/3 of the pivot row so that<div class=\"decision-equation\">2/3 - (2/3)(1) = 0</div>Therefore, use <b>R<sub>1</sub>&prime; = R<sub>1</sub> - (2/3)R<sub>2</sub>&prime;</b>.",
            tableau=second_stages[2], reference_tableau=first,
            revealed_rows=("x2", "Z", "x1"), path=first_path,
            highlights=HighlightSpec(entering_column="x2", transformed_rows=("Z", "x1")),
        ),
        _state(
            "S22", "Second pivot", "Complete the x₂ column", "operation",
            "The current x<sub>2</sub> entry in the s<sub>3</sub> row (i.e., row 3) is 5/3. Subtract 5/3 of the pivot row so that<div class=\"decision-equation\">5/3 - (5/3)(1) = 0</div>Therefore, use <b>R<sub>3</sub>&prime; = R<sub>3</sub> - (5/3)R<sub>2</sub>&prime;</b>.<br><br>The current x<sub>2</sub> entry in the s<sub>4</sub> row (i.e., row 4) is 1. Subtract the pivot row so that<div class=\"decision-equation\">1 - 1(1) = 0</div>Therefore, use <b>R<sub>4</sub>&prime; = R<sub>4</sub> - R<sub>2</sub>&prime;</b>.",
            tableau=second_stages[4], reference_tableau=first,
            revealed_rows=("x2", "Z", "x1", "s3", "s4"), path=first_path,
            highlights=HighlightSpec(entering_column="x2", transformed_rows=("s3", "s4")),
        ),
        _state(
            "S23", "Final tableau", "How do we read the current solution?", "question",
            '<span class="pause">Pause and think before pressing Next.</span>',
            tableau=final, path=first_path,
            highlights=HighlightSpec(basic_columns=("x1", "x2", "s3", "s4")),
        ),
        _state(
            "S24", "Final tableau", "Read the neighbouring BFS: Z has improved", "explanation",
            """
<div class="equation-reading compact-reading">
<div>As before, read the current solution by first writing the equations represented by the tableau:</div>
<div class="equation-list">
  <div>Z + (3/4)s<sub>1</sub> + (1/2)s<sub>2</sub> = 21</div>
  <div>x<sub>1</sub> + (1/4)s<sub>1</sub> - (1/2)s<sub>2</sub> = 3</div>
  <div>x<sub>2</sub> - (1/8)s<sub>1</sub> + (3/4)s<sub>2</sub> = 3/2</div>
  <div>s<sub>3</sub> + (3/8)s<sub>1</sub> - (5/4)s<sub>2</sub> = 5/2</div>
  <div>s<sub>4</sub> + (1/8)s<sub>1</sub> - (3/4)s<sub>2</sub> = 1/2</div>
</div>
<div>The nonbasic variables are s<sub>1</sub> and s<sub>2</sub>. Setting s<sub>1</sub> = s<sub>2</sub> = 0 gives <b>Z = 21, x<sub>1</sub> = 3, x<sub>2</sub> = 3/2, s<sub>3</sub> = 5/2, s<sub>4</sub> = 1/2.</b></div>
<div>Therefore, <b>(x<sub>1</sub>, x<sub>2</sub>, s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>, s<sub>4</sub>) = (3, 3/2, 0, 0, 5/2, 1/2)</b>, corresponding to the corner point <b>(3, 3/2)</b>.</div>
</div>
""",
            tableau=final, path=full_path,
            highlights=HighlightSpec(basic_columns=("x1", "x2", "s3", "s4")),
        ),
        _state(
            "S25", "Optimality", "How do we know this solution is optimal?", "question",
            '<span class="pause">Pause and think before pressing Next.</span>',
            tableau=final, path=full_path, highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S26", "Optimality", "Stop: no neighbouring BFS can improve Z", "result",
            """
Because there is no negative coefficient in row 0, there is no current nonbasic variable that can increase the maximizing objective.
<div class="decision-equation equation-pair"><span>Z + (3/4)s<sub>1</sub> + (1/2)s<sub>2</sub> = 21</span> <span>or Z = 21 - (3/4)s<sub>1</sub> - (1/2)s<sub>2</sub></span></div>
The nonbasic variables are s<sub>1</sub> = s<sub>2</sub> = 0. Increasing either one from zero would decrease Z.
<br><br>Therefore the current BFS is optimal.
""",
            tableau=final, path=full_path,
            highlights=HighlightSpec(row_zero=True),
        ),
        _state(
            "S27", "Key takeaways", "Key takeaways", "result",
            """
<div class="takeaway-list">
  <div>Equality form provides a convenient initial basic feasible solution.</div>
  <div>The simplex tableau is another representation of the system of equations.</div>
  <div>Row 0 indicates which nonbasic variable can improve the objective; the minimum-ratio test limits its increase so that the current basic variables remain nonnegative.</div>
  <div>Pivoting uses row operations to create the basic-variable column for the entering variable: one 1 in its own row and 0 elsewhere.</div>
  <div>Each new tableau represents a new basic feasible solution.</div>
  <div>When no nonbasic variable can improve the objective, the current basic feasible solution is optimal.</div>
</div>
""",
            tableau=None, panel_title="", panel_html=None, path=full_path,
            workspace_hidden=True, is_final=True,
        ),
    )

    return SimplexDemonstration(
        states, initial, first, final, first_stages, second_stages,
    )


def objective_value(x1: Fraction, x2: Fraction) -> Fraction:
    return 5 * x1 + 4 * x2


def is_feasible(x1: Fraction, x2: Fraction) -> bool:
    return (
        x1 >= 0
        and x2 >= 0
        and 6 * x1 + 4 * x2 <= 24
        and x1 + 2 * x2 <= 6
        and -x1 + x2 <= 1
        and x2 <= 2
    )
