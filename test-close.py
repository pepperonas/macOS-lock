#!/usr/bin/env python3
"""
Test für Auto-Close Funktionalität
"""

import tkinter as tk
import threading
import time
import sys
import os

class TestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Auto Close")
        self.root.geometry("300x200")
        
        # Test Button
        btn = tk.Button(
            self.root,
            text="Starte 3s Timer",
            command=self.start_timer,
            font=('Arial', 14)
        )
        btn.pack(pady=50)
        
        self.status = tk.Label(self.root, text="Bereit")
        self.status.pack()
        
    def start_timer(self):
        """Startet Timer der nach 3s die App schließt"""
        self.status.config(text="Timer läuft...")
        threading.Thread(target=self.timer_thread, daemon=True).start()
        
    def timer_thread(self):
        """Timer Thread"""
        time.sleep(3)
        print("Timer abgelaufen - schließe App")
        # Thread-sichere Schließung
        self.root.after(0, self.close_app)
        
    def close_app(self):
        """Schließt die App"""
        print("Schließe App...")
        try:
            self.root.quit()
            self.root.destroy()
            sys.exit(0)
        except:
            os._exit(0)
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()