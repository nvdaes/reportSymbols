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
	"speakTypedSpaces": "boolean(default=False)",
	"speakEnter": "boolean(default=False)",
	"speakTab": "boolean(default=False)",
}
config.conf.spec["reportSymbols"] = confspec

class AddonSettingsDialog(SettingsDialog):

	# Translators: title of a dialog.
	title = _("Report Symbols settings")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label of a dialog.
		self.reportSymbolsCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Report &printable symbols")))
		self.reportSymbolsCheckBox.SetValue(config.conf["reportSymbols"]["speakTypedSymbols"])

		# Translators: label of a dialog.
		self.reportSpacesCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Report &spaces")))
		self.reportSpacesCheckBox.SetValue(config.conf["reportSymbols"]["speakTypedSpaces"])

		# Translators: label of a dialog.
		self.reportEnterCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("&Report carriage returns")))
		self.reportEnterCheckBox.SetValue(config.conf["reportSymbols"]["speakEnter"])

		# Translators: label of a dialog.
		self.reportTabCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Repor&t other blank characters")))
		self.reportTabCheckBox.SetValue(config.conf["reportSymbols"]["speakTab"])

	def postInit(self):
		self.reportSymbolsCheckBox.SetFocus()

	def onOk(self,evt):
		config.conf["reportSymbols"]["speakTypedSymbols"] = self.reportSymbolsCheckBox.GetValue()
		config.conf["reportSymbols"]["speakTypedSpaces"] = self.reportSpacesCheckBox.GetValue()
		config.conf["reportSymbols"]["speakEnter"] = self.reportEnterCheckBox.GetValue()
		config.conf["reportSymbols"]["speakTab"] = self.reportTabCheckBox.GetValue()
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
		if api.isTypingProtected():
			return
		if not config.conf["keyboard"]["speakTypedCharacters"] and config.conf["keyboard"]["speechInterruptForCharacters"]:
			if config.conf["reportSymbols"]["speakTypedSymbols"] and not ch.isalnum() and not ch.isspace() and ord(ch)>=32:
				speech.speakSpelling(ch)
			elif config.conf["reportSymbols"]["speakTypedSpaces"] and ord(ch) == 32:
				speech.speakSpelling(ch)
		if not config.conf["keyboard"]["speakCommandKeys"]:
			if config.conf["reportSymbols"]["speakEnter"] and config.conf["keyboard"]["speechInterruptForEnter"] and ord(ch) == 13:
				speech.speakSpelling(ch)
			elif config.conf["reportSymbols"]["speakTab"] and ch.isspace() and ord (ch) not in (13, 32):
				speech.speakSpelling(ch)

	def onSettings(self, evt):
		gui.mainFrame._popupSettingsDialog(AddonSettingsDialog)

	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)
	script_settings.category = SCRCAT_CONFIG
	# Translators: message presented in input mode.
	script_settings.__doc__ = _("Shows the Report Symbols settings dialog.")
