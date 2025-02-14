'''Info Header Start
Name : extOlibDependancy
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2023.11880
Info Header End'''

import pathlib
import subprocess
import td


class extOlibDependancy:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp:COMP = ownerComp

	def _filepath(self)-> pathlib.Path:
		return pathlib.Path( 
			self.ownerComp.par.Downloaddirectory.eval(),
			self.ownerComp.par.Filename.eval() 
		)

	def _fetchRemoteData(self):
		targetmode 		= self.ownerComp.par.Target.eval()
		if targetmode 	== "Olib"		: remote = self.ownerComp.op("olib_remote")
		if targetmode 	== "Github"		: remote = self.ownerComp.op("github_remote")
		if targetmode 	== "Url"		: remote = self.ownerComp.op("url_remote")
		if targetmode 	== "Callback" 	: remote = self.ownerComp.op("callback_remote")
		if targetmode 	== "COMP"		: remote = self.ownerComp.op("comp_remote")
		return remote.ExternalData()

	def GetRemoteFilepath(self) -> pathlib.Path:
		"""Downloads the file from the selected source and returns the filepath."""
		filepath = self._filepath()
		if filepath.is_file(): return filepath
		packagedFilepath = self._getPackagedFile( filepath )
		if packagedFilepath: return packagedFilepath

		downloadURL = self._fetchRemoteData()
		if downloadURL.startwith("file://"):
			return downloadURL.removeprefix("file://")
		return self._downloadFile( 	filepath,
									downloadURL )
	
	def GetGlobalComponent(self) -> COMP:
		"""Downlaods the remote resource and places a Operator representing it with the given
		Global Shortcut in the define path.
		If the file does alreay exist and is placed, it just returns the operator."""
		globalOPShortcut = self.ownerComp.par.Globalopshortcut.eval()
		return getattr( op, globalOPShortcut, None ) or self._downloadAndPlace()

	def _downloadAndPlace(self) -> COMP:
		targetTox = self.GetRemoteFilepath()
		if not targetTox: return None

		newComp 					= self._getTargetAndPlace().loadTox( targetTox )
		newComp.par.opshortcut.val  = self.ownerComp.par.Globalopshortcut.eval()
		return newComp

	def _getTargetAndPlace(self) -> COMP:
		operator = td.root
		for path_element in self.ownerComp.par.Globallocation.eval().split("/"):
			if not path_element: continue
			operator = operator.op(path_element) or operator.create(baseCOMP, tdu.legalName(path_element))
		return operator

	def _downloadFile(self, filepath:pathlib.Path, url:str) -> pathlib.Path:
		downloadScriptDAT 	= self.ownerComp.op("downloadScript")
		downloadScript 		= pathlib.Path( f"TDImportCache/Scripts/{downloadScriptDAT.id}" )
		downloadScript.is_file() or downloadScriptDAT.save(downloadScript, createFolders = True)
		executable = app.pythonExecutable
		if subprocess.call( 
			[ executable, downloadScript, url, filepath]
			) :
			raise Exception( "Error on Download! Try again. Enable TOUCH_TEXT_CONSOLE to read info of subprocess.")
		return filepath
	
	def Package(self):
		self.ownerComp.vfs.addFile(
			self.GetRemoteFilepath(), overrideName = self.GetRemoteFilepath().name
		)
		self.ownerComp.cook( force= True)
	
	def Unpackage(self):
		try:
			self.ownerComp.vfs[self.GetRemoteFilepath().name].destroy()
			self.ownerComp.cook( force=True)
		except tdAttributeError:
			pass

	def _getPackagedFile(self, filepath:pathlib.Path):
		try:
			self.ownerComp.vfs[filepath.name].export( filepath.parent )
			return filepath
		except tdAttributeError:
			pass
		return None
	
	@property
	def PackageVFS(self):
		try:
			return self.ownerComp.vfs[self._filepath().name]
		except tdAttributeError:
			return None