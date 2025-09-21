#!/usr/bin/env python3
"""
macOS Lock GUI - Sicherheits-App mit grafischer Oberfläche
"""

import tkinter as tk
from tkinter import ttk, messagebox
import Quartz
import threading
import subprocess
import sys
import os


class InputLocker:
    def __init__(self, app_callback=None):
        self.locked = False
        self.x_pressed = False
        self.c_pressed = False
        self.unlock_thread = None
        self.tap = None
        self.run_loop_source = None
        self.lock_thread = None
        self.app_callback = app_callback
        
    def event_callback(self, proxy, event_type, event, refcon):
        """Fängt alle Tastatur- und Maus-Events ab"""
        
        # Wenn entsperrt, alle Events durchlassen
        if not self.locked:
            return event
            
        # Tastendruck-Events prüfen
        if event_type in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp]:
            keycode = Quartz.CGEventGetIntegerValueField(
                event, Quartz.kCGKeyboardEventKeycode
            )
            
            # Keycodes: X=7, C=8
            if event_type == Quartz.kCGEventKeyDown:
                if keycode == 7:  # X
                    self.x_pressed = True
                elif keycode == 8:  # C
                    self.c_pressed = True
                    
            elif event_type == Quartz.kCGEventKeyUp:
                if keycode == 7:  # X
                    self.x_pressed = False
                elif keycode == 8:  # C
                    self.c_pressed = False
            
            # Entsperren wenn beide Tasten gedrückt
            if self.x_pressed and self.c_pressed:
                self.unlock()
                return event
                
        # Alle Events blockieren wenn gesperrt
        return None
        
    def lock(self):
        """Aktiviert die Sperre"""
        self.locked = True
        self.x_pressed = False
        self.c_pressed = False
        
        # Event-Maske für alle relevanten Events
        event_mask = (
            (1 << Quartz.kCGEventKeyDown) |
            (1 << Quartz.kCGEventKeyUp) |
            (1 << Quartz.kCGEventLeftMouseDown) |
            (1 << Quartz.kCGEventLeftMouseUp) |
            (1 << Quartz.kCGEventRightMouseDown) |
            (1 << Quartz.kCGEventRightMouseUp) |
            (1 << Quartz.kCGEventMouseMoved) |
            (1 << Quartz.kCGEventLeftMouseDragged) |
            (1 << Quartz.kCGEventRightMouseDragged) |
            (1 << Quartz.kCGEventScrollWheel) |
            (1 << Quartz.kCGEventOtherMouseDown) |
            (1 << Quartz.kCGEventOtherMouseUp)
        )
        
        # Event Tap erstellen
        self.tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            event_mask,
            self.event_callback,
            None
        )
        
        if not self.tap:
            return False
            
        # Event Tap zum Run Loop hinzufügen
        self.run_loop_source = Quartz.CFMachPortCreateRunLoopSource(
            Quartz.kCFAllocatorDefault, self.tap, 0
        )
        
        # Run Loop in separatem Thread starten
        self.lock_thread = threading.Thread(target=self._run_loop)
        self.lock_thread.daemon = True
        self.lock_thread.start()
        
        return True
        
    def _run_loop(self):
        """Führt den Event Loop aus"""
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            self.run_loop_source,
            Quartz.kCFRunLoopCommonModes
        )
        
        # Event Tap aktivieren
        Quartz.CGEventTapEnable(self.tap, True)
        
        # Run Loop starten
        Quartz.CFRunLoopRun()
        
    def unlock(self):
        """Deaktiviert die Sperre"""
        self.locked = False
        if self.tap:
            Quartz.CGEventTapEnable(self.tap, False)
            Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())
        # Callback zur App, um sie zu schließen - in separatem Thread
        if self.app_callback:
            threading.Thread(target=self.app_callback, daemon=True).start()


class LockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("macOS Lock")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        
        # System Style
        self.root.configure(bg='#f0f0f0')
        
        # Locker Instance mit Callback zum Schließen
        self.locker = InputLocker(app_callback=self.close_app)
        self.is_locked = False
        self.should_close = False
        
        # UI erstellen
        self.setup_ui()
        
        # Window Events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#f0f0f0')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Icon (Lock Symbol)
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
        
        # Main Button
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
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
            # Prüfe Berechtigung
            if not self.check_accessibility():
                self.show_accessibility_dialog()
                return
                
            # Aktiviere Sperre
            if self.locker.lock():
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
        else:
            # Entsperre
            self.locker.unlock()
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
            
    def check_accessibility(self):
        """Prüft ob Bedienungshilfen-Berechtigung vorhanden ist"""
        # Erstelle Test Event Tap
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            (1 << Quartz.kCGEventKeyDown),
            lambda p, t, e, r: e,
            None
        )
        
        if tap:
            Quartz.CFRelease(tap)
            return True
        return False
        
    def show_accessibility_dialog(self):
        """Zeigt Dialog für Bedienungshilfen-Berechtigung"""
        result = messagebox.askyesno(
            "Berechtigung erforderlich",
            "Diese App benötigt Zugriff auf die Bedienungshilfen.\n\n"
            "Möchten Sie die Systemeinstellungen öffnen?\n\n"
            "Fügen Sie dort diese App hinzu und aktivieren Sie den Schalter.",
            icon='warning'
        )
        
        if result:
            # Öffne Systemeinstellungen
            subprocess.run([
                'open',
                'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
            ])
            
    def on_closing(self):
        """Wird beim Schließen des Fensters aufgerufen"""
        if self.is_locked:
            # Entsperre vor dem Beenden
            self.locker.unlock()
        self.root.destroy()
    
    def close_app(self):
        """Wird aufgerufen wenn über X+C entsperrt wird"""
        print("close_app() aufgerufen - update GUI")
        self.is_locked = False
        # Update GUI im Main Thread
        self.root.after(10, self.update_gui_after_unlock)

    def update_gui_after_unlock(self):
        """Updated die GUI nach dem Entsperren mit X+C"""
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

    def check_close_flag(self):
        """Wird nicht mehr verwendet"""
        pass
        
    def run(self):
        """Startet die App"""
        # Bringe Fenster in den Vordergrund
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # Starte Event Loop
        self.root.mainloop()


def main():
    app = LockApp()
    app.run()


if __name__ == "__main__":
    main()