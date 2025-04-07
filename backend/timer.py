def remaining(timer_status, long_break_interval, timer_remain_total_secs, long_interval_count):
    if timer_remain_total_secs > 0:
        timer_remain_total_secs -= 1
        
    if timer_remain_total_secs <= 0:
        if timer_status == "Study":
            long_interval_count += 1
            if long_interval_count % long_break_interval == 0:
                timer_status = "Long Break"
            else:
                timer_status = "Short Break"
        elif timer_status == "Short Break" or timer_status == "Long Break":
            timer_status = "Study"
        else:
            if timer_status == "Reset":
                print("Error: Timer status is reset, but the timer is still running.")
            else:
                print("Error: Timer status is not recognized.")
    
    return timer_status, timer_remain_total_secs, long_interval_count