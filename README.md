# Focus Tutor

**Focus Tutor** is an EEG-based focus monitoring application that helps users track their concentration levels during study or work sessions. This project is based on the Brain Activity Index (BAI) introduced in the paper:

> **"Brain Activity Based Metrics for Driver Drowsiness Detection"**  
> Bajaj, R., et al. (2018)  
> _In: Advances in Intelligent Systems and Computing_, Springer  
> https://link.springer.com/chapter/10.1007/978-3-319-92285-0_49

While the original paper focused on **driver drowsiness detection**, Focus Tutor adapts the BAI metric to measure focus and attention during **studying or work activities**. The application provides real-time feedback on concentration states and integrates a Pomodoro-style timer to support productive work sessions.

---

## Features

- **Real-time EEG Analysis**: Measures brain activity using BAI algorithm to assess focus levels (Low, Medium, High, Very High)
- **Pomodoro Timer**: Built-in study/break timer with customizable intervals
- **Live Visualization**: Real-time BAI score plotting with matplotlib
- **LSL Integration**: Streams EEG data via Lab Streaming Layer (pylsl) from compatible devices (e.g., PetalStream_eeg)
- **GUI Interface**: User-friendly Tkinter-based interface with tabs for home and settings

---

## Technical Overview

### Brain Activity Index (BAI)

The BAI is computed using EEG frequency band powers:

$$
\text{BAI} = \left| \left( \frac{d\alpha}{dt} + \frac{d\theta}{dt} \right) \cdot \frac{d\delta}{dt} - \frac{d\beta}{dt} \right|
$$

Where:
- **Alpha (α)**: 8-12 Hz — Associated with relaxed alertness
- **Beta (β)**: 13-30 Hz — Associated with active thinking and focus
- **Theta (θ)**: 4-8 Hz — Associated with drowsiness and light sleep
- **Delta (δ)**: 0.5-4 Hz — Associated with deep sleep

The derivatives of these band powers are calculated over time epochs, and the BAI value reflects the dynamic changes in brain state related to attention and focus.

### Architecture

```
focustutor/
├── main.py                 # Main application GUI (Tkinter)
├── backend/
│   ├── bai.py             # BAI computation pipeline (filtering, epoching, FFT, BAI formula)
│   ├── lsl.py             # Lab Streaming Layer interface for EEG data acquisition
│   ├── matplot.py         # Real-time BAI visualization with matplotlib
│   └── timer.py           # Pomodoro timer logic
├── pyproject.toml         # Project dependencies (uv/pip)
└── README.md              # This file
```

### Processing Pipeline

1. **Data Acquisition** (`backend/lsl.py`):
   - Resolves EEG stream via pylsl (`PetalStream_eeg`)
   - Averages AF7 and AF8 channels for frontal cortex monitoring
   - Samples at 256 Hz

2. **Preprocessing** (`backend/bai.py`):
   - Butterworth bandpass filter (0.5-50 Hz) to remove noise
   - Segmentation into 1-second epochs

3. **Feature Extraction** (`backend/bai.py`):
   - FFT-based power spectrum computation for each epoch
   - Band power extraction for alpha, beta, theta, delta

4. **BAI Calculation** (`backend/bai.py`):
   - Numerical gradient (time derivative) of band powers
   - BAI formula application
   - Normalization and scoring (1-100 scale)

5. **Focus Classification**:
   - **Low**: BAI score < 25
   - **Medium**: 25 ≤ BAI score < 50
   - **High**: 50 ≤ BAI score < 75
   - **Very High**: BAI score ≥ 75

---

## Installation

### Prerequisites

- Python 3.10 or higher
- EEG device compatible with Lab Streaming Layer (e.g., Emotiv, Muse, or PetalStream)

### Setup with UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package manager. Install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install dependencies:

```bash
cd focustutor
uv sync
```

### Alternative: Setup with pip

