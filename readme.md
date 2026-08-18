# Open Link With #

Authors: Ibrahim Hamadeh, Cary Rowen, Belala Toufik  
NVDA compatibility: 2024.2 and beyond   
Download [Stable version 3.3.0][1]  

This addon is used to extract links either from selected, clipboard, or last spoken text  
display them in a list in a dialog  
and give you the opportunity to open them with several browsers if found on your pc.

## Usage

*	First you have to assign a gestures for the addon through input gestures dialog.  
*	You can do that going to NVDA Menu/Preferences/Input Gestures/Openlink with category.  
*	There are three unassigned gestures there.  
	1.	A gesture to display links under selected text.  
	2.	A gesture to display link in clipboard text.  
	3.	A gesture to display link in last spoken text.  
*	Thus assigning a gesture, you have the option to get and display links, either from selected , clipboard or last spoken text.  
*	then press the shortcut of the addon, as you have chosen it  
*	if present, links will be displayed in a listbox in a dialog  
*	Choose the link, and press enter if you want to open it with the default browser.  
*	otherwise, tab to the browser you want to open it with, and hit enter.  
*	If there is only one link, you can choose to be opened  directly with the default browser. this obtion can be adjusted in the settings panel.
*	In the settings panel also, remember that you got the obtion to close the dialog, after activating a link.  

## Hyper link menu

Suppose you are in one browser and found a link, you like to open it with another browser.

or you are reading a message and in it a link, you wish to open it with a specific browser(not the default), what to do in this case?

Here comes the beautiful hyper link menu feature, press the gesture of hyper link menu(Alt+/), a menu will pop up giving you the option to open the link with several browsers on your machine.

Lot of times, while reading a message encounter a link to github, the browser I am logged in with it in github is Chrome, while my default browser is Firefox, and I need to open the link with Chrome to react with the issue of the link. Hyper link menu can help me now to go to github with the browser I am already logged in with it, even if it is not the default one.

Alt+/ is the default gesture, but you can always change it through NVDA menu/Preferences/Input gestures/Open link with.

## Announce and copy web page address

If on a web page, and would like to know the page address,  press the shortcut once, and if you would like to copy the address to clipboard, just press it twice.

This feature does not have an assign shortcut, so you should assign to it a shortcut by yourself, going to:

NVDA menu/Preferences/Input gestures/Open link with/Announce address or link of a web page if pressed once, and copies it to clipboard when pressed twice.

## Changes for 3.3.0 ##

*	Add a new feature, that announces a web page address, if the shortcut pressed once, and copies it to clipboard if pressed twice.

## Changes for 3.2.9 ##

*	The addon now uses NVDA’s builtin pre_speech extension point instead of patching NVDA’s core speech function.  
*	Minimum NVDA version is now 2024.2 (since that’s when the extension point was introduced).  
*	When collecting spoken text, the addon now uses NVDA’s CHUNK_SEPARATOR, resulting cleaner and more accurate extraction of links from speech sequences.  
*	In Hyper link menu feature, the addon now recognizes links inside nested elements and graphical objects, using the same approach as NVDA core, making it capable of detecting and accessing more and more links.
*	As always credit goes to [Cary Rowen](https://github.com/cary-rowen), thanks Cary! 

## Changes for 3.2.7 ##

*	Added new urlutility.py module for robust link parsing and validation.
*	Improved link extraction and checking across all parts of a URL — earlier there were problems with results, which should now be fixed.
*	Added a full set of unit tests in tests/unit/test_urlUtils.py to ensure reliability.
*	All credit for this goes to [Cary Rowen](https://github.com/cary-rowen). Thank you, Cary!

## Changes for 3.2.5 ##

*	Update minimum tested version to 2021.1, and remove versionInfo related code.
*	Update addon template files.

## Changes for 3.2.4 ##

*	Update last tested version, thus making the addon compatible with NVDA 2025.1 release.

## Changes for 3.2.3 ##

*	Add the option for opening the link in private mode, for Firefox, Chrome and Microsoft Edge if found in your computer. You can reach to them in Open link with menu.
*	In webbrowser.open function add new=2 argument, so that the link will Open in a new tab in the foreground.

## Changes for 3.2.1 ##

*	Add Russian localization and documentation, contributed by Kostenkov.

## Changes for 3.2 ##

*	Update last tested version, so the addon now is compatible with NVDA 2024.1.

## Changes for 3.1 ##

*	Enhance hyper link menu code, so now more links can be access and opened by this menu.

## Changes for 3.0 ##

*	Fix the issue of gui.SettingsPanel, and get rid of warning messages in the log.
*	Use github actions instead of apveyor to build the addon.

## Changes for 2.9 ##

*	Add hyper link menu feature, to give you the option to open the link with other browsers.
*	Stand on a link, and press the gesture Alt+/
*	A menu will pop up, giving you the option to open the link with other browsers on your machine.
*	You can press escape to dismiss the menu, or enter on any of the browser to open the link right with it.

## Changes for 2.8 ##
*	Updated add-on template.
*	Update last tested version to 2023.1, to comply with latest addon api.

## Changes for 2.7 ##

*	Now, You can extract the links from the text in last spoken.
*	You can use the options in the settings panel to decide whether to open it directly with the default browser when there is only one link in text.
*	Remove duplicates after extracting URL

## Changes for 2.6 ##

*	Add Turkish translation for the addon.

## Changes for 2.5 ##

*	Disable the addon in secure mode
*	Update last tested version to 2022.1, to comply with latest addon api.

## Changes for 2.4 ##

*	Now you have two unassigned gestures for the addon.  
*	One to display links under selected text, and the other to display links in clipboard text.   
*	Use latest addon template files  
*	Update manifest.ini for minimum and last version tested.  

## Changes for 2.2 ##
*	Ensures compatibility with python3.  

## Changes for 2.0 ##

*	Now we access the standard browsers from the registry, and not from C drive.
*	Added a configuration settings dialog for the addon in preferences menu  
So that we have the obtion to close the dialog after activating a link.
*	Added Edge browser to browsers available if in windows10.
*	Added settings panel to  fit  with NVDA2018.2 or later.

## Changes for 1.0 ##

*	Initial version.

[1]: https://github.com/ibrahim-s/openLinkWith/releases/download/3.3.0/openLinkWith-3.3.0.nvda-addon
