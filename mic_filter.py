import sounddevice as sd
import numpy as np
from scipy.signal import butter, lfilter

# Konfigurasi Filter
samplerate = 44100  # Frekuensi sampling
lowcut = 1015       # Batas bawah frekuensi (Hz)
highcut = 1025      # Batas atas frekuensi (Hz)

tone_treshold = -90
ident_counter = 0

# Fungsi untuk membuat bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

# Fungsi untuk memonitor audio dari mikrofon dan mengukur dB pada frekuensi 1020 Hz
def monitor_microphone():
    measurement_counter = 0  # Untuk menghitung hasil pengukuran

    def audio_callback(indata, frames, time, status):
        nonlocal measurement_counter  # Akses variabel di luar fungsi
        if status:
            print(f"Status Error: {status}")

        # Ambil data audio dari mikrofon
        audio_data = indata[:, 0]  # Ambil channel pertama jika stereo

        # Terapkan filter bandpass
        filtered_data = bandpass_filter(audio_data, lowcut, highcut, samplerate)
        
        # Hitung RMS dan dB dari sinyal yang telah difilter
        rms = np.sqrt(np.mean(np.square(filtered_data)))
        db = 20 * np.log10(rms) if rms > 0 else -np.inf
        

        # Tampilkan setiap 10 pengukuran
        if measurement_counter % 10 == 0 :
            global tone_treshold
            print(f"Realtime dB pada frekuensi 1020 Hz: {db:.2f} dB")
            if db >= tone_treshold:
                global ident_counter
                ident_counter += 1
                print("Ada Ident : " + str(ident_counter))
                
        measurement_counter += 1

    # Buka stream mikrofon
    with sd.InputStream(samplerate=samplerate, channels=1, callback=audio_callback):
        print("Monitoring mikrofon. Tekan Ctrl+C untuk berhenti.")
        try:
            while True:
                sd.sleep(100)
        except KeyboardInterrupt:
            print("\nMonitoring dihentikan.")

# Menu utama
def main():
    print("=== Pengukur dB Mikrofon pada Frekuensi 1020 Hz ===")
    monitor_microphone()

if __name__ == "__main__":
    main()
