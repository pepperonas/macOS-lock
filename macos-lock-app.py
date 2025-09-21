#!/usr/bin/env python3
"""
Standalone macOS Lock App - vereinfachte Version für bessere Kompatibilität
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


class SimpleLockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("macOS Lock")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')

        self.is_locked = False
        self.lock_process = None
        self.check_timer = None

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#f0f0f0')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Icon
        self.lock_label = tk.Label(
            header_frame,
            text="🔒",
            font=('Arial', 48),
            bg='#f0f0f0'
        )
        self.lock_label.pack()
        
        # Status
        self.status_label = tk.Label(
            header_frame,
            text="Bereit zum Sperren",
            font=('Arial', 16),
            bg='#f0f0f0',
            fg='#333'
        )
        self.status_label.pack(pady=(10, 0))
        
        # Button
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        self.lock_button = tk.Button(
            button_frame,
            text="SPERREN",
            command=self.toggle_lock,
            font=('Arial', 18, 'bold'),
            bg='#0A84FF',
            fg='#000000',
            width=12,
            height=2,
            bd=0,
            highlightthickness=0,
            activebackground='#0060DF',
            activeforeground='#000000',
            cursor='hand2'
        )
        self.lock_button.pack()
        
    def toggle_lock(self):
        """Wechselt zwischen gesperrt und entsperrt"""
        if not self.is_locked:
            # Starte Sperre
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                lock_script = os.path.join(script_dir, 'macos-lock.py')
                
                if not os.path.exists(lock_script):
                    messagebox.showerror("Fehler", "macos-lock.py nicht gefunden!")
                    return
                
                self.lock_process = subprocess.Popen([sys.executable, lock_script])
                
                self.is_locked = True
                self.lock_label.config(text="🔓")
                self.status_label.config(text="System gesperrt", fg='#FF3B30')
                self.lock_button.config(
                    text="ENTSPERREN",
                    bg='#FF3B30',
                    activebackground='#D70015',
                    fg='#000000',
                    activeforeground='#000000'
                )
                # Minimiere Fenster
                self.root.iconify()
                # Starte Überwachung des Lock-Prozesses
                self.check_lock_status()

            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte nicht sperren: {e}")
        else:
            # Entsperre
            if self.check_timer:
                self.root.after_cancel(self.check_timer)
                self.check_timer = None
            if self.lock_process:
                self.lock_process.terminate()
                self.lock_process = None

            self.is_locked = False
            self.lock_label.config(text="🔒")
            self.status_label.config(text="Bereit zum Sperren", fg='#333')
            self.lock_button.config(
                text="SPERREN",
                bg='#0A84FF',
                activebackground='#0060DF',
                fg='#000000',
                activeforeground='#000000'
            )
            # Fenster wieder anzeigen
            self.root.deiconify()
            self.root.lift()
            
    def check_lock_status(self):
        """Überprüft den Status des Lock-Prozesses"""
        if self.is_locked and self.lock_process:
            # Prüfe ob Prozess noch läuft
            poll = self.lock_process.poll()
            if poll is not None:
                # Prozess beendet - wurde entsperrt mit X+C
                self.is_locked = False
                self.lock_process = None
                self.lock_label.config(text="🔒")
                self.status_label.config(text="Bereit zum Sperren", fg='#333')
                self.lock_button.config(
                    text="SPERREN",
                    bg='#0A84FF',
                    activebackground='#0060DF',
                    fg='#000000',
                    activeforeground='#000000'
                )
                # Fenster wieder anzeigen
                self.root.deiconify()
                self.root.lift()
                # Stoppe Timer
                return

        # Weiter überwachen wenn noch gesperrt
        if self.is_locked:
            self.check_timer = self.root.after(500, self.check_lock_status)

    def on_closing(self):
        """Wird beim Schließen aufgerufen"""
        if self.check_timer:
            self.root.after_cancel(self.check_timer)
        if self.lock_process:
            self.lock_process.terminate()
        self.root.destroy()
        
    def run(self):
        """Startet die App"""
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.mainloop()


def main():
    app = SimpleLockApp()
    app.run()


if __name__ == "__main__":
    main()