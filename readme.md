# Open Link With #

Authors: Ibrahim Hamadeh, Cary Rowen, Belala Toufik  
NVDA compatibility: 2019.1 and beyond   
Download [Stable version 3.2.1][1]  

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

[1]: https://github.com/ibrahim-s/openLinkWith/releases/download/3.2.1/openLinkWith-3.2.1.nvda-addon
