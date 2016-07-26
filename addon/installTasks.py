import addonHandler

addonHandler.initTranslation()

def onInstall():
	import gui
	import wx
	for addon in addonHandler.getAvailableAddons():
		if addon.manifest['name'] == "ReportSymbols":
			if gui.messageBox(
				# Translators: the label of a message box dialog.
				_("You have installed the ReportSymbols add-on, probably an old and incompatible version with this one. Do you want to uninstall the old version?"),
				# Translators: the title of a message box dialog.
				_("Uninstall incompatible add-on"),
				wx.YES|wx.NO|wx.ICON_WARNING)==wx.YES:
					addon.requestRemove()
			break
