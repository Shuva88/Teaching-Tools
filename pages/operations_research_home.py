"""Homepage for the Operations Research teaching demonstrations."""

import streamlit as st


st.markdown(
    """
<style>
.block-container {max-width: 1120px; padding-top: 3.75rem !important; padding-bottom: 1.5rem;}
.home-tool-card {
    min-height: 168px;
    border: 1px solid rgba(128, 128, 128, 0.28);
    border-radius: 0.65rem;
    padding: 1rem 1.1rem 0.75rem;
    background: rgba(128, 128, 128, 0.04);
    margin-bottom: 0.65rem;
}
.home-tool-card h3 {margin: 0 0 0.45rem;}
.home-tool-card p {margin: 0; opacity: 0.82;}
@media (max-width: 800px) {
    .block-container {padding-top: 4rem !important;}
    .home-tool-card {min-height: auto;}
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Operations Research Teaching Tools")
st.caption("Interactive, step-by-step classroom demonstrations")
st.markdown(
    "Select a demonstration below. Each tool uses a fixed example and reveals "
    "the method one decision at a time."
)

columns = st.columns(3, gap="large")
with columns[0]:
    st.markdown(
        """
<div class="home-tool-card">
  <h3>Simplex Algorithm - Example 1</h3>
  <p>Follow two tableau iterations while connecting row operations, basic feasible solutions, and movement across the feasible region.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/simplex_algorithm.py",
        label="Open Simplex Algorithm - Example 1",
        icon="➡️",
        width="stretch",
    )
with columns[1]:
    st.markdown(
        """
<div class="home-tool-card">
  <h3>Transportation Problem - Example 1</h3>
  <p>Plan shipments from three warehouses to four stores using Northwest Corner, Least Cost, or Vogel’s method, then test the plan for optimality.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/transportation_problem_example_1.py",
        label="Open Transportation Problem - Example 1",
        icon="➡️",
        width="stretch",
    )
with columns[2]:
    st.markdown(
        """
<div class="home-tool-card">
  <h3>Transportation Problem - Example 2</h3>
  <p>Start with Vogel’s method, then follow two UV iterations involving loops, donor limits, and changes in total cost.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/transportation_problem_example_2.py",
        label="Open Transportation Problem - Example 2",
        icon="➡️",
        width="stretch",
    )
