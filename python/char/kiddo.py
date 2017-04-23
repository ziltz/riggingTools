__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm

from create.rig_puppet import puppet
from create.rig_biped import rig_biped
from rutils.rig_modules import rig_module
from make.rig_controls import *


'''

import char.kiddo as char
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
	
	main = rig_control(name='main', shape='box',
	                   targetOffset='mainJA_JNT', constrain='mainJA_JNT',
	                   parentOffset='rigModule_GRP',
	                   scale=(45,40,50), colour='white' )

	main.gimbal = createCtrlGimbal(main)
	main.pivot = createCtrlPivot(main)

	upperBody = rig_control(name='upperBody', shape='box',
	                        targetOffset='upperWaistX_JA_JNT',
	                        constrainOffset=main.con, scale=(35,15,40),
	                        colour='yellow', parentOffset=bodyModule.controls,
	                        lockHideAttrs=['tx','ty','tz']  )

	pm.move(upperBody.ctrl.cv, [0, 5, 0], relative=True, objectSpace=True)

	pm.orientConstraint( upperBody.con, 'upperWaistX_JA_JNT', skip=('y','z'),
	                     mo=True )
	pm.orientConstraint( upperBody.con, 'upperWaistY_JA_JNT', skip=('x','z'), mo=True )
	pm.orientConstraint( upperBody.con, 'upperWaistZ_JA_JNT', skip=('y','x'), mo=True )

	lowerBody = rig_control(name='lowerBody', shape='box',
	                        targetOffset='lowerBodyJA_JNT',
	                        constrainOffset=main.con, scale=(40, 20, 30),
	                        colour='green',  parentOffset=bodyModule.controls,
	                        lockHideAttrs=['tx','ty','tz', 'rx','rz'] )

	pm.orientConstraint(lowerBody.con, 'lowerBodyJA_JNT', skip=('x', 'z'), mo=True)

	pm.move(lowerBody.ctrl.cv, [0, -10, 0], relative=True, objectSpace=True)

	
	biped = rig_biped()
	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=14)

		shoulderModule = biped.shoulder(side, ctrlSize = 12)
		shoulderCtrl = biped.shoulderControl

		pm.parentConstraint( upperBody.con, shoulderCtrl.offset , mo=True )


def kiddoFinish():
	print 'Finishing kiddo'

def kiddoPuppet():
	puppet('kiddo_v001', character='kiddo')
