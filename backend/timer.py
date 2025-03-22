import streamlit as st

@st.fragment(run_every=1)
def remaining(study_time):

    if "time_left" not in st.session_state:
        st.session_state.time_left = 0
    if "prev_study_time" not in st.session_state:
        st.session_state.prev_study_time = study_time

    if st.session_state.reset_flag or st.session_state.prev_study_time != study_time:
        st.session_state.time_left = 0
        st.session_state.prev_study_time = study_time
        st.session_state.reset_flag = False

    total_seconds = study_time * 60
    remaining_seconds = total_seconds - st.session_state.time_left
    mins, secs = divmod(max(remaining_seconds, 0), 60)
    st.metric("Remaining", f"{mins:02d}:{secs:02d}", border=True)

    if remaining_seconds > 0:
        st.session_state.time_left += 1