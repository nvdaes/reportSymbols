# -*- coding: UTF-8 -*-

# reportSymbols: Plugin to listen the typed symbols (non alphanumeric characters)
# Copyright (C) 2013-2025 Noelia Ruiz Martínez
# Released under GPL 2

import wx
import copy

import addonHandler
import globalPluginHandler
import api
import characterProcessing
import ui
import config
import speech
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel, NVDASettingsDialog
from globalCommands import SCRCAT_CONFIG
from scriptHandler import script

addonHandler.initTranslation()

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]
ADDON_PANEL_TITLE = ADDON_SUMMARY

confspec = {
	"speakTypedSymbols": "boolean(default=False)",
	"speakTypedSpaces": "boolean(default=False)",
	"speakEnter": "boolean(default=False)",
	"speakTab": "boolean(default=False)",
	"excludedSymbols": "string_list(default=list())",
}
config.conf.spec["reportSymbols"] = confspec


class AddonSettingsPanel(SettingsPanel):
	title = ADDON_PANEL_TITLE

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

	def onSave(self):
		config.conf["reportSymbols"]["speakTypedSymbols"] = self.reportSymbolsCheckBox.GetValue()
		config.conf["reportSymbols"]["speakTypedSpaces"] = self.reportSpacesCheckBox.GetValue()
		config.conf["reportSymbols"]["speakEnter"] = self.reportEnterCheckBox.GetValue()
		config.conf["reportSymbols"]["speakTab"] = self.reportTabCheckBox.GetValue()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		NVDASettingsDialog.categoryClasses.append(AddonSettingsPanel)

	def terminate(self):
		NVDASettingsDialog.categoryClasses.remove(AddonSettingsPanel)

	def event_typedCharacter(self, obj, nextHandler, ch):
		nextHandler()
		if api.isTypingProtected():
			return
		typingEchoMode = config.conf["keyboard"]["speakTypedCharacters"]
		if (
			typingEchoMode == config.configFlags.TypingEcho.OFF.value
			or (
				typingEchoMode == config.configFlags.TypingEcho.EDIT_CONTROLS.value
				and not speech.speech.isFocusEditable()
			)
			and config.conf["keyboard"]["speechInterruptForCharacters"]
		):
			if (
				config.conf["reportSymbols"]["speakTypedSymbols"]
				and not ch.isalnum()
				and not ch.isspace()
				and ord(ch) >= 32
				and not ch in config.conf["reportSymbols"]["excludedSymbols"]
			):
				speech.speakSpelling(ch)
			elif config.conf["reportSymbols"]["speakTypedSpaces"] and ord(ch) == 32:
				speech.speakSpelling(ch)
		if not config.conf["keyboard"]["speakCommandKeys"]:
			if (
				config.conf["reportSymbols"]["speakEnter"]
				and config.conf["keyboard"]["speechInterruptForEnter"]
				and ord(ch) == 13
			):
				speech.speakSpelling(ch)
			elif config.conf["reportSymbols"]["speakTab"] and ch.isspace() and ord(ch) not in (13, 32):
				speech.speakSpelling(ch)

	def onSettings(self, evt):
		gui.mainFrame.popupSettingsDialog(NVDASettingsDialog, AddonSettingsPanel)


	@classmethod
	def __new__(cls, *args, **kwargs):
		# Iterate through the available symbols, creating scripts for them.
		for symbol in cls.getSymbols():
			cls.addScriptForSymbol(symbol)
		return super(GlobalPlugin, cls).__new__(cls)

	@classmethod
	def getSymbols(cls):
		try:
			processor = characterProcessing._localeSpeechSymbolProcessors.fetchLocaleData(
				speech.getCurrentLanguage(),
			)
		except LookupError:
			processor = characterProcessing._localeSpeechSymbolProcessors.fetchLocaleData("en")
		symbols = [copy.copy(symbol) for symbol in processor.computedSymbols.values()]
		return symbols

	@classmethod
	def _getScriptNameForSymbol(cls, symbol):
		name = symbol.replacement.replace(" ", "_")
		return "symbol_%s" % name

	@classmethod
	def _symbolScript(cls, symbol):
		if symbol.identifier not in config.conf["reportSymbols"]["excludedSymbols"]:
			config.conf["reportSymbols"]["excludedSymbols"].append(symbol.identifier)
			# Translators: Reported when a symbol has been added to excludedSymbols.
			ui.message(_("{symbol} excluded from symbols to report").format(symbol=symbol.replacement))
		else:
			config.conf["reportSymbols"]["excludedSymbols"].remove(symbol.identifier)
			# Translators: Reported when a symbol has been removed to excludedSymbols.
			ui.message(_("{symbol} included in symbols to report").format(symbol=symbol.replacement))

	@classmethod
	def addScriptForSymbol(cls, symbol):
		script = lambda self, gesture: cls._symbolScript(symbol)  # Noqa E731
		funcName = script.__name__ = "script_%s" % cls._getScriptNameForSymbol(symbol)
		setattr(cls, funcName, script)
		# Just set the doc string of the script, using the decorator is overkill here.
		# Translators: Message presented in input help mode.
		script.__doc__ = _("Excludes or includes the %s symbol in the set of signs to be reported when typing" % symbol.replacement)

	@script(
		category=SCRCAT_CONFIG,
		# Translators: message presented in input mode.
		description=_("Shows the %s settings.") % ADDON_SUMMARY,
	)
	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)
