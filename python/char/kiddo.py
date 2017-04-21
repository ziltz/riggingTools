__author__ = 'Jerry'




import pymel.core as pm
import maya.cmds as mc
import maya.mel as mm

from rig_puppet import puppet
from rig_biped import rig_biped
from rig_modules import rig_module
from rig_controls import rig_control

'''

import char.kiddo as char
reload(char)
char.kiddoPuppet()

'''

def kiddoPrepareRig():
	print 'Prepare kiddo'

	mc.parent('l_clavicleJA_JNT', w=True)
	mc.parent('r_clavicleJA_JNT', w=True)
	mc.parent('l_armJA_JNT', w=True)
	mc.parent('r_armJA_JNT', w=True)
	
	mc.parent( 'l_legJA_JNT', w=True )
	mc.parent( 'r_legJA_JNT', w=True )
	

def kiddoRigModules():
	print 'Create kiddo rig modules'
	
	bodyModule = rig_module('body')
	
	main = rig_control(name='main', shape='box', gimbal=1, targetOffset='mainJA_JNT' )
	
	upperBody = rig_control(name='upperBody', shape='box' )
	
	#upperWaistY_JA_JNT
	
	#lowerBodyJA_JNT
	
	biped = rig_biped()
	l_arm = biped.arm('l')
	r_arm = biped.arm('r')
	


def kiddoFinish():
	print 'Finishing kiddo'

def kiddoPuppet():
	puppet('kiddo_v001', character='kiddo')
