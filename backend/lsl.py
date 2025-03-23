import streamtlit as st
from pylsl import StreamInlet, resolve_streams

# Function to get the LSL stream from Muse 2 via Petal Metrics
def get_inlet():
    print("Resolving streams")
    streams = resolve_streams(wait_time=1)
    eeg_stream = None

    for stream in streams:
        if stream.name() == 'PetalStream_eeg':
            eeg_stream = stream
            break

    if eeg_stream is None:
        st.error("Stream not found")
        exit(1)
    print("Inlet created")

    return StreamInlet(eeg_stream)

def get_af7_af8_data():
    inlet = get_inlet()

    try:
        sample, timestamp = inlet.pull_sample()
        af7, af8 = sample[1], sample[2]
        return af7, af8, timestamp
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        return None, None, None

if __name__ == "__main__":
    inlet = get_inlet()
    while True:
        sample, timestamp = inlet.pull_sample()
        print(sample, timestamp)