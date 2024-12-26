import sounddevice as sd
import numpy as np
import wave
from scipy.signal import butter, lfilter

# Konfigurasi Filter
samplerate = 44100  # Frekuensi sampling
lowcut = 1015       # Batas bawah frekuensi (Hz)
highcut = 1025      # Batas atas frekuensi (Hz)

# Fungsi untuk membuat bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

# Fungsi untuk memutar audio dan mengukur dB pada frekuensi 1020 Hz
def play_audio_with_db_measurement(file_path):
    def audio_callback(outdata, frames, time, status):
        if status:
            print(f"Status Error: {status}")
        data = wf.readframes(frames)
        if not data:
            raise sd.CallbackStop
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Terapkan filter bandpass
        filtered_data = bandpass_filter(audio_data, lowcut, highcut, samplerate)
        
        # Hitung RMS dan dB dari sinyal yang telah difilter
        rms = np.sqrt(np.mean(np.square(filtered_data)))
        db = 20 * np.log10(rms) if rms > 0 else -np.inf
        print(f"Realtime dB pada frekuensi 1020 Hz: {db:.2f} dB")

        # Salurkan audio asli untuk output ke speaker
        outdata[:] = audio_data.reshape(-1, 1)

    # Membuka file audio
    with wave.open(file_path, 'rb') as wf:
        # Pastikan konfigurasi file audio sesuai
        if wf.getframerate() != samplerate or wf.getnchannels() != 1:
            print("File audio harus mono dengan samplerate 44.1 kHz.")
            return
        
        with sd.OutputStream(samplerate=samplerate, channels=1, callback=audio_callback):
            print(f"Memutar file audio: {file_path}")
            while True:
                try:
                    sd.sleep(100)
                except sd.CallbackStop:
                    break
            print("Pemutaran selesai.")

# Menu utama
def main():
    print("=== Audio Player dengan Pengukur dB pada 1020 Hz ===")
    file_path = input("Masukkan path file audio (misal: audio.wav): ")
    play_audio_with_db_measurement(file_path)

if __name__ == "__main__":
    main()
