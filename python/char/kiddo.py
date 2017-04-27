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

def kiddoPuppet():
	puppet('kiddo_v001', character='kiddo')


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
	pm.parent('mainJA_JNT', bodyModule.skeleton)

	main = rig_control(name='main', shape='box',
	                   targetOffset='mainJA_JNT', constrain='mainJA_JNT',
	                   parentOffset=bodyModule.controls,
	                   scale=(45,10,50), colour='white' )

	main.gimbal = createCtrlGimbal(main)
	main.pivot = createCtrlPivot(main, overrideScale=(10,10,10))

	upperBody = rig_control(name='upperBody', shape='box', modify=1,
	                        targetOffset='mainJA_JNT',
	                        constrainOffset=main.con, scale=(35,15,40),
	                        colour='yellow', parentOffset=bodyModule.controls,
	                        lockHideAttrs=['tx','ty','tz'] )

	#pm.setAttr(upperBody.ctrl.rotateOrder, 2)

	constrainObject(upperBody.modify,
	                [upperBody.offset, 'worldSpace_GRP'],
	                upperBody.ctrl, ['main', 'world'], type='orientConstraint')

	pm.move(upperBody.ctrl.cv, [0, 10, 0], relative=True, objectSpace=True)

	pm.connectAttr( upperBody.ctrl.rotateX, 'upperWaistX_JA_JNT.rotateX' )
	pm.connectAttr( upperBody.ctrl.rotateY, 'upperWaistY_JA_JNT.rotateY' )
	pm.connectAttr( upperBody.ctrl.rotateZ, 'upperWaistZ_JA_JNT.rotateZ' )

	lowerBody = rig_control(name='lowerBody', shape='box', modify=1,
	                        targetOffset='lowerBodyJA_JNT',
	                        constrainOffset=main.con, scale=(40, 20, 30),
	                        colour='green',  parentOffset=bodyModule.controls,
	                        lockHideAttrs=['tx','ty','tz', 'rx','rz'] )

	constrainObject(lowerBody.modify,
	                [lowerBody.offset, 'worldSpace_GRP'],
	                lowerBody.ctrl, ['main', 'world'], type='orientConstraint',
	                skip=('x','z'))

	pm.orientConstraint(lowerBody.con, 'lowerBodyJA_JNT', skip=('x', 'z'), mo=True)

	pm.move(lowerBody.ctrl.cv, [0, -10, 0], relative=True, objectSpace=True)

	
	biped = rig_biped()
	biped.spineConnection = 'upperWaistX_JA_JNT'
	biped.pelvisConnection = 'lowerBodyJA_JNT'
	biped.centerConnection = 'mainJA_JNT'
	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=14)

		# arm setup
		#poleVector = biped.armControls['poleVector']
		#pm.move(poleVector.offset, [0, -40, 0], relative=True, objectSpace=True)

		shoulderModule = biped.shoulder(side, ctrlSize = 12)

		biped.connectArmShoulder(side)
		
		
		

def kiddoFinish():
	print 'Finishing kiddo'






