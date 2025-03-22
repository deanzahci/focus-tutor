import streamlit as st
from streamlit_cookies_controller import CookieController
controller = CookieController()

study_time_default = 25
short_break_time_default = 5
long_break_time_default = 15
long_break_interval_default = 4

def set_session_state():
    st.session_state.study_time = controller.get("study_time") or study_time_default
    st.session_state.short_break_time = controller.get("short_break_time") or short_break_time_default
    st.session_state.long_break_time = controller.get("long_break_time") or long_break_time_default
    st.session_state.long_break_interval = controller.get("long_break_interval") or long_break_interval_default

def set_cookies():
    controller.set("study_time", st.session_state.study_time)
    # controller.set("short_break_time", st.session_state.short_break_time)
    # controller.set("long_break_time", st.session_state.long_break_time)
    # controller.set("long_break_interval", st.session_state.long_break_interval)
