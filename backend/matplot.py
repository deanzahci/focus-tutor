import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class RealTimeBAIView(tk.Frame):
    def __init__(self, parent, update_ms=1000):
        super().__init__(parent)
        self.update_ms = update_ms
        self.t = []
        self.bai = []
        self.t_elapsed = 0.0
        self._build_figures()

    def _build_figures(self):
        fig = Figure(figsize=(5, 2.5), dpi=100)
        self.ax_bai = fig.add_subplot(1, 1, 1)
        self.ax_bai.set_title("Brain Activity Index")
        self.ax_bai.set_xlabel("Time (s)")
        self.ax_bai.set_ylabel("BAI")
        (self.line_bai,) = self.ax_bai.plot([], [], alpha=0.8)

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_bai(self, bai_value):
        self.t_elapsed += self.update_ms / 1000.0
        self.t.append(self.t_elapsed)
        self.bai.append(bai_value)

        self.line_bai.set_data(self.t, self.bai)
        self.ax_bai.relim()
        self.ax_bai.autoscale_view()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    view = RealTimeBAIView(root, update_ms=500)
    view.pack(fill="both", expand=True)

    def dummy_update():
        bai_val = np.random.rand()
        view.update_bai(bai_val)
        view.after(view.update_ms, dummy_update)

    view.after(view.update_ms, dummy_update)
    root.mainloop()