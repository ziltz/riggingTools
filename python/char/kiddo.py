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
from rutils.rig_nodes import *

'''

import char.kiddo as char
char.kiddoPuppet()

'''

def kiddoPuppet():
	puppet( character='kiddo' )


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

	pm.move(upperBody.ctrl.cv, [0, 10, 0], relative=True, objectSpace=True)


	upperWaistXYZ = simpleControls(['upperWaistY_JA_JNT', 'upperWaistZ_JA_JNT',
	                               'upperWaistX_JA_JNT'],
	               modify=1, scale=(45,10,50),
	               parentOffset=bodyModule.controls,
	               lockHideAttrs=['tx', 'ty', 'tz'])

	upperWaistY = upperWaistXYZ['upperWaistY_JA_JNT']
	upperWaistZ = upperWaistXYZ['upperWaistZ_JA_JNT']
	upperWaistX = upperWaistXYZ['upperWaistX_JA_JNT']

	pm.hide( upperWaistY.offset, upperWaistZ.offset, upperWaistX.offset )

	constrainObject(upperBody.modify,
	                [upperBody.offset, 'worldSpace_GRP'],
	                upperBody.ctrl, ['main', 'world'], type='orientConstraint')

	constrainObject(upperWaistY.modify,
	                [upperWaistY.offset, 'worldSpace_GRP'],
	                upperBody.ctrl, ['main', 'world'], type='orientConstraint',
	                skip=('x','z'))

	constrainObject(upperWaistZ.modify,
	                [upperWaistZ.offset, 'worldSpace_GRP'],
	                upperBody.ctrl, ['main', 'world'], type='orientConstraint',
	                skip=('x', 'y'))

	constrainObject(upperWaistX.modify,
	                [upperWaistX.offset, 'worldSpace_GRP'],
	                upperBody.ctrl, ['main', 'world'], type='orientConstraint',
	                skip=('z', 'y'))

	pm.connectAttr( upperBody.ctrl.rotateX, upperWaistX.ctrl.rotateX )
	pm.connectAttr( upperBody.ctrl.rotateY, upperWaistY.ctrl.rotateY )
	pm.connectAttr( upperBody.ctrl.rotateZ, upperWaistZ.ctrl.rotateZ )



	lowerBody = rig_control(name='lowerBody', shape='box', modify=1,
	                        targetOffset='lowerBodyJA_JNT',
	                        constrainOffset=main.con, scale=(40, 20, 30),
	                        colour='green',  parentOffset=bodyModule.controls,
	                        lockHideAttrs=['tx','ty','tz', 'rx','rz'], rotateOrder=2 )

	constrainObject(lowerBody.modify,
	                [lowerBody.offset, 'worldSpace_GRP'],
	                lowerBody.ctrl, ['main', 'world'], type='orientConstraint',
	                skip=('x','z'))

	pm.parentConstraint(lowerBody.con, 'lowerBodyJA_JNT', mo=True)

	pm.move(lowerBody.ctrl.cv, [0, -10, 0], relative=True, objectSpace=True)

	biped = rig_biped()
	biped.spineConnection = 'upperWaistX_JA_JNT'
	biped.pelvisConnection = 'lowerBodyJA_JNT'
	biped.centerConnection = 'mainJA_JNT'
	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=10)

		fingersModule = biped.hand( side, ctrlSize= 2.2 )

		shoulderModule = biped.shoulder(side, ctrlSize = 12)

		biped.connectArmShoulder(side)
		
		
		secColour = 'deepskyblue'
		if side == 'r':
			secColour = 'magenta'


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
		                         parentOffset=legModule.parts, scale=(2,2,2))

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
		                   scale=(13, 13, 13),
		                   parentOffset=legModule.controls,
		                   lockHideAttrs=['rx', 'ry', 'rz'])

		pm.delete(pm.pointConstraint(footJnt, foot.offset))
		pm.parentConstraint(foot.con, ik.handle, mo=True)
		#pm.pointConstraint( foot.con, legPoleVector.modify, mo=True )

		foot.gimbal = createCtrlGimbal(foot)
		foot.pivot = createCtrlPivot(foot)

		constrainObject(foot.offset,
		                [biped.pelvisConnection, biped.centerConnection,
		                 'worldSpace_GRP'],
		                foot.ctrl, ['pelvis', 'main', 'world'],
		                type='parentConstraint')

		pm.setAttr(foot.ctrl.space, 2)

		pm.addAttr(foot.ctrl, longName='twist', at='float', k=True)
		pm.addAttr(foot.ctrl, longName='springBiasBottom', at='float',min=0,max=1,
		           k=True, dv=0)
		pm.addAttr(foot.ctrl, longName='springBiasTop', at='float', min=0, max=1,
		           k=True, dv=0.5)
		pm.connectAttr(foot.ctrl.twist, ik.handle.twist)

		pm.connectAttr(foot.ctrl.springBiasBottom,
		               ik.handle+'.springAngleBias[0].springAngleBias_FloatValue',
		               f=True)
		pm.connectAttr(foot.ctrl.springBiasTop,
		               ik.handle + '.springAngleBias[1].springAngleBias_FloatValue',
		               f=True)


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
		                   parentOffset=legModule.parts, targetOffset=hipZJnt,
		                   lockHideAttrs=['tx','ty','tz','rx', 'ry'],
		                   rotateOrder=0)

		pm.parentConstraint(hipZ.con, hipZJnt, mo=True)
		pm.parentConstraint( lowerBody.con, hipZ.offset, mo=True )

		rotCon = pm.orientConstraint(hipZ.offset, hipAimZ_loc, hipZ.modify, mo=True,
		                             skip=('x','y'))
		targetZ = rotCon.getWeightAliasList()
		#pm.addAttr(hipZ.ctrl, longName='aim', at='float', k=True, min=0, max=1,
		# dv=1)
		#pm.connectAttr ( hipZ.ctrl.aim, target )



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
		rotCon = pm.orientConstraint(hipY.offset, hipAimY_loc, hipY.modify,
		                             mo=True, skip=('x','z'))
		targetY = rotCon.getWeightAliasList()
		pm.addAttr(hipY.ctrl, longName='aim', at='float', k=True, min=0, max=1, dv=1)
		pm.connectAttr(hipY.ctrl.aim, targetY[1])
		pm.connectAttr(hipY.ctrl.aim, targetZ[1])
		connectReverse( name=side+'_leg',input=(hipY.ctrl.aim, hipY.ctrl.aim,0),
		                output=(targetY[0], targetZ[0],0) )

		pm.setAttr( rotCon.interpType, 2 )
		pm.transformLimits(hipY.modify, ry=(-30, 10), ery=(1, 1))

		# constrain shizzle
		
		legTop = rig_transform(0, name=side + '_legTop',
		                            target=legJnt, parent=legModule.skeleton).object

		pm.setAttr( legTop+'.inheritsTransform', 0 )
		pm.scaleConstraint( 'worldScale_GRP', legTop )
		legSkeletonParts = rig_transform(0, name=side + '_legSkeletonParts',
		                                 parent=legTop).object

		pm.parent( hipAimY, hipAimZ, legModule.parts )
		pm.parent( legJntIK,legJnt, legSkeletonParts )
		pm.hide( legJntIK )
		pm.parentConstraint( hipYJnt, legTop, mo=True, skipRotate=('x','y','z') )

		#pm.connectAttr(legJntIK+'.rotate', legJnt+'.rotate')
		pm.connectAttr(kneeJntIK+'.rotate', kneeJnt+'.rotate')
		pm.connectAttr(ankleJntIK+'.rotate', ankleJnt+'.rotate')

		multiplyDivideNode('legRotate', 'multiply', input1=[legJntIK+'.rotateX',
		                                                    legJntIK+'.rotateY',
		                                                    legJntIK + '.rotateZ'],
		                   input2=[1, hipY.ctrl.aim, hipY.ctrl.aim],
		                   output=[legJnt + '.rotateX',
		                           legJnt + '.rotateY',
		                           legJnt + '.rotateZ'])

		pm.parent(hipZJnt, legModule.skeleton)
		pm.parent(hipYJnt, legModule.skeleton)

		footJnts = [side+'_heelRotY_JA_JNT', side+'_footRotX_JA_JNT',
		            side+'_footRotY_JA_JNT', side+'_footRotZ_JA_JNT']
		footControls = simpleControls( footJnts, modify=2, scale=(11,3,20),
		                               parentOffset=legModule.parts,
		                               colour=secColour,
		                               lockHideAttrs=['tx', 'ty', 'tz'])

		#footControls[side+'']

		ankle = rig_control(side=side, name='ankle', shape='box', modify=1,
		                   scale=(10, 6, 8), colour=secColour,
		                   parentOffset=legModule.controls,
		                   targetOffset=side+'_footRotZ_JA_JNT',
		                   lockHideAttrs=['tx', 'ty','tz', 'ry'])

		pm.parentConstraint( footJnt, ankle.offset, mo=True )

		heel = footControls[side+'_heelRotY_JA_JNT']
		footRotX = footControls[side+'_footRotX_JA_JNT']
		footRotY = footControls[side+'_footRotY_JA_JNT']
		footRotZ = footControls[side+'_footRotZ_JA_JNT']

		pm.parent( heel.offset, legModule.controls )
		heel.ctrl.rotateX.setKeyable(False)
		heel.ctrl.rotateX.setLocked(False)
		heel.ctrl.rotateZ.setKeyable(False)
		heel.ctrl.rotateZ.setLocked(False)

		pm.parentConstraint( footRotY.con, heel.modify[0], mo=True )
		pm.parentConstraint( footRotZ.con, footRotY.modify[0], mo=True)
		pm.parentConstraint( footRotX.con, footRotZ.modify[0], mo=True)

		footSpace = footJnt
		if side == 'l':
			footSpace = rig_transform( 0, name='l_footSpace', parent=legModule.parts,
			                           target=footJnt).object
			pm.setAttr( footSpace+'.rotateX', 0 )
			pm.parentConstraint( footJnt, footSpace, mo=True)

		toeSpaceList = ('lowerBody', 'foot','main', 'world')
		constrainObject(heel.modify[1],
		                [biped.pelvisConnection, footSpace, biped.centerConnection,
		                 'worldSpace_GRP'],
		                heel.ctrl, toeSpaceList,
		                type='orientConstraint', skip=('x','z'))

		constrainObject(footRotX.modify[0],
		                [biped.pelvisConnection, footSpace, biped.centerConnection,
		                 'worldSpace_GRP'],
		                footRotX.ctrl, toeSpaceList,
		                type='orientConstraint', skip=('y', 'z'))

		constrainObject(footRotZ.modify[1],
		                [biped.pelvisConnection, footSpace, biped.centerConnection,
		                 'worldSpace_GRP'],
		                footRotZ.ctrl, toeSpaceList,
		                type='orientConstraint', skip=('x', 'y'))

		pm.connectAttr( ankle.ctrl.rotateX, footRotX.ctrl.rotateX )
		#pm.connectAttr( ankle.ctrl.rotateY, heel.ctrl.rotateY )
		#connectNegative(ankle.ctrl.rotateY, heel.ctrl.rotateY)
		pm.connectAttr( ankle.ctrl.rotateZ, footRotZ.ctrl.rotateZ )

		pm.addAttr(ankle.ctrl, ln='SPACES', at='enum',
		           enumName='___________',
		           k=True)
		ankle.ctrl.SPACES.setLocked(True)
		pm.addAttr(ankle.ctrl, ln='rollSpace', at='enum',
		           enumName='lowerBody:foot:main:world', k=True)
		#pm.addAttr(ankle.ctrl, ln='yawSpace', at='enum',
		#           enumName='lowerBody:foot:main:world', k=True)
		pm.addAttr(ankle.ctrl, ln='pitchSpace', at='enum',
		           enumName='lowerBody:foot:main:world', k=True)

		pm.connectAttr( ankle.ctrl.rollSpace, footRotX.ctrl.space )
		#pm.connectAttr( ankle.ctrl.yawSpace, heel.ctrl.space)
		pm.connectAttr( ankle.ctrl.pitchSpace, footRotZ.ctrl.space )

		pm.addAttr(ankle.ctrl, ln='MOTION', at='enum',
		           enumName='___________',
		           k=True)
		ankle.ctrl.MOTION.setLocked(True)

		pm.addAttr(ankle.ctrl, longName='fangs', at='float', k=True, min=0, max=10,
		           dv=0)
		fangsJnt = pm.PyNode(side+'_toeFangsJA_JNT')
		fangsTranslate = fangsJnt.translate.get()
		pm.setDrivenKeyframe(fangsJnt.translateX, cd=ankle.ctrl.fangs, dv=0,
		                     v=fangsTranslate[0])
		pm.setDrivenKeyframe(fangsJnt.translateY, cd=ankle.ctrl.fangs, dv=0,
		                     v=fangsTranslate[1])
		pm.setDrivenKeyframe(fangsJnt.translateZ, cd=ankle.ctrl.fangs, dv=0,
		                     v=fangsTranslate[2])
		pm.move(0, 1.5, 0, fangsJnt, r=True, os=True)
		fangsTranslate = fangsJnt.translate.get()
		pm.move(0, -1.5, 0, fangsJnt, r=True, os=True)
		pm.setDrivenKeyframe(fangsJnt.translateX, cd=ankle.ctrl.fangs, dv=10,
		                     v=fangsTranslate[0])
		pm.setDrivenKeyframe(fangsJnt.translateY, cd=ankle.ctrl.fangs, dv=10,
		                     v=fangsTranslate[1])
		pm.setDrivenKeyframe(fangsJnt.translateZ, cd=ankle.ctrl.fangs, dv=10,
		                     v=fangsTranslate[2])

		pm.addAttr(ankle.ctrl, longName='toeCapRotate', at='float', k=True, dv=0)
		if side == 'l':
			pm.connectAttr( ankle.ctrl.toeCapRotate, 'l_footCapJA_JNT.rotateX', f=True)
		else:
			connectReverse( ankle.ctrl.toeCapRotate, 'r_footCapJA_JNT.rotateX' )


		# simple controls

		simpleControls( side+'_kneeCapJA_JNT' , colour=secColour,
		                               modify=1, scale=(10,10, 3),
		                              parentOffset=legModule.controls,
		                              lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'] )

		simpleControls(side + '_ballsJA_JNT', colour=secColour,
		               modify=1, scale=(3, 6, 6),
		               parentOffset=legModule.controls,
		               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

		simpleControls(side + '_shoulderShieldJA_JNT', colour=secColour,
		               modify=1, scale=(4, 4, 4),
		               parentOffset=armModule.controls,
		               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])



	# assymentrical controls
	simpleControls('r_gunBarrelJA_JNT', colour=secColour, scale=(4, 4, 4),
	               parentOffset=armModule.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])

	simpleControls('missileJA_JNT', colour='white', scale=(8, 6, 8),
	               parentOffset=bodyModule.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

def kiddoFinish():
	print 'Finishing kiddo'

	# removing aim attribute temporary
	for side in ('l', 'r'):
		hip = pm.PyNode(side+'_hipYaw_CTRL')
		hip.aim.set(k=False, cb=False)

		# main space
		#pm.setAttr(side+'_foot_CTRL.space', 1)
		pm.setAttr(side + '_heelRotY_CTRL.space', 1)










