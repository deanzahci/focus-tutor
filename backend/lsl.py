from pylsl import StreamInlet, resolve_streams

def get_lsl():
    print("Resolving streams")
    streams = resolve_streams(wait_time=2.0)
    eeg_stream = None

    for stream in streams:
        if stream.name() == 'PetalStream_eeg':
            eeg_stream = stream
            break

    if eeg_stream is None:
        print("Stream not found")
        exit(1)
    print("Inlet created")

    return StreamInlet(eeg_stream)

if __name__ == "__main__":
    inlet = get_lsl()
    while True:
        sample, timestamp = inlet.pull_sample()
        print(sample, timestamp)