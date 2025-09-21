#!/usr/bin/env python3
"""
macOS Tastatur und Touchpad Sperre
Sperrt alle Eingaben bis die Tastenkombination "xy" gedrückt wird
"""

import Quartz
import time
import threading
import subprocess
import sys
import os


class InputLocker:
	def __init__(self):
		self.locked = True
		self.x_pressed = False
		self.c_pressed = False
		self.unlock_thread = None

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
				self.locked = False
				# Beende nach kurzer Verzögerung - GUI wartet auf uns
				if not self.unlock_thread:
					self.unlock_thread = threading.Timer(0.2, self.stop_app)
					self.unlock_thread.start()
				return event

		# Alle Events blockieren wenn gesperrt
		return None

	def stop_app(self):
		"""Beendet die Anwendung"""
		Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())

	def run(self):
		"""Startet die Event-Überwachung"""

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
		tap = Quartz.CGEventTapCreate(
			Quartz.kCGSessionEventTap,
			Quartz.kCGHeadInsertEventTap,
			Quartz.kCGEventTapOptionDefault,
			event_mask,
			self.event_callback,
			None
		)

		if not tap:
			print("❌ Fehler: Konnte Event Tap nicht erstellen!")
			print("💡 Tipp: Erlaube Terminal/Python in Systemeinstellungen > ")
			print("   Sicherheit & Datenschutz > Datenschutz > Bedienungshilfen")
			sys.exit(1)

		# Event Tap zum Run Loop hinzufügen
		run_loop_source = Quartz.CFMachPortCreateRunLoopSource(
			Quartz.kCFAllocatorDefault, tap, 0
		)
		Quartz.CFRunLoopAddSource(
			Quartz.CFRunLoopGetCurrent(),
			run_loop_source,
			Quartz.kCFRunLoopCommonModes
		)

		# Event Tap aktivieren
		Quartz.CGEventTapEnable(tap, True)

		# Run Loop starten
		Quartz.CFRunLoopRun()


def main():
	# Locker starten
	locker = InputLocker()
	try:
		locker.run()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		pass


if __name__ == "__main__":
	main()