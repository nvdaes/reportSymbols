# -*- coding: UTF-8 -*-
# reportSymbols: Plugin to listen the typed symbols (non alphanumeric characters)
#Copyright (C) 2013-2016 Noelia Ruiz Martínez
# Released under GPL 2

import addonHandler
import globalPluginHandler
import api
import config
import speech
import wx
import gui
from gui import SettingsDialog, guiHelper
from globalCommands import SCRCAT_CONFIG

addonHandler.initTranslation()

confspec = {
	"speakTypedSymbols": "boolean(default=False)",
}
config.conf.spec["reportSymbols"] = confspec

class AddonSettingsDialog(SettingsDialog):

	# Translators: title of a dialog.
	title = _("Report Symbols settings")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label of a dialog.
		self.reportSymbolsCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("&Report symbols")))
		self.reportSymbolsCheckBox.SetValue(config.conf["reportSymbols"]["speakTypedSymbols"])

	def postInit(self):
		self.reportSymbolsCheckBox.SetFocus()

	def onOk(self,evt):
		config.conf["reportSymbols"]["speakTypedSymbols"] = self.reportSymbolsCheckBox.GetValue()
		super(AddonSettingsDialog, self).onOk(evt)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		self.settingsItem = self.prefsMenu.Append(wx.ID_ANY,
			# Translators: name of a menu item.
			_("Report &Symbols settings..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.settingsItem)

	def terminate(self):
		try:
			self.prefsMenu.RemoveItem(self.settingsItem)
		except wx.PyDeadObjectError:
			pass

	def event_typedCharacter(self, obj, nextHandler, ch):
		nextHandler()
		if not config.conf["reportSymbols"]["speakTypedSymbols"] or config.conf["keyboard"]["speakTypedCharacters"] or api.isTypingProtected() or not config.conf["keyboard"]["speechInterruptForCharacters"]:
			return
		if not ch.isalnum() and not ch.isspace() and ord(ch)>=32:
			speech.speakSpelling(ch)

	def onSettings(self, evt):
		gui.mainFrame._popupSettingsDialog(AddonSettingsDialog)

	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)
	script_settings.category = SCRCAT_CONFIG
	# Translators: message presented in input mode.
	script_settings.__doc__ = _("Shows the Report Symbols settings dialog.")
