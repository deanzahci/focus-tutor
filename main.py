import streamlit as st
from backend.timer import remaining
from backend.cookie import set_session_state, set_cookies

st.set_page_config(page_title="FocusTutor")
st.title("FocusTutor")

set_session_state()

# For testing purpose
# if "count_for_long_break" not in st.session_state:
#     st.session_state.count_for_long_break = 0
# st.markdown(f"{st.session_state.count_for_long_break}")

st.sidebar.markdown("# Settings")
st.sidebar.slider("Study (min)", key="study_time", min_value=1, max_value=120)
st.sidebar.slider("Short Break (min)", key="short_break_time", min_value=1, max_value=15)
st.sidebar.slider("Long Break (min)", key="long_break_time", min_value=1, max_value=30)
st.sidebar.slider("Long Break Interval", key="long_break_interval", min_value=0, max_value=10)
st.sidebar.write("0 long breaks interval means no long breaks.")
set_cookies()

if "timer_status" not in st.session_state:
    st.session_state["timer_status"] = "reset"
if "reset_flag" not in st.session_state:
    st.session_state["reset_flag"] = False

a, b = st.columns(2)
with a:
    timer_ph = st.empty()

if st.session_state["timer_status"] == "reset":
    if st.button("Start Studying", key="start_studying", use_container_width=True):
        st.session_state.timer_status = "studying"
        st.rerun()
elif st.session_state["timer_status"] == "short_break" or st.session_state["timer_status"] == "long_break":
    a, b = st.columns(2)
    with a:
        if st.button("Start Studying", key="start_studying", use_container_width=True):
            st.session_state.timer_status = "studying"
            st.rerun()
    with b:
        if st.button("Reset", key="reset_study", use_container_width=True):
            st.session_state.reset_flag = True
            st.session_state.timer_status = "reset"
            st.rerun()
else:
    a, b, c = st.columns(3)
    with a:
        if st.button("Start Short Break", key="start_short_break", use_container_width=True):
            st.session_state.timer_status = "short_break"
            st.rerun()
    with b:
        if st.button("Start Long Break", key="start_long_break", use_container_width=True):
            st.session_state.timer_status = "long_break"
            st.rerun()
    with c:
        if st.button("Reset", key="reset_break", use_container_width=True):
            st.session_state.reset_flag = True
            st.session_state.timer_status = "reset"
            st.rerun()

if st.session_state["timer_status"] == "studying":
    with timer_ph:
        remaining(st.session_state.study_time)
elif st.session_state["timer_status"] == "short_break":
    with timer_ph:
        remaining(st.session_state.short_break_time)
elif st.session_state["timer_status"] == "long_break":
    with timer_ph:
        remaining(st.session_state.long_break_time)

st.sidebar.markdown("""
# Information
You'll need a [Muse 2](https://choosemuse.com/products/muse-2) or [Muse S](https://choosemuse.com/products/muse-s-athena), plus [Petal Metrics](https://petal.tech/downloads) to run this app.
Find the source code and more info on [GitHub](https://github.com/deanzahci/focustutor).
Built by the De Anza Human-Computer Interaction team.
""")

# Hide the cookies controller iframe
# https://github.com/NathanChen198/streamlit-cookies-controller/issues/8
st.markdown(
    """
    <style>
        .element-container:has(
            iframe[height="0"]
        ):has(
            iframe[title="streamlit_cookies_controller.cookie_controller.cookie_controller"]
        ) {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)