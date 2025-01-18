import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db

# Inisialisasi Firebase
cred = credentials.Certificate("azimuth-360-firebase-adminsdk-fbsvc-b3f464aaf1.json")  # Ganti dengan nama file JSON Anda
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://azimuth-360-default-rtdb.asia-southeast1.firebasedatabase.app/"  # Ganti dengan URL database Anda
})

# Fungsi untuk mengambil data dari Firebase
def fetch_data():
    try:
        ref = db.reference("/")  # Path root database
        data = ref.get()
        display_data(data)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data:\n{e}")

# Fungsi untuk menampilkan data di antarmuka
def display_data(data):
    text_display.delete("1.0", tk.END)  # Bersihkan teks lama
    if data:
        for key, value in data.items():
            text_display.insert(tk.END, f"{key}: {value}\n")
    else:
        text_display.insert(tk.END, "No data found.")

# Aplikasi Desktop dengan Tkinter
root = tk.Tk()
root.title("Firebase Realtime Database Viewer")
root.geometry("500x400")

# Label Judul
label_title = tk.Label(root, text="Firebase Realtime Database Viewer", font=("Helvetica", 16))
label_title.pack(pady=10)

# Tombol Fetch Data
btn_fetch = tk.Button(root, text="Fetch Data", command=fetch_data, font=("Helvetica", 12))
btn_fetch.pack(pady=10)

# Text Widget untuk Menampilkan Data
text_display = tk.Text(root, wrap=tk.WORD, font=("Courier", 12), height=15)
text_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Menjalankan aplikasi
root.mainloop()
