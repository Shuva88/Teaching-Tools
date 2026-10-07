"""Browser-side tableau, graph, and QA playback for the simplex example."""

from __future__ import annotations

import json
from fractions import Fraction

from algorithms.simplex import SimplexDemonstration, Tableau, TeachingState


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _tableau_payload(tableau: Tableau | None) -> dict[str, object] | None:
    if tableau is None:
        return None
    return {
        "basicVariables": tableau.basic_variables,
        "rows": [[_fraction_text(value) for value in row] for row in tableau.rows],
    }


def _state_payload(state: TeachingState) -> dict[str, object]:
    return {
        "id": state.state_id,
        "section": state.section,
        "title": state.title,
        "kind": state.kind,
        "bodyHtml": state.body_html,
        "tableau": _tableau_payload(state.tableau),
        "referenceTableau": _tableau_payload(state.reference_tableau),
        "revealedRows": state.revealed_rows,
        "panelTitle": state.panel_title,
        "panelHtml": state.panel_html,
        "workspaceHidden": state.workspace_hidden,
        "highlights": {
            "rowZero": state.highlights.row_zero,
            "enteringColumn": state.highlights.entering_column,
            "leavingRow": state.highlights.leaving_row,
            "pivotRow": state.highlights.pivot_row,
            "pivotColumn": state.highlights.pivot_column,
            "transformedRows": state.highlights.transformed_rows,
            "ratioRows": state.highlights.ratio_rows,
            "excludedRows": state.highlights.excluded_rows,
            "basicColumns": state.highlights.basic_columns,
        },
        "ratios": dict(state.ratios),
        "path": [
            {
                "x1": float(point.x1),
                "x2": float(point.x2),
                "z": _fraction_text(point.objective),
                "label": point.label,
                "values": [_fraction_text(value) for value in point.values],
            }
            for point in state.path
        ],
        "isFinal": state.is_final,
    }


