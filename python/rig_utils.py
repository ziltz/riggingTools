__author__ = 'Jerry'

import glob, os, platform

import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm


def rig_utilsOpenMayaPort():
	#mc.commandPort( name=":7002", close=True )
	mc.commandPort(name=":7002", sourceType="mel")




def rig_sourceMelFiles(dir='C:/dev/riggingTools/mel/', ext='*.mel'):
	if platform.system() == 'Darwin':
		dir = '/Users/Jerry/Documents/dev/riggingTools/mel/'
	os.chdir(dir)
	for file in glob.glob(ext):
		print("Sourcing "+file+" ....")
		mm.eval('source "'+dir+file+'";')

