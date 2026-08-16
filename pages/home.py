"""Homepage for the Operations Management teaching demonstrations."""

import streamlit as st


st.markdown(
    """
<style>
.block-container {max-width: 1120px; padding-top: 1.2rem; padding-bottom: 1.5rem;}
.home-tool-card {
    min-height: 150px;
    border: 1px solid rgba(128, 128, 128, 0.28);
    border-radius: 0.65rem;
    padding: 1rem 1.1rem 0.75rem;
    background: rgba(128, 128, 128, 0.04);
    margin-bottom: 0.65rem;
}
.home-tool-card h3 {margin: 0 0 0.45rem;}
.home-tool-card p {margin: 0; opacity: 0.82;}
@media (max-width: 800px) {
    .block-container {padding-top: 0.75rem;}
    .home-tool-card {min-height: auto;}
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Operations Management Teaching Tools")
st.caption("Interactive, step-by-step classroom demonstrations")
st.markdown(
    "Select a demonstration below. Each tool uses a fixed example and reveals "
    "the method one decision at a time."
)

columns = st.columns(2, gap="large")
with columns[0]:
    st.markdown(
        """
<div class="home-tool-card">
  <h3>Johnson's Rule</h3>
  <p>Sequence six jobs through two resources and compare the resulting schedule with the original order.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/johnson_rule.py",
        label="Open Johnson's Rule",
        icon="➡️",
        width="stretch",
    )

with columns[1]:
    st.markdown(
        """
<div class="home-tool-card">
  <h3>Scheduling Consecutive Days Off</h3>
  <p>Build a minimum-size weekly employee schedule with two consecutive days off.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/consecutive_days_off.py",
        label="Open Consecutive Days Off",
        icon="➡️",
        width="stretch",
    )
