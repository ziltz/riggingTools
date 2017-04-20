__author__ = 'Jerry'




import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm

from rig_puppet import puppet

'''

import char.kiddo as char
reload(char)
char.kiddoPuppet()

'''

def kiddoPrepareRig():
	print 'Prepare kiddo'

def kiddoRigModules():
	print 'Create kiddo rig modules'

def kiddoFinish():
	print 'Finishing kiddo'

def kiddoPuppet():
	puppet('kiddo_v001', character='kiddo')
