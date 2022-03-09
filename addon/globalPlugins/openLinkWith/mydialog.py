#graphical user interface for the dialog to be displayed, containing a listbox for the links and buttons for several browsers.

import wx
import config
import os 
import webbrowser 
import subprocess 
from .getbrowsers import getBrowsers
import addonHandler
addonHandler.initTranslation()

class MyDialog(wx.Dialog):

	def __init__(self, parent, links, browsers):
		super(MyDialog, self).__init__(parent, title = _('Open Link With'))
		self.links= links
		panel = wx.Panel(self, -1)
		self.listBox = wx.ListBox(panel, -1)
		listBoxSizer =  wx.BoxSizer(wx.VERTICAL)
		listBoxSizer.Add(self.listBox, 1, wx.ALL, 5)
		buttonSizer = wx.BoxSizer(wx.VERTICAL)
		staticText = wx.StaticText(panel, -1, _('Open With'))
		buttonSizer.Add(staticText, 0, wx.EXPAND|wx.ALL, 10)
		#As for browsers taken from the registry, to dynamically  create each button and its function using lambda .
		for browser,path in browsers:
		#browsers is a list of tuples, each tuple consists of the browser name and it's path.
			btn = wx.Button(panel, -1, label = browser)
			btn.Bind(wx.EVT_BUTTON, lambda evt, temp=path: self.onOpen(evt, temp))
			buttonSizer.Add(btn, 1, wx.ALL, 10)
		self.ok= wx.Button(panel, wx.ID_OK)
		self.ok.SetDefault()
		self.ok.Bind(wx.EVT_BUTTON, self.onOk)
		buttonSizer.Add(self.ok, 1, wx.EXPAND|wx.ALL, 10)
		self.cancel = wx.Button(panel, wx.ID_CANCEL)
		self.cancel.Bind(wx.EVT_BUTTON, self.onCancel)
		buttonSizer.Add(self.cancel, 1, wx.EXPAND|wx.ALL, 10)
		mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		mainSizer.Add(listBoxSizer, 1, wx.EXPAND|wx.ALL, 10)
		mainSizer.Add(buttonSizer, 1, wx.EXPAND|wx.ALL, 10)
		panel.SetSizer(mainSizer)

	def postInit(self):
		self.listBox.Set(self.links)
		self.listBox.SetSelection(0)
		self.Centre()
		self.Raise()
		self.Show()
 
	def checkCloseAfterActivatingLink(self):
		if config.conf["openLinkWith"]["closeDialogAfterActivatingALink"]== True:
			wx.CallLater(4000, self.Destroy)

	def onOpen(self, evt, exe_path):
		url= self.getUrl()
		if url:
			subprocess.Popen(exe_path+' '+url)
			self.checkCloseAfterActivatingLink()

	def getUrl(self):
		i = self.listBox.GetSelection()
		if i!= -1:
			url= self.listBox.GetStringSelection()
			return url

	def onCancel (self, e):
		self.Destroy()

	def onOk(self, e):
		url= self.getUrl()
		if url:
			webbrowser.open(url)
			self.checkCloseAfterActivatingLink()
