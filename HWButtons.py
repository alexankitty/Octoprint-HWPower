from __future__ import absolute_import, unicode_literals

import subprocess
import gpiozero

import octoprint.plugin
import octoprint.events

class HWButtonsPlugin(octoprint.plugin.StartupPlugin, octoprint.plugin.SettingsPlugin):
    def __init__(self):
        #super().__init__(self)
        self.power = None
        self.psu_status = None
        self.psu_on = None
        self.psu_off = None
        self.shutdown = None

    def on_after_startup(self):
        self.shutdown = self._settings.global_get(["server", "commands", "systemShutdownCommand"])
        helpers = self._plugin_manager.get_helpers("psucontrol", "get_psu_state", "turn_psu_on", "turn_psu_off")
        if helpers and "get_psu_state" in helpers and "turn_psu_on" in helpers and "turn_psu_off" in helpers:
           self.psu_status = helpers["get_psu_state"]
           self.psu_on = helpers["turn_psu_on"]
           self.psu_off = helpers["turn_psu_off"]
        else:
            self._logger.warn("PSUControl failed to load, is it installed?")
            return
        self.power = gpiozero.Button(3, pull_up=True, hold_time=5)
        self.power.when_pressed = self.on_printerPower_pressed

    def __del__(self):
        self.power.close()

    def on_printerPower_pressed(self):
        while self.power.is_pressed:
            if self.power.active_time and self.power.active_time > self.power.hold_time:
                self.on_power_held()
                return

        if self._printer.is_operational() and self._printer.is_printing() and not self._printer.is_cancelling():
            self._logger.info("Cancelling print. (Hardware button pressed)")
            self._printer.cancel_print()
        elif self.psu_status():
            self.psu_off()
            self._logger.info("Turning printer off. (Hardware button pressed)")
        else:
            self.psu_on()
            self._logger.info("Turning printer on. (Hardware button pressed)")
            
    def on_power_held(self):
        if self._printer.is_operational() and self._printer.is_printing() and not self._printer.is_cancelling():
            self._logger.info("Cancelling print. (Hardware button pressed)")
            self._printer.cancel_print()
            import time
            time.sleep(300) #Give things a chance to cool before we yank the plug
            self.psu_off()
            self._logger.info("Shutting down. (Hardware button pressed)")
            subprocess.call(self.shutdown, shell=True)
        else:
            self.psu_off()
            self._logger.info("Shutting down. (Hardware button pressed)")
            subprocess.call(self.shutdown, shell=True)

def __plugin_load__():
        global __plugin_implementation__
        __plugin_implementation__ = HWButtonsPlugin()

__plugin_name__ = "Hardware Buttons"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Actions for hardware buttons wired to RPi GPIO pins."
__plugin_pythoncompat__ = ">=2.7,<4"
