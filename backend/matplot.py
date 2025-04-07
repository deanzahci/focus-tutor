import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

from backend.lsl import get_raw_eeg


def compute_bai(alpha_series, beta_series, theta_series, delta_series, fs):
    # Calculate derivatives (approximated by discrete differences)
    dt = 1.0 / fs
    d_alpha = np.gradient(alpha_series, dt)
    d_beta = np.gradient(beta_series, dt)
    d_theta = np.gradient(theta_series, dt)
    d_delta = np.gradient(delta_series, dt)
    bai_values = np.abs((d_alpha + d_theta) * d_delta - d_beta)
    return bai_values


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a


def apply_filter(data, fs, lowcut=0.5, highcut=50.0, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return filtfilt(b, a, data)


# data: 1D np.array of EEG samples for the epoch

def compute_power_spectrum(data, fs):
    fft_vals = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(len(data), 1.0/fs)
    psd = np.abs(fft_vals) ** 2
    return freqs, psd


def get_band_power(freqs, psd, band):
    idx = np.where((freqs >= band[0]) & (freqs <= band[1]))[0]
    return np.mean(psd[idx]) if len(idx) > 0 else 0


class RealtimeEEGPlot:
    def __init__(self, fs=256, epoch_size=1.0, max_len=60):
        self.fs = fs
        self.epoch_size = epoch_size
        self.max_len = max_len
        
        self.alpha_vals = []
        self.theta_vals = []
        self.bai_vals = []
        self.time_pts = []
        self.current_time = 0.0
        
        # Create figure and axis for plotting
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Real-Time EEG: Alpha, Theta, and BAI")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        
        # Initialize line objects with empty data
        self.line_alpha, = self.ax.plot([], [], label='Alpha', alpha=0.5)
        self.line_theta, = self.ax.plot([], [], label='Theta', alpha=0.5)
        self.line_bai, = self.ax.plot([], [], label='BAI', alpha=0.8)
        self.ax.legend()
        
    def update(self):
        # Get new data chunk
        chunk_samples = int(self.fs * self.epoch_size)
        data = get_raw_eeg()  # This should return a 1D np.array of EEG samples for the epoch
        filtered_data = apply_filter(data, self.fs, 0.5, 50.0)
        freqs, psd = compute_power_spectrum(filtered_data, self.fs)
        
        alpha_power = get_band_power(freqs, psd, (8, 12))
        theta_power = get_band_power(freqs, psd, (4, 8))
        
        if len(self.alpha_vals) > 1:
            bai_series = compute_bai(np.array(self.alpha_vals), np.zeros_like(self.alpha_vals), 
                                     np.array(self.theta_vals), np.zeros_like(self.theta_vals), self.fs)
            current_bai = bai_series[-1]
        else:
            current_bai = 0
        
        # Update current time and append new data
        self.current_time += self.epoch_size
        self.time_pts.append(self.current_time)
        self.alpha_vals.append(alpha_power)
        self.theta_vals.append(theta_power)
        self.bai_vals.append(current_bai)
        
        # Limit data points to last max_len seconds
        if len(self.time_pts) > self.max_len:
            self.time_pts.pop(0)
            self.alpha_vals.pop(0)
            self.theta_vals.pop(0)
            self.bai_vals.pop(0)
        
        # Update line data
        self.line_alpha.set_data(self.time_pts, self.alpha_vals)
        self.line_theta.set_data(self.time_pts, self.theta_vals)
        self.line_bai.set_data(self.time_pts, self.bai_vals)
        
        # Update axes limits
        self.ax.set_xlim(self.time_pts[0], self.time_pts[-1])
        all_vals = self.alpha_vals + self.theta_vals + self.bai_vals
        if all_vals:
            ymin = min(all_vals)
            ymax = max(all_vals)
            if ymin == ymax:
                ymax += 1
            self.ax.set_ylim(ymin, ymax)
        
        return self.fig


if __name__ == "__main__":
    plotter = RealtimeEEGPlot()
    plt.ion()
    while True:
        plotter.update()
        plt.pause(0.01)