#!/usr/bin/env python3
"""
Hilfsskript zum vollständigen Beenden der macOS Lock App
"""

import subprocess
import sys
import os
import time

def force_quit_macos_lock():
    """Beendet die macOS Lock App vollständig"""
    
    methods = [
        # 1. Kill alle macos-lock Prozesse (schnellste Methode)
        ['pkill', '-9', '-f', 'macos-lock'],
        
        # 2. Kill Python-Prozesse mit App-Bundle Pfad  
        ['pkill', '-9', '-f', 'macOS Lock.app'],
        
        # 3. AppleScript force quit
        ['osascript', '-e', '''
        tell application "System Events"
            try
                set appProcess to first process whose name is "macOS Lock"
                tell appProcess to quit
            end try
        end tell
        '''],
        
        # 4. Dock Application Manager
        ['osascript', '-e', '''
        tell application "System Events"
            try
                tell dock preferences to quit application "macOS Lock"
            end try
        end tell
        '''],
        
        # 5. GUI Scripting Force Quit
        ['osascript', '-e', '''
        tell application "System Events"
            try
                key down command
                key down option  
                keystroke "esc"
                key up option
                key up command
                delay 0.5
                if exists (window "Force Quit Applications") then
                    tell window "Force Quit Applications"
                        try
                            select (first row of table 1 whose value of static text 1 contains "macOS Lock")
                            click button "Force Quit"
                        end try
                    end tell
                end if
            end try
        end tell
        '''],
        
        # 6. Direkter Prozess-Kill über PID
        ['sh', '-c', 'ps aux | grep "macOS Lock.app" | grep -v grep | awk \'{print $2}\' | xargs kill -9'],
    ]
    
    for i, method in enumerate(methods):
        try:
            print(f"Methode {i+1}: {' '.join(method[:3])}...")
            result = subprocess.run(method, capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                print(f"  → Erfolgreich")
            else:
                print(f"  → Return code: {result.returncode}")
            time.sleep(0.2)  # Kürzere Wartezeit
        except Exception as e:
            print(f"  → Fehler: {e}")
    
    # Final cleanup - nochmal alle Python-Prozesse mit macOS Lock killen
    try:
        subprocess.run(['pkill', '-9', '-f', 'macOS Lock'], check=False)
        subprocess.run(['pkill', '-9', '-f', 'macos-lock'], check=False)
    except:
        pass
    
    print("Aggressive force quit abgeschlossen")

if __name__ == "__main__":
    force_quit_macos_lock()