```bash
cd focustutor
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

---

## Usage

### Running the Application

```bash
uv run python main.py
```

Or with activated virtual environment:

```bash
python main.py
```

### EEG Stream Requirement

Ensure your EEG device is streaming data via LSL with the stream name `PetalStream_eeg`. The application will automatically resolve and connect to this stream when "Start BCI" is clicked.

### GUI Controls

- **Start Studying**: Begin a study session with the timer
- **Start Short Break / Long Break**: Take breaks (configurable in Settings tab)
- **Reset**: Stop timer and reset session
- **Start/Stop BCI**: Toggle EEG analysis and visualization
- **Settings Tab**: Adjust study time, break durations, and long break intervals

---

## Dependencies

- **numpy** (≥2.2.6): Numerical computing and array operations
- **scipy** (≥1.15.3): Signal processing (Butterworth filter, FFT)
- **matplotlib** (≥3.10.6): Real-time BAI plotting
- **pylsl** (≥1.17.6): Lab Streaming Layer for EEG data streaming

---

## Performance Evaluation and Limitations

### Challenges in Performance Measurement

Evaluating the accuracy of BAI-based focus detection is inherently difficult due to:

1. **Lack of Ground Truth Labels**: Concentration is subjective and varies significantly across individuals. Obtaining reliable labeled data (e.g., "focused" vs. "unfocused" states) requires controlled experiments, self-reporting, or behavioral metrics—all of which introduce noise and bias.

2. **Individual Variability**: EEG patterns differ by age, cognitive state, fatigue, and environmental factors. A model trained on one population may not generalize well.

3. **Hardware Dependency**: Real-time EEG data quality depends on electrode placement, skin impedance, and device specifications. Reproducibility across devices is limited.

4. **Ethical and Privacy Concerns**: Collecting labeled EEG data from human subjects requires informed consent and ethical approval, making large-scale dataset creation resource-intensive.

### Recommended Evaluation Strategies

Given these constraints, the following approaches can provide partial validation:

- **Offline Dataset Testing**: Use public EEG datasets (e.g., [DEAP](http://www.eecs.qmul.ac.uk/mmv/datasets/deap/), [PhysioNet](https://physionet.org/)) with attention/valence labels to benchmark BAI against known states.
- **Latency and Real-Time Performance**: Measure processing time from EEG acquisition to BAI output (target: <1 second per epoch).
- **User Studies**: Conduct small-scale experiments (5-10 participants) comparing self-reported focus levels with BAI scores. Calculate correlation coefficients.
- **Comparative Analysis**: Compare BAI with alternative BCI metrics (e.g., Engagement Index, Alpha/Beta ratio) using open-source tools like [MNE-Python](https://mne.tools/).
- **Simulation Testing**: Generate synthetic EEG signals with known characteristics to validate algorithmic correctness.

### Current Status

This project is a **prototype application** demonstrating the BAI methodology adapted from driver drowsiness research. Formal performance validation has not been conducted due to the labeling challenges described above. Users should interpret BAI scores as **relative indicators** of focus trends rather than absolute measurements.

### Future Work

- Collect labeled training data through controlled study experiments
- Implement machine learning models (e.g., SVM, Random Forest) trained on labeled data
- Add user calibration mode to personalize BAI thresholds
- Explore unsupervised or semi-supervised learning approaches
- Integrate additional physiological signals (heart rate, eye tracking) for multimodal analysis

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## References

- Bajaj, R., Khanna, K., Jha, A., & Tripathi, S. (2018). Brain Activity Based Metrics for Driver Drowsiness Detection. In: Lödding, H., Riedel, R., Thoben, KD., von Cieminski, G., Kiritsis, D. (eds) _Advances in Production Management Systems. Smart Manufacturing for Industry 4.0_. APMS 2018. IFIP Advances in Information and Communication Technology, vol 536. Springer, Cham. https://doi.org/10.1007/978-3-319-92285-0_49

---

## Acknowledgments

- Springer for the original BAI research paper
- [Lab Streaming Layer](https://labstreaminglayer.org/) for real-time data streaming protocols
- Python scientific computing community (NumPy, SciPy, Matplotlib)
