## Changes for 3.2.9 ##

*	The addon now uses NVDA’s builtin pre_speech extension point instead of patching NVDA’s core speech function.  
*	Minimum NVDA version is now 2024.2 (since that’s when the extension point was introduced).  
*	When collecting spoken text, the addon now uses NVDA’s CHUNK_SEPARATOR, resulting cleaner and more accurate extraction of links from speech sequences.  
*	In Hyper link menu feature, the addon now recognizes links inside nested elements and graphical objects, using the same approach as NVDA core, making it capable of detecting and accessing more and more links.
*	As always credit goes to [Cary Rowen](https://github.com/cary-rowen), thanks Cary! 
