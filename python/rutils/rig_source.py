__author__ = 'Jerry'

import glob, os, platform, math, importlib, sys

import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm



def rig_utilsOpenMayaPort():
	# mc.commandPort( name=":7002", close=True )
	mc.commandPort(name=":7002", sourceType="mel")



def rig_sourceAll( riggingDir='C:/dev/riggingTools/' ):
	print("Sourcing all rig files")
	
	devPath = riggingDir+'python/'
	if platform.system() == 'Darwin':
		riggingDir = '/Users/Jerry/Documents/dev/riggingTools/'
		devPath = riggingDir +'python/'

	if devPath not in sys.path:
		sys.path.append(devPath)
	if riggingDir not in sys.path:
		sys.path.append(riggingDir)
	
	for root, dirs, files in os.walk(devPath):
		for d in dirs:
			folderPath = devPath + d
			if folderPath not in sys.path:
				print folderPath
				sys.path.append(folderPath)

	rig_sourceMelFiles()
	rig_sourcePythonFiles()


def rig_sourceMelFiles(dir='C:/dev/riggingTools/mel/', ext='*.mel'):
	print("Sourcing all mel files")
	if platform.system() == 'Darwin':
		dir = '/Users/Jerry/Documents/dev/riggingTools/mel/'
	os.chdir(dir)
	for file in glob.glob(ext):
		print( "- " + file +" ....")
		mm.eval( 'source "' + dir + file +'";')


def rig_sourcePythonFiles(dir='C:/dev/riggingTools/python/', ext='*.py'):
	print("Sourcing all python files")
	if platform.system() == 'Darwin':
		dir = '/Users/Jerry/Documents/dev/riggingTools/python/'
	
	print 'Using directory = '+ dir
	for root, dirs, files in os.walk(dir):
		currentDir = root.replace(dir, '')
		if dirs is not 'other':
			for file in files:
				if file is not 'rig_source.py':
					if file.endswith(".py"):
						path = currentDir + '.' + file[:-3]
						if not currentDir:
							path = file[:-3]
						if file[:-3] not in '__init__':
							mod = importlib.import_module(path, package='riggingTools.python')
							print path
							reload(mod)
							
						
						
						
						
						