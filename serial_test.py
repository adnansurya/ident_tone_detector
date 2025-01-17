import serial
import time

def main():
    # Konfigurasi serial port
    port = 'COM3'  # Sesuaikan dengan port Arduino
    baudrate = 9600  # Sesuaikan dengan baud rate pada Arduino

    try:
        # Membuka koneksi serial
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Terhubung ke {port} dengan baud rate {baudrate}")
        time.sleep(2)  # Menunggu Arduino siap

        while True:
            # Mengirimkan teks ke Arduino
            teks_kirim = input("Masukkan teks untuk dikirim (ketik 'exit' untuk keluar): ")
            if teks_kirim.lower() == 'exit':
                print("Mengakhiri koneksi serial.")
                break

            ser.write((teks_kirim + '\n').encode('utf-8'))
            print(f"Teks terkirim: {teks_kirim}")

            # Menerima respons dari Arduino
            if ser.in_waiting > 0:
                teks_terima = ser.readline().decode('utf-8').strip()
                print(f"Teks diterima: {teks_terima}")

    except serial.SerialException as e:
        print(f"Kesalahan pada serial port: {e}")

    finally:
        # Menutup koneksi serial
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Koneksi serial ditutup.")

if __name__ == "__main__":
    main()
