import sounddevice as sd
import numpy as np
import wave
from scipy.signal import butter, lfilter

# Konfigurasi Filter
samplerate = 44100  # Frekuensi sampling
lowcut = 1015  # Batas bawah frekuensi
highcut = 1025  # Batas atas frekuensi
output_file = "filtered_microphone_audio.wav"  # Nama file output

# Fungsi untuk membuat bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

# Fungsi untuk menangani audio dari mikrofon
def process_microphone_audio(duration):
    audio_data = []  # Buffer untuk menyimpan data audio

    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        # Terapkan filter
        filtered_data = bandpass_filter(indata[:, 0], lowcut, highcut, samplerate)
        audio_data.extend(filtered_data)  # Simpan data yang difilter
        print("Realtime data difilter:", filtered_data[:10])  # Cetak 10 data pertama (opsional)

    # Stream audio secara realtime
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate):
        print("Merekam dari mikrofon... Tekan Ctrl+C untuk berhenti.")
        sd.sleep(int(duration * 1000))

    # Simpan data audio yang telah difilter ke file WAV
    audio_array = np.array(audio_data, dtype=np.int16)
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 byte per sampel (16-bit audio)
        wf.setframerate(samplerate)
        wf.writeframes(audio_array.tobytes())
    print(f"Audio hasil filter disimpan di {output_file}")

# Fungsi untuk menangani audio dari file
def process_audio_file(file_path):
    with wave.open(file_path, 'rb') as wf:
        # Membaca metadata file
        channels = wf.getnchannels()
        samplerate = wf.getframerate()
        nframes = wf.getnframes()
        print(f"File audio memiliki {channels} channel, samplerate {samplerate}, total frame {nframes}")
        
        # Membaca data audio
        audio_data = np.frombuffer(wf.readframes(nframes), dtype=np.int16)
        
        # Terapkan bandpass filter
        filtered_data = bandpass_filter(audio_data, lowcut, highcut, samplerate)
        print("Audio file telah difilter.")
        
        # Simpan hasil filter ke file baru
        output_file = "filtered_audio.wav"
        with wave.open(output_file, 'wb') as out_wf:
            out_wf.setnchannels(channels)
            out_wf.setsampwidth(wf.getsampwidth())
            out_wf.setframerate(samplerate)
            out_wf.writeframes(filtered_data.astype(np.int16).tobytes())
        print(f"Audio hasil filter disimpan di {output_file}")

# Fungsi untuk memutar audio dan mengukur dB secara realtime
def play_audio_and_measure_db(file_path):
    def audio_callback(outdata, frames, time, status):
        if status:
            print(status)
        data = wf.readframes(frames)
        if not data:
            raise sd.CallbackStop
        outdata[:] = np.frombuffer(data, dtype=np.int16).reshape(-1, 1)
        # Hitung dB
        rms = np.sqrt(np.mean(np.square(outdata)))
        db = 20 * np.log10(rms) if rms > 0 else -np.inf
        print(f"Nilai dB: {db:.2f}")

    # Membuka file audio
    with wave.open(file_path, 'rb') as wf:
        with sd.OutputStream(samplerate=wf.getframerate(), channels=wf.getnchannels(), callback=audio_callback):
            print(f"Memutar audio dari file {file_path}")
            while True:
                try:
                    sd.sleep(100)
                except sd.CallbackStop:
                    break
            print("Pemutaran selesai.")

# Menu utama
def main():
    print("Pilih sumber audio:")
    print("1. Mikrofon realtime")
    print("2. File audio")
    print("3. Putar file hasil rekaman dan tampilkan dB")
    choice = input("Masukkan pilihan (1/2/3): ")

    if choice == '1':
        duration = int(input("Masukkan durasi rekaman (dalam detik): "))
        process_microphone_audio(duration)
    elif choice == '2':
        file_path = input("Masukkan path file audio (misal: audio.wav): ")
        process_audio_file(file_path)
    elif choice == '3':
        file_path = input("Masukkan path file audio hasil rekaman (misal: filtered_microphone_audio.wav): ")
        play_audio_and_measure_db(file_path)
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
