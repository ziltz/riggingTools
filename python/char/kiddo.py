__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import rig_biped
from rutils.rig_modules import rig_module
from make.rig_controls import *
from rutils.rig_utils import *


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
	
	#mc.parent( 'l_legJA_JNT', w=True )
	#mc.parent( 'r_legJA_JNT', w=True )
	

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

		shoulderModule = biped.shoulder(side, ctrlSize = 12)

		biped.connectArmShoulder(side)
		
		
		


		# make leg
		legName = side+'_leg'
		legModule = rig_module(legName)

		hipZJnt = side+'_hipZ_JA_JNT'
		hipYJnt = side+'_hipY_JA_JNT'

		legJnt = side+'_legJA_JNT'
		kneeJnt = side+'_kneeJA_JNT'
		ankleJnt = side+'_ankleJA_JNT'
		footJnt = side+'_footJA_JNT'

		pm.setAttr( hipYJnt+'.rotateOrder', 2 )

		# chain IK
		legJntIK = rig_transform(0, name=side + '_legIK', type='joint', target=legJnt,
		                      parent=legModule.parts).object
		kneeJntIK = rig_transform(0, name=side + '_kneeIK', type='joint',
		                        target=kneeJnt).object
		ankleJntIK = rig_transform(0, name=side + '_ankleIK', type='joint',
		                         target=ankleJnt,).object
		footJntIK = rig_transform(0, name=side + '_footIK', type='joint',
		                           target=footJnt, ).object
		chainIK = [legJntIK, kneeJntIK, ankleJntIK, footJntIK]

		chainParent(chainIK)
		chainIK.reverse()

		# create ik
		ik = rig_ik(legName, legJntIK, footJntIK, 'ikSpringSolver')
		pm.parent(ik.handle, module.parts)

		# pole vector
		legPoleVector = rig_control(side=side, name='legPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx', 'ry', 'rz'],
		                         targetOffset=[legJnt, footJnt],
		                         parentOffset=legModule.controls, scale=(4,4,4))

		pm.parentConstraint(biped.centerConnection, legPoleVector.offset, mo=True)
		pm.delete(pm.aimConstraint(kneeJnt, legPoleVector.offset, mo=False))

		kneePos = pm.xform(kneeJnt, translation=True, query=True, ws=True)
		poleVectorPos = pm.xform(legPoleVector.con, translation=True, query=True,
		                         ws=True)

		pvDistance = lengthVector(kneePos, poleVectorPos)

		pm.xform(legPoleVector.offset, translation=[pvDistance, 0, 0], os=True,
		         r=True)

		pm.poleVectorConstraint(legPoleVector.con, ik.handle)  # create pv

		# create foot control
		foot = rig_control(side=side, name='foot', shape='box', modify=1,
		                   scale=(15, 15, 15),
		                   parentOffset=legModule.controls,
		                   lockHideAttrs=['rx', 'ry', 'rz'])

		pm.delete(pm.pointConstraint(footJnt, foot.offset))
		pm.parentConstraint(foot.con, ik.handle, mo=True)
		pm.pointConstraint( foot.con, legPoleVector.modify, mo=True )

		foot.gimbal = createCtrlGimbal(foot)
		foot.pivot = createCtrlPivot(foot)

		constrainObject(foot.offset,
		                [biped.pelvisConnection, biped.centerConnection,
		                 'worldSpace_GRP'],
		                foot.ctrl, ['pelvis', 'main', 'world'],
		                type='parentConstraint')

		pm.addAttr(foot.ctrl, longName='twist', at='float', k=True)
		pm.connectAttr(foot.ctrl.twist, ik.handle.twist)

		# create hip aims
		hipAimZ_loc = rig_transform(0, name=side + 'hipAimZ', type='locator',
		                        parent=legModule.parts).object
		footAimZ_loc = rig_transform(0, name=side + 'footAimZ', type='locator',
		                            parent=legModule.parts).object

		pm.pointConstraint(biped.pelvisConnection, hipAimZ_loc)
		pm.pointConstraint(foot.con, footAimZ_loc)

		hipAimZ = mm.eval(
			'rig_makePiston("' + footAimZ_loc + '", "' + hipAimZ_loc + '", "' + side +
			'_hipAimZ");')


		# y rotation

		hipAimY_loc = rig_transform(0, name=side + 'hipAimY', type='locator',
		                            parent=legModule.parts).object
		footAimY_loc = rig_transform(0, name=side + 'footAimY', type='locator',
		                             parent=legModule.parts).object

		pm.pointConstraint(biped.pelvisConnection, hipAimY_loc)
		pm.pointConstraint(foot.con, footAimY_loc)

		hipAimY = mm.eval(
			'rig_makePiston("' + footAimY_loc + '", "' + hipAimY_loc + '", '
			                                                           '"' + side +
			'_hipAimY");')

		# constrain shizzle


def kiddoFinish():
	print 'Finishing kiddo'






