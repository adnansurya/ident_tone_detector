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
        if data:
            azimuth_value.set(data.get("azimuth", "N/A"))
            ident_value.set(data.get("ident", "N/A"))
        else:
            azimuth_value.set("N/A")
            ident_value.set("N/A")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data:\n{e}")

    # Panggil fungsi ini lagi setelah 1 detik
    root.after(1000, fetch_data)

# Aplikasi Desktop Tkinter
root = tk.Tk()
root.title("Firebase RTDB Monitor")
root.geometry("400x300")
root.configure(bg="#2c3e50")

# Judul
title = tk.Label(root, text="Ident Azimuth Monitor", font=("Helvetica", 16, "bold"), fg="white", bg="#2c3e50")
title.pack(pady=10)

# Frame untuk indikator
frame = tk.Frame(root, bg="#34495e", bd=2, relief="groove")
frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Azimuth Label
tk.Label(frame, text="Azimuth:", font=("Helvetica", 14), fg="white", bg="#34495e").grid(row=0, column=0, sticky="w", padx=10, pady=10)
azimuth_value = tk.StringVar(value="Loading...")
azimuth_label = tk.Label(frame, textvariable=azimuth_value, font=("Helvetica", 14), fg="yellow", bg="#34495e")
azimuth_label.grid(row=0, column=1, sticky="e", padx=10, pady=10)

# Ident Label
tk.Label(frame, text="Ident:", font=("Helvetica", 14), fg="white", bg="#34495e").grid(row=1, column=0, sticky="w", padx=10, pady=10)
ident_value = tk.StringVar(value="Loading...")
ident_label = tk.Label(frame, textvariable=ident_value, font=("Helvetica", 14), fg="yellow", bg="#34495e")
ident_label.grid(row=1, column=1, sticky="e", padx=10, pady=10)

# Tombol Keluar
exit_button = tk.Button(root, text="Exit", font=("Helvetica", 12), bg="#e74c3c", fg="white", command=root.quit)
exit_button.pack(pady=5)

# Mulai mengambil data secara periodik
fetch_data()

# Menjalankan aplikasi
root.mainloop()