def build_simplex_demonstration_html(
    demo: SimplexDemonstration,
    *,
    review_state_index: int | None = None,
) -> str:
    """Return the interactive player or one static state for QA review."""

    if review_state_index is None:
        displayed_states = demo.states
        display_offset = 0
        app_class = "app"
        controls_markup = """
  <div class="controls">
    <div id="state-note" class="state-note"></div>
    <button id="previous" type="button">Previous</button>
    <button id="next" class="primary" type="button">Next</button>
  </div>"""
    else:
        if not 0 <= review_state_index < len(demo.states):
            raise IndexError("review_state_index is outside the demonstration")
        displayed_states = (demo.states[review_state_index],)
        display_offset = review_state_index
        app_class = "app review-mode"
        controls_markup = ""

    states_json = json.dumps(
        [_state_payload(state) for state in displayed_states],
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")

    template = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}:root{--ink:#20293a;--muted:#667085;--line:#d8dee9;--soft:#f7f9fc;--blue:#2563eb;--blue-soft:#eaf1ff;--amber:#d97706;--amber-soft:#fff5df;--green:#16803a;--green-soft:#eaf8ee;--purple:#7356b6}
html,body{margin:0;height:100%;overflow:hidden}body{font-family:Inter,Arial,sans-serif;color:var(--ink);background:transparent}
.app{height:612px;display:grid;grid-template-rows:auto 330px minmax(144px,1fr) auto;gap:8px}.app.review-mode{height:680px;grid-template-rows:auto 330px minmax(300px,1fr)}.review-mode .teaching{overflow:visible}
.topbar{display:flex;align-items:center;gap:12px;min-height:32px}.section{font-size:12px;font-weight:750;letter-spacing:.02em;color:var(--blue)}.progress-wrap{margin-left:auto;min-width:190px;display:flex;align-items:center;gap:8px}.progress-label{font-size:12px;color:var(--muted);white-space:nowrap}.progress-track{flex:1;height:7px;border-radius:999px;background:#e7ebf2;overflow:hidden}.progress-fill{height:100%;width:0;background:var(--blue);transition:width 220ms ease}
.workspace{min-height:0;display:grid;grid-template-columns:minmax(0,1.06fr) minmax(0,.94fr);gap:10px}.panel{min-width:0;border:1px solid var(--line);border-radius:12px;background:white;overflow:hidden}.panel-heading{height:37px;display:flex;align-items:center;padding:0 12px;border-bottom:1px solid #e8ecf2;background:var(--soft);font-size:14px;font-weight:750}
.tableau-wrap{height:calc(100% - 37px);display:flex;align-items:center;justify-content:center;padding:7px 8px;overflow:auto}.tableau{width:100%;border-collapse:separate;border-spacing:0;text-align:center;font-variant-numeric:tabular-nums}.tableau th,.tableau td{min-width:42px;padding:7px 4px;border-right:1px solid #e0e5ec;border-bottom:1px solid #e0e5ec;font-size:13px;transition:background 160ms ease,box-shadow 160ms ease}.tableau th{background:#f1f4f8;color:#3f4b5f;font-weight:750}.tableau tr:first-child th{border-top:1px solid #e0e5ec}.tableau th:first-child,.tableau td:first-child{border-left:1px solid #e0e5ec;font-weight:750}.tableau .row-zero td{background:#f3effd}.tableau .entering{background:var(--blue-soft)!important;color:#1649a5;font-weight:750}.tableau .basic-column{background:#edf8f1;color:#116b31;font-weight:750}.tableau .leaving td{background:var(--amber-soft)}.tableau .pivot{background:#ffe3a3!important;box-shadow:inset 0 0 0 2px var(--amber);font-weight:800}.tableau .transformed td{box-shadow:inset 0 2px 0 var(--blue),inset 0 -2px 0 var(--blue)}.tableau .ratio-cell{background:#eaf8ee;color:#116b31;font-weight:800}.tableau .excluded-cell{background:#f5f5f5;color:#777}.legend{display:flex;flex-wrap:wrap;gap:5px 11px;margin-top:6px;font-size:10.5px;color:var(--muted)}.key{display:inline-flex;align-items:center;gap:4px}.swatch{width:10px;height:10px;border-radius:2px;border:1px solid #cfd6e1}.swatch.enter{background:var(--blue-soft)}.swatch.leave{background:var(--amber-soft)}.swatch.ratio,.swatch.basic{background:var(--green-soft)}
.equation-card{width:100%;max-width:455px;padding:12px 18px;border:1px solid #dce2ec;border-radius:10px;background:#fbfcfe;text-align:left;line-height:1.48;font-size:15px}.model-line{display:grid;grid-template-columns:44px minmax(0,1fr);gap:8px}.equation-card .objective{font-weight:800;color:#183f8f;margin-bottom:4px}.model-operator{font-weight:750;color:#344054}.equation-card .objective-row{color:#6f3fa0;font-weight:750}.equation-card .first-equation{padding-bottom:6px;margin-bottom:5px;border-bottom:1px solid #dce2ec}.compact-equations{line-height:1.48}
.graph-content{height:calc(100% - 37px);display:grid;grid-template-rows:minmax(0,1fr) auto}.graph-wrap{min-height:0;padding:1px 4px}.graph-wrap svg{display:block;width:100%;height:100%}.graph-bfs{min-height:48px;padding:6px 10px;border-top:1px solid #e8ecf2;background:#fbfcfe;font-size:13px;line-height:1.35;color:#344054}.graph-bfs b{color:#183f8f}.axis{stroke:#5f6b7c;stroke-width:1.5}.grid{stroke:#edf0f4;stroke-width:1}.constraint{fill:none;stroke-width:2.2}.c1{stroke:#2878b5}.c2{stroke:#d46b36}.c3{stroke:#7b61a8}.c4{stroke:#b66a00;stroke-dasharray:6 4}.feasible{fill:#cdeed8;fill-opacity:.72;stroke:#4a9a62;stroke-width:1.5}.constraint-label{font-size:24px;font-weight:700;paint-order:stroke;stroke:white;stroke-width:5px;stroke-linejoin:round}.tick{font-size:14px;fill:#697586}.path-line{stroke:var(--blue);stroke-width:3.5;stroke-linecap:round;opacity:.72}.path-line.current{stroke-dasharray:1;animation:drawPath 520ms ease both}.bfs-past{fill:white;stroke:var(--blue);stroke-width:2.5}.bfs-current{fill:#ef4444;stroke:white;stroke-width:2.5;filter:drop-shadow(0 1px 2px #777)}.bfs-label{font-size:24px;font-weight:800;fill:#1f2937;paint-order:stroke;stroke:white;stroke-width:3px}@keyframes drawPath{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
.teaching{min-height:0;padding:9px 12px 8px;border:1px solid var(--line);border-left:5px solid var(--blue);border-radius:11px;background:white;overflow:auto}.teaching.question{border-left-color:var(--amber);background:#fffdf8}.teaching.operation{border-left-color:var(--purple)}.teaching.result{border-left-color:var(--green);background:#fbfffc}.teaching-title{margin:0 0 4px;font-size:15px;font-weight:800}.teaching-body{font-size:13px;line-height:1.38;color:#303b4f;text-align:left}.teaching-body .pause{display:block;margin-top:5px;color:#9a5a05;font-size:12px;font-weight:700}.bfs-equation{margin-top:6px;padding:5px 7px;border-radius:6px;background:#eef4ff;font-weight:700}.ratio-explanation{display:grid;grid-template-columns:1fr 1fr;gap:4px 12px;margin-bottom:5px}.ratio-explanation>div{padding:3px 6px;background:#f8fafc;border-radius:5px}.final-equations{display:grid;grid-template-columns:1fr 1fr;gap:3px 12px;margin-bottom:5px;font-weight:650}.result-strip{display:flex;align-items:center;flex-wrap:wrap;gap:6px 16px;padding:5px 8px;margin-bottom:5px;background:var(--green-soft);border-radius:7px;color:#116b31}.result-strip span{margin-left:auto;color:#344054}.optimality{font-size:12.5px;margin:4px 2px 6px}.takeaway-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px 14px;font-size:11.5px;line-height:1.3}.takeaway-grid>div::before{content:'•';color:var(--green);margin-right:5px}
.controls{display:grid;grid-template-columns:1fr minmax(170px,240px) minmax(170px,240px);align-items:center;gap:10px}.state-note{color:var(--muted);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}button{min-height:38px;border:1px solid #cbd3df;border-radius:9px;background:white;color:#273244;font-size:14px;font-weight:750;cursor:pointer}button.primary{background:var(--blue);color:white;border-color:var(--blue)}button:disabled{opacity:.42;cursor:default}sub{line-height:0}
@media(max-width:760px){html,body{overflow:auto}.app{height:auto;min-height:612px;grid-template-rows:auto auto auto auto}.app.review-mode{height:auto;grid-template-rows:auto auto auto}.workspace{grid-template-columns:1fr}.panel{min-height:310px}.progress-wrap{min-width:135px}.controls{grid-template-columns:1fr 1fr}.state-note{grid-column:1/-1;grid-row:2;text-align:center}.ratio-explanation,.final-equations,.takeaway-grid{grid-template-columns:1fr}.result-strip span{margin-left:0}}
.app{height:590px;grid-template-rows:auto 302px minmax(150px,1fr) auto;gap:7px}
.app.review-mode{height:680px;grid-template-rows:auto 318px minmax(312px,1fr)}
.tableau-wrap{padding:6px 8px;overflow:hidden}
.tableau th,.tableau td{padding:6px 4px;font-size:14px}
.stacked-tableaus{width:100%;height:100%;display:grid;grid-template-rows:minmax(0,1fr) 10px minmax(0,1fr);gap:2px}
.tableau-block{min-height:0;display:flex;flex-direction:column;justify-content:center;overflow:hidden}.tableau-caption{height:13px;font-size:10px;font-weight:800;color:#475467}
.stacked-tableaus .tableau{height:auto}
.stacked-tableaus .tableau th,.stacked-tableaus .tableau td{min-width:30px;padding:1px 2px;font-size:10.5px;height:16px}
.row-flow{text-align:center;color:#7356b6;font-size:10px;font-weight:800}
.placeholder-row td{color:transparent!important;background:#fbfcfe!important}
.fresh-reveal{animation:revealRow 360ms ease both}
@keyframes revealRow{from{opacity:0;transform:translateY(-3px)}to{opacity:1;transform:none}}
.teaching{padding:8px 12px 7px;overflow:hidden}
.teaching-title{font-size:16px}.teaching-body{font-size:13px;line-height:1.3}
.teaching-body .pause{font-size:13px}
.bfs-equation,.decision-equation{margin-top:5px;padding:4px 7px;border-radius:6px;background:#eef4ff;font-weight:700}
.ratio-explanation{gap:4px 10px;margin:5px 0}.final-equations{gap:2px 10px;margin:5px 0}
.ratio-explanation>div{line-height:1.15;padding:2px 5px}
.solution-reading-grid,.final-state-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;height:100%}
.solution-reading-grid>div,.final-state-grid>div{min-width:0}
.compact-paragraph{margin-top:5px}.solution-values{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px 8px;margin:3px 0}
.compact-bfs{display:grid;gap:2px;font-size:.92em;line-height:1.18}
.concept-note{margin-top:7px;padding:6px 8px;border-radius:6px;background:#eef4ff}.equation-reading{display:grid;gap:5px}.equation-list{display:grid;gap:1px;padding:5px 8px;border-radius:6px;background:#f6f8fb;font-weight:650}.takeaway-list{display:grid;gap:8px;font-size:14px;line-height:1.35}.takeaway-list>div{padding:7px 10px;border-left:4px solid var(--green);border-radius:5px;background:#f2fbf5}
/* The host iframe is fitted to the actual browser viewport by fitWorkspace. */
.presentation{display:contents}
.app:not(.review-mode){height:100vh;min-height:0;grid-template-rows:22px minmax(0,1fr) 28px;gap:4px;padding-bottom:2px}
.app:not(.review-mode) .presentation{min-height:0;display:grid;grid-template-rows:var(--workspace-height,260px) auto;align-content:start;gap:4px;overflow-y:auto;overflow-x:hidden}
.app:not(.review-mode) .topbar{min-height:22px}
.app:not(.review-mode) .panel-heading{height:30px;font-size:13px}
.app:not(.review-mode) .tableau-wrap,.app:not(.review-mode) .graph-content{height:calc(100% - 30px)}
.app:not(.review-mode) .tableau th,.app:not(.review-mode) .tableau td{font-size:12px;line-height:1.1;padding:2px 2px;min-width:0}
.app:not(.review-mode) .tableau .fraction{font-size:11px;line-height:.85!important}
.app:not(.review-mode) .tableau .fraction .numerator,.app:not(.review-mode) .tableau .fraction .denominator{padding:0 1px!important}
.app:not(.review-mode) .tableau-block{justify-content:flex-start;overflow:visible}
.app:not(.review-mode) .tableau-caption{flex-shrink:0}
.app:not(.review-mode) .stacked-tableaus{height:auto;grid-template-columns:1fr;grid-template-rows:auto 10px auto;gap:2px}
.app:not(.review-mode) .row-flow{font-size:10px}
.app:not(.review-mode) .stacked-tableaus .tableau th,.app:not(.review-mode) .stacked-tableaus .tableau td{height:15px;font-size:12px;padding:0 1px}
.app:not(.review-mode) .stacked-tableaus .fraction{display:inline!important;line-height:inherit!important}
.app:not(.review-mode) .stacked-tableaus .fraction .numerator{border-bottom:0!important;padding:0!important}
.app:not(.review-mode) .stacked-tableaus .fraction .numerator::after{content:'/'}
.app:not(.review-mode) .stacked-tableaus .fraction .denominator{padding:0!important}
.app:not(.review-mode) .teaching{align-self:start;width:100%;padding:6px 10px 5px;overflow:visible}
.app:not(.review-mode) .teaching-title{font-size:15px;line-height:1.2;margin-bottom:3px}
.app:not(.review-mode) .concept-note{margin-top:5px;padding:4px 7px}
.app:not(.review-mode) .teaching-body br+br{display:none}
.app:not(.review-mode) .equation-reading{gap:2px}
.app:not(.review-mode) .equation-list{gap:0}
.app:not(.review-mode) .graph-bfs{min-height:36px;padding:5px 8px;font-size:12px}
.app:not(.review-mode) .controls{min-height:28px;grid-template-columns:1fr 100px 110px;gap:7px}
.app:not(.review-mode) button{min-height:28px;padding:2px 10px;border-radius:6px;font-size:12px}
.app:not(.review-mode) .state-note{font-size:11px}
.app:not(.review-mode).workspace-hidden .presentation{grid-template-rows:minmax(0,1fr)}
.equation-pair{display:flex;flex-wrap:wrap;align-items:baseline;gap:3px 12px}
.equation-pair>span{white-space:nowrap}
/* Keep emphasis selective; equations remain readable without bold blocks. */
.section,.panel-heading,.teaching-title,.tableau-caption,.row-flow{font-weight:600}
.tableau th,.tableau td:first-child,.tableau .entering,.tableau .basic-column,.tableau .pivot,.tableau .ratio-cell{font-weight:600}
.equation-card .objective,.equation-card .objective-row,.model-operator{font-weight:400}
.teaching-body b,.bfs-equation,.decision-equation,.equation-list,.final-equations{font-weight:400}
.graph-bfs b{font-weight:400}
.graph-wrap svg text{font-weight:400}
.constraint-label{font-size:17px;stroke-width:3px}
.bfs-label{font-size:19px;stroke-width:3px}
.graph-bfs[hidden]{display:none}
.explanation-block+.explanation-block{margin-top:4px}
.ratio-row-label{font-weight:600;margin-bottom:2px}
.ratio-equations{margin-left:12px;line-height:1.3}
.ratio-conclusion{margin-top:4px;padding-left:12px;position:relative;line-height:1.3}
.ratio-conclusion::before{content:'\2022';position:absolute;left:0;color:var(--muted)}
.ratio-note{margin-top:4px;padding-left:12px;position:relative}
.ratio-note::before{content:'\2022';position:absolute;left:0;color:var(--muted)}
.decision-equation,.bfs-equation,.equation-list{padding-left:16px}
.workspace-hidden .workspace{display:none}
.workspace-hidden .teaching{height:100%;display:flex;flex-direction:column;justify-content:center;padding:18px 24px}
.workspace-hidden .teaching-title{font-size:20px;margin-bottom:10px}
.workspace-hidden .state-note{visibility:hidden}
@media(max-width:760px){
  .app:not(.review-mode){height:100vh;min-height:0}
  .app:not(.review-mode) .workspace{grid-template-columns:minmax(0,1.06fr) minmax(0,.94fr)}
  .app:not(.review-mode) .panel{min-height:0}
  .app:not(.review-mode) .controls{grid-template-columns:1fr 100px 110px}
  .app:not(.review-mode) .state-note{grid-row:auto;grid-column:auto;text-align:left}
  .app:not(.review-mode) .tableau th,.app:not(.review-mode) .tableau td{font-size:12px;padding:2px 1px}
  .app:not(.review-mode) .stacked-tableaus{grid-template-columns:1fr;grid-template-rows:auto 10px auto;gap:2px}
  .ratio-explanation,.final-equations,.takeaway-grid{grid-template-columns:1fr 1fr}
}
@media(max-width:620px){
  .app:not(.review-mode){grid-template-rows:auto minmax(0,1fr) 36px}
  .app:not(.review-mode) .topbar{flex-wrap:wrap;gap:3px 8px}
  .progress-wrap{min-width:0}.progress-label{font-size:11px}.progress-track{display:none}
  .app:not(.review-mode) .presentation{display:block;overflow-y:auto;overscroll-behavior:contain}
  .app:not(.review-mode) .workspace{display:grid;grid-template-columns:1fr;gap:6px}
  .app:not(.review-mode) .panel{min-height:0;height:auto}
  .app:not(.review-mode) .tableau-wrap{height:auto;padding:6px;align-items:flex-start;overflow:visible}
  .app:not(.review-mode) .graph-content{height:auto}
  .app:not(.review-mode) .graph-wrap{aspect-ratio:520/300;height:auto}
  .app:not(.review-mode) .teaching{margin-top:6px}
  .app:not(.review-mode) .ratio-explanation,.app:not(.review-mode) .final-equations{grid-template-columns:1fr}
  .app:not(.review-mode) .controls{min-height:36px;grid-template-columns:1fr 96px 106px}
  .app:not(.review-mode) button{min-height:36px}
  .app:not(.review-mode).workspace-hidden .workspace{display:none}
  .workspace-hidden .teaching{height:auto;min-height:100%;padding:12px}
  .takeaway-list{font-size:13px;gap:6px}
}
</style></head><body>
<main class="__APP_CLASS__">
  <div class="topbar"><div id="section" class="section"></div><div class="progress-wrap"><span id="progress-label" class="progress-label"></span><span class="progress-track"><span id="progress-fill" class="progress-fill"></span></span></div></div>
  <div class="presentation">
  <div class="workspace">
    <section class="panel"><div id="left-title" class="panel-heading"></div><div id="tableau-wrap" class="tableau-wrap"></div></section>
    <section class="panel"><div class="panel-heading">Feasible region and simplex path</div><div class="graph-content"><div id="graph" class="graph-wrap"></div><div id="graph-bfs" class="graph-bfs"></div></div></section>
  </div>
  <section id="teaching" class="teaching"><div id="teaching-title" class="teaching-title"></div><div id="teaching-body" class="teaching-body"></div></section>
  </div>
__CONTROLS_MARKUP__
</main>
<script>
const states=__STATES__,columns=['Z','x1','x2','s1','s2','s3','s4','RHS'];
const displayOffset=__DISPLAY_OFFSET__,displayTotal=__DISPLAY_TOTAL__;let stateIndex=0;
function label(v){if(v==='RHS'||v==='Z')return v;return `${v[0]}<sub>${v.slice(1)}</sub>`}
function numberMarkup(v){if(!v.includes('/'))return v.replace('-','−');const neg=v.startsWith('-'),clean=neg?v.slice(1):v,[a,b]=clean.split('/');return `${neg?'−':''}<span class="fraction" style="display:inline-grid;line-height:1;text-align:center;vertical-align:middle"><span class="numerator" style="border-bottom:1px solid currentColor;padding:0 2px">${a}</span><span class="denominator" style="padding:1px 2px 0">${b}</span></span>`}
function tableMarkup(tableau,h,ratios={},options={}){const showRatios=Object.keys(ratios).length>0,revealed=options.revealed||null,previous=options.previous||[],fresh=[];if(revealed)revealed.forEach(v=>{if(!previous.includes(v))fresh.push(v)});let html='<table class="tableau"><thead><tr><th>BV</th>';columns.forEach(c=>{const cls=[h.enteringColumn===c?'entering':'',(h.basicColumns||[]).includes(c)?'basic-column':''].filter(Boolean).join(' ');html+=`<th class="${cls}">${label(c)}</th>`});if(showRatios)html+='<th>Ratio</th>';html+='</tr></thead><tbody>';tableau.rows.forEach((row,i)=>{const basic=tableau.basicVariables[i],isVisible=!revealed||revealed.includes(basic),classes=[];if(!isVisible)classes.push('placeholder-row');if(isVisible&&fresh.includes(basic))classes.push('fresh-reveal');if(i===0&&h.rowZero)classes.push('row-zero');if(h.leavingRow===basic)classes.push('leaving');if((h.transformedRows||[]).includes(basic))classes.push('transformed');const delay=Math.max(0,fresh.indexOf(basic))*240;if(delay)classes.push('delayed-row');html+=`<tr class="${classes.join(' ')}" style="${delay?`animation-delay:${delay}ms`:''}"><td>${isVisible?label(basic):'&nbsp;'}</td>`;row.forEach((value,j)=>{const c=columns[j],cell=[];if(h.enteringColumn===c)cell.push('entering');if((h.basicColumns||[]).includes(c))cell.push('basic-column');if(h.pivotRow===basic&&h.pivotColumn===c)cell.push('pivot');html+=`<td class="${cell.join(' ')}">${isVisible?numberMarkup(value):'&nbsp;'}</td>`});if(showRatios){const cell=[];if((h.ratioRows||[]).includes(basic))cell.push('ratio-cell');if((h.excludedRows||[]).includes(basic))cell.push('excluded-cell');html+=`<td class="${cell.join(' ')}">${isVisible?(ratios[basic]||'—'):'&nbsp;'}</td>`}html+='</tr>'});return html+'</tbody></table>'}
function renderTableau(state){const wrap=document.getElementById('tableau-wrap');document.getElementById('left-title').textContent=state.referenceTableau?'Current and next tableaus':state.panelTitle;if(!state.tableau){wrap.innerHTML=state.panelHtml||'';return}const h=state.highlights,ratios=state.ratios||{};if(state.referenceTableau){const previousState=stateIndex>0?states[stateIndex-1]:null,previous=previousState&&previousState.referenceTableau?(previousState.revealedRows||[]):[];wrap.innerHTML=`<div class="stacked-tableaus"><div class="tableau-block"><div class="tableau-caption">Current tableau</div>${tableMarkup(state.referenceTableau,h)}</div><div class="row-flow">row operations ↓</div><div class="tableau-block"><div class="tableau-caption">Next tableau</div>${tableMarkup(state.tableau,h,{}, {revealed:state.revealedRows||[],previous})}</div></div>`;return}let html='<div style="width:100%">'+tableMarkup(state.tableau,h,ratios)+'<div class="legend">';if(h.enteringColumn)html+='<span class="key"><span class="swatch enter"></span>Incoming column</span>';if(h.leavingRow)html+='<span class="key"><span class="swatch leave"></span>Leaving row</span>';if((h.ratioRows||[]).length)html+='<span class="key"><span class="swatch ratio"></span>Valid ratio</span>';if((h.basicColumns||[]).length)html+='<span class="key"><span class="swatch basic"></span>Basic-variable columns</span>';wrap.innerHTML=html+'</div></div>'}
function sx(x){return 52+(x/5)*430}function sy(y){return 260-(y/3)*220}
function constraintLabel(text,color,a,b,t){const x=sx(a[0])+t*(sx(b[0])-sx(a[0])),y=sy(a[1])+t*(sy(b[1])-sy(a[1])),angle=Math.atan2(sy(b[1])-sy(a[1]),sx(b[0])-sx(a[0]))*180/Math.PI;return `<text class="constraint-label" fill="${color}" text-anchor="middle" transform="translate(${x} ${y}) rotate(${angle})" y="-8">${text}</text>`}
function renderGraph(state){let svg='<svg viewBox="0 0 520 300" role="img" aria-label="Feasible region and simplex path">';for(let x=0;x<=5;x++)svg+=`<line class="grid" x1="${sx(x)}" y1="${sy(0)}" x2="${sx(x)}" y2="${sy(3)}"/>`;for(let y=0;y<=3;y++)svg+=`<line class="grid" x1="${sx(0)}" y1="${sy(y)}" x2="${sx(5)}" y2="${sy(y)}"/>`;svg+=`<polygon class="feasible" points="${sx(0)},${sy(0)} ${sx(4)},${sy(0)} ${sx(3)},${sy(1.5)} ${sx(2)},${sy(2)} ${sx(1)},${sy(2)} ${sx(0)},${sy(1)}"/>`;svg+=`<line class="constraint c1" x1="${sx(2)}" y1="${sy(3)}" x2="${sx(4)}" y2="${sy(0)}"/><line class="constraint c2" x1="${sx(0)}" y1="${sy(3)}" x2="${sx(5)}" y2="${sy(.5)}"/><line class="constraint c3" x1="${sx(0)}" y1="${sy(1)}" x2="${sx(2)}" y2="${sy(3)}"/><line class="constraint c4" x1="${sx(0)}" y1="${sy(2)}" x2="${sx(5)}" y2="${sy(2)}"/>`;svg+=constraintLabel('6x₁ + 4x₂ = 24','#2878b5',[2,3],[4,0],.25)+constraintLabel('x₁ + 2x₂ = 6','#d46b36',[0,3],[5,.5],.77)+constraintLabel('−x₁ + x₂ = 1','#7b61a8',[0,1],[2,3],.4)+constraintLabel('x₂ = 2','#b66a00',[0,2],[5,2],.85);svg+=`<line class="axis" x1="${sx(0)}" y1="${sy(0)}" x2="${sx(5)+7}" y2="${sy(0)}"/><line class="axis" x1="${sx(0)}" y1="${sy(0)}" x2="${sx(0)}" y2="${sy(3)-7}"/>`;for(let x=0;x<=5;x++)svg+=`<text class="tick" text-anchor="middle" x="${sx(x)}" y="${sy(0)+16}">${x}</text>`;for(let y=1;y<=3;y++)svg+=`<text class="tick" text-anchor="end" x="${sx(0)-8}" y="${sy(y)+4}">${y}</text>`;svg+=`<text class="constraint-label" x="${sx(5)+4}" y="${sy(0)+19}">x₁</text><text class="constraint-label" x="${sx(0)-19}" y="${sy(3)-8}">x₂</text>`;const path=state.path||[];for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i],cls=i===path.length-1?'path-line current':'path-line';svg+=`<line class="${cls}" pathLength="1" x1="${sx(a.x1)}" y1="${sy(a.x2)}" x2="${sx(b.x1)}" y2="${sy(b.x2)}" marker-end="url(#arrow)"/>`}svg+='<defs><marker id="arrow" markerWidth="5" markerHeight="5" refX="4.5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 z" fill="#2563eb"/></marker></defs>';path.forEach((p,i)=>{const current=i===path.length-1;svg+=`<circle class="${current?'bfs-current':'bfs-past'}" cx="${sx(p.x1)}" cy="${sy(p.x2)}" r="${current?6:4}"/>`;const dx=p.x1===0?9:p.x2>0?-82:-8,dy=p.x2===0&&p.x1>0?32:p.x2>0?24:-12;svg+=`<text class="bfs-label" x="${sx(p.x1)+dx}" y="${sy(p.x2)+dy}">${p.label}</text>`});svg+='</svg>';document.getElementById('graph').innerHTML=svg;const summary=document.getElementById('graph-bfs');summary.hidden=!path.length;if(!path.length){summary.innerHTML='';return}const p=path[path.length-1],tuple=p.values.map(numberMarkup).join(', ');summary.innerHTML=`<b>Current BFS:</b> (x<sub>1</sub>,x<sub>2</sub>,s<sub>1</sub>,s<sub>2</sub>,s<sub>3</sub>,s<sub>4</sub>) = (${tuple}) &nbsp; · &nbsp; <b>Z = ${numberMarkup(p.z)}</b>`}
function fitWorkspace(){
  const app=document.querySelector('main');
  if(app.classList.contains('review-mode'))return;
  const frame=window.frameElement;
  if(frame){
    const available=Math.floor(window.parent.innerHeight-frame.getBoundingClientRect().top-12);
    if(available>0){
      frame.style.setProperty('height',available+'px','important');
      const host=frame.closest('[data-testid="stElementContainer"]');
      if(host)host.style.setProperty('height',available+'px','important');
    }
  }
  const wrap=document.getElementById('tableau-wrap'),content=wrap.firstElementChild;
  if(content&&!app.classList.contains('workspace-hidden')){
    const minimum=Math.max(200,Math.ceil(content.getBoundingClientRect().height+44));
    const presentation=document.querySelector('.presentation'),teaching=document.getElementById('teaching');
    const graph=document.getElementById('graph'),bfs=document.getElementById('graph-bfs');
    const idealGraph=Math.ceil(graph.clientWidth*300/520+bfs.offsetHeight+32);
    const remaining=presentation.clientHeight-teaching.offsetHeight-4;
    app.style.setProperty('--workspace-height',Math.max(minimum,Math.min(idealGraph,remaining))+'px');
  }
}
function fitTeaching(teaching){teaching.scrollTop=0;document.querySelector('.presentation').scrollTop=0;fitWorkspace()}
window.addEventListener('resize',()=>requestAnimationFrame(fitWorkspace));
if(window.frameElement){
  const parentResize=()=>{if(window.frameElement?.isConnected)requestAnimationFrame(fitWorkspace);else window.parent.removeEventListener('resize',parentResize)};
  window.parent.addEventListener('resize',parentResize);
  new ResizeObserver(()=>requestAnimationFrame(fitWorkspace)).observe(window.frameElement);
}
function render(){const state=states[stateIndex],n=displayOffset+stateIndex+1,app=document.querySelector('main');app.classList.toggle('workspace-hidden',Boolean(state.workspaceHidden));document.getElementById('section').textContent=state.section;document.getElementById('progress-label').textContent=`Teaching step ${n} / ${displayTotal}`;document.getElementById('progress-fill').style.width=`${(n/displayTotal)*100}%`;renderTableau(state);renderGraph(state);const teaching=document.getElementById('teaching');teaching.className=`teaching ${state.kind}`;document.getElementById('teaching-title').textContent=state.title;document.getElementById('teaching-body').innerHTML='<div class="explanation-block">'+state.bodyHtml.replace(/<br\s*\/?><br\s*\/?>/gi,'</div><div class="explanation-block">')+'</div>';const note=document.getElementById('state-note');if(note)note.textContent=state.isFinal?'Review complete.':state.id;const previous=document.getElementById('previous'),next=document.getElementById('next');if(previous&&next){previous.disabled=stateIndex===0;next.disabled=stateIndex===states.length-1;next.textContent=state.id==='S26'?'Key takeaways':stateIndex===states.length-1?'Complete':'Next'}requestAnimationFrame(()=>fitTeaching(teaching))}
const previousButton=document.getElementById('previous'),nextButton=document.getElementById('next');if(previousButton&&nextButton){previousButton.addEventListener('click',()=>{if(stateIndex>0){stateIndex-=1;render()}});nextButton.addEventListener('click',()=>{if(stateIndex<states.length-1){stateIndex+=1;render()}});document.addEventListener('keydown',event=>{if(event.key==='ArrowRight'&&stateIndex<states.length-1){stateIndex+=1;render()}if(event.key==='ArrowLeft'&&stateIndex>0){stateIndex-=1;render()}})}render();
</script></body></html>"""
    return (
        template.replace("__STATES__", states_json)
        .replace("__APP_CLASS__", app_class)
        .replace("__CONTROLS_MARKUP__", controls_markup)
        .replace("__DISPLAY_OFFSET__", str(display_offset))
        .replace("__DISPLAY_TOTAL__", str(len(demo.states)))
    )


def build_simplex_review_state_html(
    demo: SimplexDemonstration,
    state_index: int,
) -> str:
    return build_simplex_demonstration_html(demo, review_state_index=state_index)
