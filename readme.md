# Open Link With #

Authors: Ibrahim Hamadeh, Belala Toufik  
Contributors: cary-rowen  
NVDA compatibility: 2018.3 and beyond   
Download [Version 2.6][1]  

This addon is used to extract links either from selected text or from clipboard text or from last spoken text
display them in a list in a dialog  
and give you the opportunity to open them with several browsers if found on your pc.

## Usage

*	First you have to assign a gestures for the addon through input gestures dialog.  
*	You can do that going to NVDA Menu/Preferences/Input Gestures/Openlink with category.  
*	There are three unassigned gestures there.  
	1.	A gesture to display links under selected text.  
	2.	A gesture to display link in clipboard text.  
	3.	A gesture to display link in last spoken text.  
*	Now you have the option to get and display links, either from selected text or from text in clipboard or from text in last spoken.  
*	then press the shortcut of the addon, as you have chosen it  
*	if present, links will be displayed in a listbox in a dialog  
*	Choose the link, and press enter if you want to open it with the default browser.  
*	otherwise, tab to the browser you want to open it with, and hit enter.  
*	If there is only one link, use the default browser to open it directly, of course this behavior is controlled by options in the settings panel.
*	Remember that you got the obtion to close the dialog, after activating a link  
and you can adjust that from openLinkWith settings dialog in preferences menu.  

## Changes for 2.6 ##

*	Add Turkish translation for the addon.
*	Now, You can extract the links from the text in last spoken.
*	You can use the options in the settings panel to decide whether to open it directly with the default browser when there is only one link

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

[1]: https://github.com/ibrahim-s/openLinkWith/releases/download/v2.6/openLinkWith-2.6.nvda-addon
