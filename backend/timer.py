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
        st.session_state.count_for_long_break = 0
        st.session_state.reset_flag = False

    total_seconds = study_time * 60
    remaining_seconds = total_seconds - st.session_state.time_left
    mins, secs = divmod(max(remaining_seconds, 0), 60)
    st.metric("Remaining", f"{mins:02d}:{secs:02d}", border=True)

    if remaining_seconds > 0:
        st.session_state.time_left += 1

    if remaining_seconds <= 0:
        if st.session_state.timer_status == "studying":
            if "count_for_long_break" not in st.session_state:
                st.session_state.count_for_long_break = 0

            st.session_state.count_for_long_break += 1

            if st.session_state.count_for_long_break == 0:
                st.session_state.timer_status = "short_break"
                st.rerun()
            elif st.session_state.count_for_long_break % st.session_state.long_break_interval == 0:
                st.session_state.timer_status = "long_break"
                st.rerun()
            else:
                st.session_state.timer_status = "short_break"
                st.rerun()
        elif st.session_state.timer_status == "short_break" or st.session_state.timer_status == "long_break":
            st.session_state.timer_status = "studying"
            st.rerun()
        else:
            if st.session_state.timer_status == "reset":
                print("Error: Timer status is reset, but the timer is still running.")