import sounddevice as sd
import numpy as np
from scipy.signal import butter, lfilter
import serial
import serial.tools.list_ports

# Konfigurasi Filter
samplerate = 44100  # Frekuensi sampling
lowcut = 1015       # Batas bawah frekuensi (Hz)
highcut = 1025      # Batas atas frekuensi (Hz)

tone_treshold = -90
ident_counter = 0

# Fungsi untuk mencari port dengan perangkat CH340
def find_ch340_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "CH340" in port.description:
            print(f"Perangkat CH340 ditemukan di {port.device}")
            return port.device
    print("Perangkat CH340 tidak ditemukan. Pastikan perangkat terhubung.")
    return None

# Fungsi untuk membuat bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

# Fungsi untuk memonitor audio dari mikrofon dan mengukur dB pada frekuensi 1020 Hz
def monitor_microphone(ser):
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
        if measurement_counter % 10 == 0:
            global tone_treshold
            print(f"Realtime dB pada frekuensi 1020 Hz: {db:.2f} dB")
            if db >= tone_treshold:
                global ident_counter
                ident_counter += 1
                print("Ada Ident : " + str(ident_counter))
                
                # Kirim teks "ident" melalui komunikasi serial
                if ser.is_open:
                    ser.write(b'ident\n')  # Kirim teks "ident" diakhiri newline
                else:
                    print("Port serial tidak terbuka!")
                
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
    ch340_port = find_ch340_port()
    if ch340_port is None:
        print("Tidak dapat melanjutkan tanpa perangkat CH340.")
        return

    try:
        with serial.Serial(ch340_port, 9600) as ser:
            monitor_microphone(ser)
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
