import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Credenziali fittizie per il login
USER_CREDENTIALS = {"admin": ("1234", "titolare"), "user": ("password", "dipendente")}

# Database simulato
DATABASE = "gestionale.db"

# Funzione per autenticare l'utente
def login():
    username = entry_user.get()
    password = entry_pass.get()
    
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username][0] == password:
        role = USER_CREDENTIALS[username][1]
        #messagebox.showinfo("Login", f"Accesso riuscito come {role}!")
        root.withdraw()  # Nasconde la finestra di login
        open_dashboard(role)  # Apre la dashboard con il ruolo specifico
    else:
        messagebox.showerror("Errore", "Credenziali non valide!")

# Funzione per aprire la dashboard principale in base al ruolo
def open_dashboard(role):
    dashboard = tk.Toplevel()
    dashboard.title(f"Dashboard - {role.capitalize()}")
    dashboard.geometry("800x600")
    
    if role == "dipendente":
        # Dashboard per dipendente
        dashboard_label = tk.Label(dashboard, text="Benvenuto nella Dashboard Dipendente", font=("Arial", 14))
        dashboard_label.pack(pady=10)
        
        frame_pulsanti = tk.Frame(dashboard)
        frame_pulsanti.pack(side=tk.LEFT, padx=20, pady=20)

        # Pulsanti per il dipendente
        tk.Button(frame_pulsanti, text="📌 Aggiungi Ordine", width=20, command=aggiungi_ordine).pack(pady=5)
        tk.Button(frame_pulsanti, text="🔎 Cerca Ordine", width=20, command=cerca_ordine).pack(pady=5)
        tk.Button(frame_pulsanti, text="👤 Cerca Cliente", width=20, command=cerca_cliente).pack(pady=5)
        tk.Button(frame_pulsanti, text="📊 Grafici in Real Time", width=20, command=mostra_grafici).pack(pady=5)
        tk.Button(frame_pulsanti, text="📑 Genera Report", width=20, command=generare_report).pack(pady=5)

    else:
        # Dashboard per titolare
        dashboard_label = tk.Label(dashboard, text="Benvenuto nella Dashboard Titolare", font=("Arial", 14))
        dashboard_label.pack(pady=10)
        
        frame_pulsanti = tk.Frame(dashboard)
        frame_pulsanti.pack(side=tk.LEFT, padx=20, pady=20)

        # Pulsanti per il titolare
        tk.Button(frame_pulsanti, text="📌 Aggiungi Ordine", width=20, command=aggiungi_ordine).pack(pady=5)
        tk.Button(frame_pulsanti, text="🔎 Cerca Ordine", width=20, command=cerca_ordine).pack(pady=5)
        tk.Button(frame_pulsanti, text="👤 Cerca Cliente", width=20, command=cerca_cliente).pack(pady=5)
        tk.Button(frame_pulsanti, text="📊 Grafici in Real Time", width=20, command=mostra_grafici).pack(pady=5)
        tk.Button(frame_pulsanti, text="📑 Genera Report", width=20, command=generare_report).pack(pady=5)
        tk.Button(frame_pulsanti, text="🔄 Assegna Cliente a Dipendente", width=20, command=assegna_cliente).pack(pady=5)

# Funzione per aggiungere un ordine
def aggiungi_ordine():
    messagebox.showinfo("Aggiungi Ordine", "Funzione non ancora implementata!")

# Funzione per cercare un ordine
def cerca_ordine():
    messagebox.showinfo("Cerca Ordine", "Funzione non ancora implementata!")

# Funzione per cercare un cliente
def cerca_cliente():
    messagebox.showinfo("Cerca Cliente", "Funzione non ancora implementata!")

# Funzione per generare i grafici in real time
def mostra_grafici():
    messagebox.showinfo("Grafici", "Funzione non ancora implementata!")

# Funzione per generare report sugli ordini effettuati
def generare_report():
    messagebox.showinfo("Genera Report", "Funzione non ancora implementata!")

# Funzione per assegnare cliente a dipendente (solo per titolare)
def assegna_cliente():
    messagebox.showinfo("Assegna Cliente", "Funzione non ancora implementata!")


# Creazione della finestra di login
root = tk.Tk()
root.title("Login")
root.geometry("500x500")

tk.Label(root, text="Username").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password").pack()
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login", command=login).pack(pady=10)


# Avvia l'interfaccia grafica
root.mainloop()
