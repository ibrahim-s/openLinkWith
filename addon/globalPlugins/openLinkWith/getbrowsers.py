#this module tries to get several browsers: Chrome, Firefox, Internet explorer, Opera, SeaMonkey, and Wyzo if found on pc.

import os

possiblePaths=[
('Firefox', ('c:\\program files\\mozilla firefox\\firefox.exe', 'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')),
('Google Chrome', ('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
'C:\\Program Files\\Google\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Google\\Application\\chrome.exe')),
('Internet Explorer', ('C:\\Program Files\\Internet Explorer\\IEXPLORE.EXE', 'C:\\Program Files (x86)\\Internet Explorer\\IEXPLORE.EXE')),
('Opera', ('C:\\Program Files\\Opera\\launcher.exe', 'C:\\Program Files (x86)\\Opera\\launcher.exe')),
('Wyzo', ('C:\\Program Files\\Wyzo\\wyzo.exe', 'C:\\Program Files (x86)\\Wyzo\\wyzo.exe')),
('Seamonkey', ('C:\\Program Files\\SeaMonkey\\seamonkey.exe', 'C:\\Program Files (x86)\\SeaMonkey\\seamonkey.exe')),
]

def getBrowsers():
	""" return a list of browsers and their path
	if present in computer. """
	browsers=[]
#getting browsers in program files or Program Files (x86)
	for browser,paths in possiblePaths:
		for path in paths:
			if os.path.exists(path):
				browsers.append((browser,path))
				break
	return browsers
