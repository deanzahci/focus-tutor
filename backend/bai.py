import numpy as np
from scipy.signal import butter, filtfilt

from backend.lsl import get_raw_eeg

"""
Filter the input data using a bandpass filter and filtfilt.
"""


def apply_filter(data, fs, lowcut=0.5, highcut=50.0, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    # filtfilt applies the filter forward and backward
    filtered_data = filtfilt(b, a, data, axis=-1)
    return filtered_data


"""
Create a Butterworth bandpass filter.
"""


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    return b, a


"""
Segment continuous data into epochs.
"""


def segment_epochs(data, fs, epoch_length_s):
    n_samples_per_epoch = int(epoch_length_s * fs)
    n_total_samples = data.shape[-1]
    n_epochs = n_total_samples // n_samples_per_epoch

    epochs = []
    for i in range(n_epochs):
        start = i * n_samples_per_epoch
        end = start + n_samples_per_epoch
        if data.ndim == 1:
            epoch_data = data[start:end]
        else:
            epoch_data = data[:, start:end]
        epochs.append(epoch_data)
    return epochs


"""
Compute power spectrum for a single epoch using FFT.
"""


def compute_power_spectrum(epoch_data, fs):
    if epoch_data.ndim == 2:
        epoch_data = np.mean(epoch_data, axis=0)

    fft_vals = np.fft.rfft(epoch_data)
    fft_freqs = np.fft.rfftfreq(len(epoch_data), 1.0 / fs)

    psd = np.abs(fft_vals) ** 2
    return fft_freqs, psd


"""
Calculate average power in a specific frequency band.
"""


def get_band_power(freqs, psd, band):
    idx = np.where((freqs >= band[0]) & (freqs <= band[1]))[0]
    band_power = np.mean(psd[idx]) if len(idx) > 0 else 0
    return band_power


"""
Compute BAI using series of alpha, beta, theta, and delta powers.
"""


def compute_bai(alpha_series, beta_series, theta_series, delta_series, fs):
    # Calculate derivatives (approximated by discrete differences)
    dt = 1.0 / fs

    d_alpha = np.gradient(alpha_series, dt)
    d_beta = np.gradient(beta_series, dt)
    d_theta = np.gradient(theta_series, dt)
    d_delta = np.gradient(delta_series, dt)

    bai_values = np.abs((d_alpha + d_theta) * d_delta - d_beta)
    return bai_values


"""
Full pipeline: filter, epoch, power spectrum, then compute BAI state.
"""


def analyze_eeg(fs=256, epoch_length_s=1.0):
    data = get_raw_eeg()

    # Preprocessing
    filtered_data = apply_filter(data, fs, lowcut=0.5, highcut=50.0, order=5)
    epochs = segment_epochs(filtered_data, fs, epoch_length_s)

    alpha_band = (8.0, 12.0)
    beta_band = (13.0, 30.0)

    alpha_series = []
    beta_series = []
    theta_series = []
    delta_series = []

    # Process each epoch
    for epoch in epochs:
        freqs, psd = compute_power_spectrum(epoch, fs)
        alpha_power = get_band_power(freqs, psd, alpha_band)
        beta_power = get_band_power(freqs, psd, beta_band)
        theta_power = get_band_power(freqs, psd, (4.0, 8.0))
        delta_power = get_band_power(freqs, psd, (0.5, 4.0))

        alpha_series.append(alpha_power)
        beta_series.append(beta_power)
        theta_series.append(theta_power)
        delta_series.append(delta_power)

    alpha_series = np.array(alpha_series)
    beta_series = np.array(beta_series)
    theta_series = np.array(theta_series)
    delta_series = np.array(delta_series)

    bai_values = compute_bai(alpha_series, beta_series, theta_series, delta_series, fs)
    mean_bai = np.mean(bai_values)
    normalized_bai = min(1.0, max(0.0, mean_bai / 1e20))
    bai_score = round(1 + (normalized_bai * 99))

    if bai_score < 25:
        focus_state = "Low"
    elif bai_score < 50:
        focus_state = "Medium"
    elif bai_score < 75:
        focus_state = "High"
    else:
        focus_state = "Very High"

    return (int(mean_bai), focus_state)
