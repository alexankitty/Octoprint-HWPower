# Octoprint-HWPower
Simple python script to run as an octoprint plugin for shutting off the printer and pi on GPIO3.
# Instructions
I have no interest in making this anything proper but it's at least out here for whoever needs it.  
Base code was ~~stolen~~ borrowed from here https://the-eg.github.io/2020/12/23/octoprint-hardware-buttons.html  
Take the python script, and slap it into ~/.octoprint/plugins  
By default this assumes you want to use GPIO3 to short to ground so the same button can be used to turn the pi on as well. This code may however be portable to other systems.  