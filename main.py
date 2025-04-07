import tkinter as tk
from tkinter import ttk
import webbrowser
import threading
import datetime

from backend.timer import remaining
from backend.bai import analyze_eeg

def main():
    app = Application()
    app.mainloop()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        # Window
        self.title("Focustutor")
        self.geometry("600x600")

        self.study_time = 25
        self.short_break_time = 5
        self.long_break_time = 15
        self.long_break_interval = 4

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Home')
        self.notebook.add(self.tab2, text='Setting')
        self.setting_tab = SettingTab(self.tab2, self)
        self.setting_tab.pack(expand=True, fill='both')
        self.home_tab = HomeTab(self.tab1, self)
        self.home_tab.pack(expand=True, fill='both')

class HomeTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.timer_status = "Reset"
        self.bci_status = False
        self.timer_remain_total_secs = 0
        self.timer_remain_mins = 0
        self.timer_remain_secs = 0
        self.long_interval_count = 0
        self.timer_loop_id = None
        
        self.draw_buttons()

        # Timer
        self.timer_mode = ttk.Label(self, text=f"Mode: {self.timer_status}")
        self.timer_mode.grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        self.timer_time = ttk.Label(self, text=f"Remaining: ")
        self.timer_time.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

        # Focus state
        self.focus_state = ttk.Label(self, text=f"State: ")
        self.focus_state.grid(row=4, column=0, padx=10, pady=10, sticky='ew')
        self.focus_state_value = ttk.Label(self, text=f"Score: ")
        self.focus_state_value.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

        if self.bci_status:
            self.matplot()

    def cancel_timer_loop(self):
        if self.timer_loop_id is not None:
            self.after_cancel(self.timer_loop_id)
            self.timer_loop_id = None

    def draw_buttons(self):
        for widget in self.grid_slaves():
            if int(widget.grid_info()["row"]) in (0, 1, 2):
                widget.destroy()

        if self.timer_status == "Reset":
            ttk.Button(self, text="Start Studying", command=self.set_study).grid(row=0, column=0, padx=10, pady=10, sticky='ew')
            if not self.bci_status:
                ttk.Button(self, text="Start BCI", command=self.start_bci).grid(row=0, column=1, padx=10, pady=10, sticky='ew')
            else:
                ttk.Button(self, text="Stop BCI", command=self.stop_bci).grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        elif self.timer_status == "Short Break" or self.timer_status == "Long Break":
            ttk.Button(self, text="Start Studying", command=self.set_study).grid(row=1, column=0, padx=10, pady=10, sticky='ew')
            ttk.Button(self, text="Reset", command=self.reset).grid(row=1, column=1, padx=10, pady=10, sticky='ew')
            if not self.bci_status:
                ttk.Button(self, text="Start BCI", command=self.start_bci).grid(row=1, column=2, padx=10, pady=10, sticky='ew')
            else:
                ttk.Button(self, text="Stop BCI", command=self.stop_bci).grid(row=1, column=2, padx=10, pady=10, sticky='ew')
        else:
            ttk.Button(self, text="Start Short Break", command=self.set_short_break).grid(row=2, column=0, padx=10, pady=10, sticky='ew')
            ttk.Button(self, text="Start Long Break", command=self.set_long_break).grid(row=2, column=1, padx=10, pady=10, sticky='ew')
            ttk.Button(self, text="Reset", command=self.reset).grid(row=2, column=2, padx=10, pady=10, sticky='ew')
            if not self.bci_status:
                ttk.Button(self, text="Start BCI", command=self.start_bci).grid(row=2, column=3, padx=10, pady=10, sticky='ew')
            else:
                ttk.Button(self, text="Stop BCI", command=self.stop_bci).grid(row=2, column=3, padx=10, pady=10, sticky='ew')

    def set_study(self):
        self.cancel_timer_loop()
        self.timer_status = "Study"
        self.timer_remain_total_secs = 0
        self.update_timer()
        self.draw_buttons()
        self.timer_mode.config(text=f"Mode: {self.timer_status}")
    
    def set_short_break(self):
        self.cancel_timer_loop()
        self.timer_status = "Short Break"
        self.timer_remain_total_secs = 0
        self.update_timer()
        self.draw_buttons()
        self.timer_mode.config(text=f"Mode: {self.timer_status}")

    def set_long_break(self):
        self.cancel_timer_loop()
        self.timer_status = "Long Break"
        self.timer_remain_total_secs = 0
        self.update_timer()
        self.draw_buttons()
        self.timer_mode.config(text=f"Mode: {self.timer_status}")
    
    def reset(self):
        self.cancel_timer_loop()
        self.timer_status = "Reset"
        self.timer_remain_total_secs = 0
        self.timer_remain_mins = 0
        self.timer_remain_secs = 0
        self.long_interval_count = 0
        self.draw_buttons()
        self.timer_mode.config(text=f"Mode: {self.timer_status}")
        self.timer_time.config(text=f"Remaining: {self.timer_remain_mins:02}:{self.timer_remain_secs:02}")

    def update_timer(self):
        if self.timer_status == "Study":
            if self.timer_remain_total_secs == 0:
                self.timer_remain_total_secs = self.app.study_time * 60
            self.timer_status, self.timer_remain_total_secs, self.long_interval_count = remaining(self.timer_status, self.app.long_break_interval, self.timer_remain_total_secs, self.long_interval_count)
        elif self.timer_status == "Short Break":
            if self.timer_remain_total_secs == 0:
                self.timer_remain_total_secs = self.app.short_break_time * 60
            self.timer_status, self.timer_remain_total_secs, self.long_interval_count = remaining(self.timer_status, self.app.long_break_interval, self.timer_remain_total_secs, self.long_interval_count)
        elif self.timer_status == "Long Break":
            if self.timer_remain_total_secs == 0:
                self.timer_remain_total_secs = self.app.long_break_time * 60
            self.timer_status, self.timer_remain_total_secs, self.long_interval_count = remaining(self.timer_status, self.app.long_break_interval, self.timer_remain_total_secs, self.long_interval_count)
        else:
            return # self.timer_status == "Reset" so the timer stops

        self.timer_remain_mins, self.timer_remain_secs = divmod(self.timer_remain_total_secs, 60)
        self.timer_time.config(text=f"Remaining: {self.timer_remain_mins:02}:{self.timer_remain_secs:02}")

        if self.timer_status != "Reset":
            self.timer_loop_id = self.after(1000, self.update_timer)
    
    def start_bci(self):
        self.bci_status = True
        
        # Create a new thread only if it doesn't exist or is not alive to prevent multiple threads running simultaneously
        if not hasattr(self, 'bci_thread') or not self.bci_thread.is_alive():
            self.bci_thread = threading.Thread(target=self.run_analyze_eeg, daemon=True)
            self.bci_thread.start()

        self.draw_buttons()

    def stop_bci(self):
        self.bci_status = False
        self.draw_buttons()
        self.focus_state.config(text="State: ")
        self.focus_state_value.config(text="Score: ")

    # Run the analyze_eeg function in a separate thread (threading)
    def run_analyze_eeg(self):
        while self.bci_status:
            (focus_state_value, focus_state) = analyze_eeg()
            self.after(0, self.update_bci_ui, focus_state_value, focus_state)

    # UI update must be done in the main thread
    def update_bci_ui(self, focus_state_value, focus_state):
        print(f"Focus state: {focus_state_value} / 100 / {datetime.datetime.now()}")
        if self.bci_status:
            self.focus_state.config(text=f"State: {focus_state}")
            self.focus_state_value.config(text=f"Score: {focus_state_value} / 100")

class SettingTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.draw_settings()

        ttk.Button(self, text="DAHCI", command=self.open_dahci).grid(row=5, column=0, padx=10, pady=10, sticky='ew')
        ttk.Button(self, text="GitHub", command=self.open_github).grid(row=5, column=1, padx=10, pady=10, sticky='ew')

    def draw_settings(self):
        ttk.Label(self, text="Study Time / 1 ~ 120 (min)").grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        self.study_time_spinbox = ttk.Spinbox(self, from_=1, to=120, increment=1)
        self.study_time_spinbox.bind("<FocusOut>", lambda e: self.update_study_time())
        self.study_time_spinbox.bind("<Return>", lambda e: self.update_study_time())
        self.study_time_spinbox.delete(0, tk.END)
        self.study_time_spinbox.insert(0, str(self.app.study_time))
        self.study_time_spinbox.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        ttk.Label(self, text="Short Break Time / 1 ~ 15 (min)").grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.short_break_time_spinbox = ttk.Spinbox(self, from_=1, to=15, increment=1)
        self.short_break_time_spinbox.bind("<FocusOut>", lambda e: self.update_short_break_time())
        self.short_break_time_spinbox.bind("<Return>", lambda e: self.update_short_break_time())
        self.short_break_time_spinbox.delete(0, tk.END)
        self.short_break_time_spinbox.insert(0, str(self.app.short_break_time))
        self.short_break_time_spinbox.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        ttk.Label(self, text="Long Break Time / 1 ~ 30 (min)").grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.long_break_time_spinbox = ttk.Spinbox(self, from_=1, to=30, increment=1)
        self.long_break_time_spinbox.bind("<FocusOut>", lambda e: self.update_long_break_time())
        self.long_break_time_spinbox.bind("<Return>", lambda e: self.update_long_break_time())
        self.long_break_time_spinbox.delete(0, tk.END)
        self.long_break_time_spinbox.insert(0, str(self.app.long_break_time))
        self.long_break_time_spinbox.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        ttk.Label(self, text="Long Break Interval / 0 ~ 10").grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        self.long_break_interval_spinbox = ttk.Spinbox(self, from_=0, to=4, increment=1)
        self.long_break_interval_spinbox.bind("<FocusOut>", lambda e: self.update_long_break_interval())
        self.long_break_interval_spinbox.bind("<Return>", lambda e: self.update_long_break_interval())
        self.long_break_interval_spinbox.delete(0, tk.END)
        self.long_break_interval_spinbox.insert(0, str(self.app.long_break_interval))
        self.long_break_interval_spinbox.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

        ttk.Button(self, text="Reset to default", command=self.reset_to_default).grid(row=4, column=0, padx=10, pady=10, sticky='ew', columnspan=2)


    def update_study_time(self):
        value = int(self.study_time_spinbox.get())
        if 1 <= value <= 120:
            self.app.study_time = value
        else:
            self.study_time_spinbox.delete(0, tk.END)
            self.study_time_spinbox.insert(0, str(self.app.study_time))
    
    def update_short_break_time(self):
        value = int(self.short_break_time_spinbox.get())
        if 1 <= value <= 15:
            self.app.short_break_time = value
        else: 
            self.short_break_time_spinbox.delete(0, tk.END)
            self.short_break_time_spinbox.insert(0, str(self.app.short_break_time))
    
    def update_long_break_time(self):
        value = int(self.long_break_time_spinbox.get())
        if 1 <= value <= 30:
            self.app.long_break_time = value
        else:
            self.long_break_time_spinbox.delete(0, tk.END)
            self.long_break_time_spinbox.insert(0, str(self.app.long_break_time))

    def update_long_break_interval(self):
        value = int(self.long_break_interval_spinbox.get())
        if 0 <= value <= 10:
            self.app.long_break_interval = value
        else:
            self.long_break_interval_spinbox.delete(0, tk.END)
            self.long_break_interval_spinbox.insert(0, str(self.app.long_break_interval))

    def reset_to_default(self):
        self.app.study_time = 25
        self.app.short_break_time = 5
        self.app.long_break_time = 15
        self.app.long_break_interval = 4

        self.study_time_spinbox.delete(0, tk.END)
        self.study_time_spinbox.insert(0, str(self.app.study_time))
        self.short_break_time_spinbox.delete(0, tk.END)
        self.short_break_time_spinbox.insert(0, str(self.app.short_break_time))
        self.long_break_time_spinbox.delete(0, tk.END)
        self.long_break_time_spinbox.insert(0, str(self.app.long_break_time))
        self.long_break_interval_spinbox.delete(0, tk.END)
        self.long_break_interval_spinbox.insert(0, str(self.app.long_break_interval))

    def open_dahci(self):
        webbrowser.open("https://linktr.ee/deanzahci")
    
    def open_github(self):
        webbrowser.open("https://github.com/deanzahci/focustutor")

if __name__ == '__main__':
    main()
