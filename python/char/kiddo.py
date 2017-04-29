__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import rig_biped
from rutils.rig_modules import rig_module
from make.rig_controls import *
from rutils.rig_utils import *
from rutils.rig_chain import *
from make.rig_ik import rig_ik

'''

import char.kiddo as char
char.kiddoPuppet()

'''

def kiddoPuppet():
	puppet('kiddo_v001', character='kiddo')


def kiddoPrepareRig():
	print 'Prepare kiddo'

	for side in ('l_', 'r_'):
		mc.parent(side+'clavicleJA_JNT', w=True)
		mc.parent(side+'armJA_JNT', w=True)
		mc.parent(side+'legJA_JNT', w=True )
		mc.parent(side+'hipZ_JA_JNT', w=True  )
		mc.parent(side+'hipY_JA_JNT', w=True)

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
	                        lockHideAttrs=['tx','ty','tz'],rotateOrder=2 )

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
	                        lockHideAttrs=['tx','ty','tz', 'rx','rz'], rotateOrder=2 )

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
		pm.parent(ik.handle, legModule.parts)

		# pole vector
		legPoleVector = rig_control(side=side, name='legPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx', 'ry', 'rz'],
		                         targetOffset=[legJnt, footJnt],
		                         parentOffset=legModule.controls, scale=(2,2,2))

		pm.delete(pm.aimConstraint(ankleJnt, legPoleVector.offset, mo=False))

		kneePos = pm.xform(kneeJnt, translation=True, query=True, ws=True)
		poleVectorPos = pm.xform(legPoleVector.con, translation=True, query=True,
		                         ws=True)

		pvDistance = lengthVector(kneePos, poleVectorPos)

		pm.xform(legPoleVector.offset, translation=[-25, 0, 0], os=True,
		         r=True)

		pm.poleVectorConstraint(legPoleVector.con, ik.handle)  # create pv
		
		#pm.parentConstraint(biped.centerConnection, legPoleVector.offset, mo=True)
		pm.parentConstraint(hipYJnt, legPoleVector.offset, mo=True)

		if side == 'r':
			pm.rotate(legPoleVector.ctrl.cv, 0, -90, 0, r=True, os=True)
		else:
			pm.rotate(legPoleVector.ctrl.cv, 0, 90, 0, r=True, os=True)

		# create foot control
		foot = rig_control(side=side, name='foot', shape='box', modify=1,
		                   scale=(15, 15, 15),
		                   parentOffset=legModule.controls,
		                   lockHideAttrs=['rx', 'ry', 'rz'])

		pm.delete(pm.pointConstraint(footJnt, foot.offset))
		pm.parentConstraint(foot.con, ik.handle, mo=True)
		#pm.pointConstraint( foot.con, legPoleVector.modify, mo=True )

		'''
		setAttr "l_leg_ikHandle.springAngleBias[0].springAngleBias_FloatValue" 0;
		setAttr "l_leg_ikHandle.springAngleBias[1].springAngleBias_FloatValue" 0.5;
		spring bias

		'''

		foot.gimbal = createCtrlGimbal(foot)
		foot.pivot = createCtrlPivot(foot)

		constrainObject(foot.offset,
		                [biped.pelvisConnection, biped.centerConnection,
		                 'worldSpace_GRP'],
		                foot.ctrl, ['pelvis', 'main', 'world'],
		                type='parentConstraint')

		pm.setAttr(foot.ctrl.space, 2)

		pm.addAttr(foot.ctrl, longName='twist', at='float', k=True)
		pm.connectAttr(foot.ctrl.twist, ik.handle.twist)

		# create hip aims
		hipAimZ_loc = rig_transform(0, name=side + '_hipAimZ', type='locator',
		                        parent=legModule.parts, target=hipZJnt).object
		footAimZ_loc = rig_transform(0, name=side + '_footAimZ', type='locator',
		                            parent=legModule.parts).object

		pm.pointConstraint(biped.pelvisConnection, hipAimZ_loc, mo=True)
		pm.parentConstraint(foot.con, footAimZ_loc)

		# z rotation

		hipAimZ = mm.eval(
			'rig_makePiston("' + footAimZ_loc + '", "' + hipAimZ_loc + '", "' + side +
			'_hipAimZ");')

		hipZ = rig_control(side=side, name='hipRoll', shape='sphere', modify=1,
		                   scale=(5, 5, 7),
		                   parentOffset=legModule.controls, targetOffset=hipZJnt,
		                   lockHideAttrs=['tx','ty','tz','rx', 'ry'],
		                   rotateOrder=0)

		pm.parentConstraint(hipZ.con, hipZJnt, mo=True)
		pm.parentConstraint( lowerBody.con, hipZ.offset, mo=True )
		#rotCon = pm.parentConstraint(hipAimZ_loc, hipZ.modify, mo=True,
		#                             skipTranslate=('x', 'y', 'z'),
		#                             skipRotate=('x', 'y'))
		rotCon = pm.orientConstraint(hipAimZ_loc, hipZ.modify, mo=True, skip=('x',
		                                                                      'y'))
		target = rotCon.getWeightAliasList()[0]
		pm.addAttr(hipZ.ctrl, longName='aim', at='long', k=True, min=0, max=1, dv=1)
		pm.connectAttr ( hipZ.ctrl.aim, target )



		# y rotation

		hipAimY_loc = rig_transform(0, name=side + '_hipAimY', type='locator',
		                            parent=legModule.parts,target=hipYJnt).object
		footAimY_loc = rig_transform(0, name=side + '_footAimY', type='locator',
		                             parent=legModule.parts).object

		pm.pointConstraint(hipZJnt, hipAimY_loc,mo=True)
		pm.parentConstraint(foot.con, footAimY_loc)

		hipAimY = mm.eval(
			'rig_makePiston("' + footAimY_loc + '", "' + hipAimY_loc + '", '
			                                                           '"' + side +
			'_hipAimY");')

		pm.setAttr( side+'_hipAimZ_LOC.rotateOrder', 4 )

		hipY = rig_control(side=side, name='hipYaw', shape='sphere', modify=1,
		                   scale=(5, 7, 5),
		                   parentOffset=legModule.controls, targetOffset=hipYJnt,
		                   lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'],
		                   rotateOrder=2)

		pm.parentConstraint(hipY.con, hipYJnt, mo=True)
		pm.parentConstraint(hipZ.con, hipY.offset, mo=True)
		#rotCon = pm.parentConstraint(hipAimY_loc, hipY.modify, mo=True,
		#                             skipTranslate=('x', 'y', 'z'),
		#                             skipRotate=('x', 'z'))
		rotCon = pm.orientConstraint(hipAimY_loc, hipY.modify, mo=True, skip=('x',
		                                                                      'z'))
		target = rotCon.getWeightAliasList()[0]
		pm.addAttr(hipY.ctrl, longName='aim', at='long', k=True, min=0, max=1, dv=1)
		pm.connectAttr(hipY.ctrl.aim, target)



		# constrain shizzle
		
		legTop = rig_transform(0, name=side + '_legTop',
		                            target=legJnt, parent=legModule.parts).object
		
		legSkeletonParts = rig_transform(0, name=side + '_legSkeletonParts',
		                                 parent=legTop).object

		pm.parent( hipAimY, hipAimZ, legModule.parts )
		pm.parent( legJntIK,legJnt, legSkeletonParts )
		pm.parentConstraint( hipYJnt, legTop, mo=True, skipRotate=('x','y','z') )

		pm.connectAttr(legJntIK+'.rotate', legJnt+'.rotate')
		pm.connectAttr(kneeJntIK+'.rotate', kneeJnt+'.rotate')
		pm.connectAttr(ankleJntIK+'.rotate', ankleJnt+'.rotate')

		pm.parent(hipZJnt, legModule.skeleton)
		pm.parent(hipYJnt, legModule.skeleton)





def kiddoFinish():
	print 'Finishing kiddo'








