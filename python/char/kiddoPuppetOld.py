__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import rig_biped

from make.rig_controls import *
from make.rig_ik import rig_ik

from rutils.rig_modules import rig_module
from rutils.rig_utils import *
from rutils.rig_chain import *
from rutils.rig_nodes import *
from rutils.rig_anim import *

import string

'''

import char.kiddoPuppet as char
char.buildPuppet()

'''

def buildPuppet():
	puppet( character='kiddo' )


def kiddoPrepareRig():
	print 'Prepare kiddo'

	for side in ('l_', 'r_'):
		mc.parent(side+'clavicleJA_JNT', w=True)
		mc.parent(side+'armJA_JNT', w=True)
		mc.parent(side+'legJA_JNT', w=True )
		mc.parent(side+'hipZ_JA_JNT', w=True  )
		mc.parent(side+'hipY_JA_JNT', w=True)
		#mc.parent(side+'handRotYJA_JNT', w=True  )

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
	               parentOffset=bodyModule.parts,
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

		fingersModule = biped.hand( side, ctrlSize= 2.5 )

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

		hipY = rig_control(side=side, name='hipYaw', shape='sphere', modify=2,
		                   scale=(5, 7, 5),
		                   parentOffset=legModule.controls, targetOffset=hipYJnt,
		                   lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'],
		                   rotateOrder=2)

		pm.parentConstraint(hipY.con, hipYJnt, mo=True)
		pm.parentConstraint(hipZ.con, hipY.offset, mo=True)
		#rotCon = pm.parentConstraint(hipAimY_loc, hipY.modify, mo=True,
		#                             skipTranslate=('x', 'y', 'z'),
		#                             skipRotate=('x', 'z'))
		rotCon = pm.orientConstraint(hipY.offset, hipAimY_loc, hipY.modify[0],
		                             mo=True, skip=('x','z'))
		targetY = rotCon.getWeightAliasList()
		pm.addAttr(hipY.ctrl, longName='aim', at='float', k=True, min=0, max=1, dv=1)
		pm.connectAttr(hipY.ctrl.aim, targetY[1])
		pm.connectAttr(hipY.ctrl.aim, targetZ[1])
		connectReverse( name=side+'_leg',input=(hipY.ctrl.aim, hipY.ctrl.aim,0),
		                output=(targetY[0], targetZ[0],0) )

		pm.setAttr( rotCon.interpType, 2 )
		pm.transformLimits(hipY.modify[0], ry=(-30, 10), ery=(1, 1))

		pm.addAttr(hipY.ctrl, longName='aimRotation', at='float', k=True, min=0,
		           max=10,
		           dv=0)

		pm.addAttr(hipY.ctrl, longName='limitOutRotation', at='float', k=True, min=0,
		           max=10,
		           dv=3)
		pm.addAttr(hipY.ctrl, longName='limitInRotation', at='float', k=True, min=0,
		           max=10,
		           dv=0)
		hipY.ctrl.limitOutRotation.set(cb=True)
		hipY.ctrl.limitInRotation.set(cb=True)

		pm.setDrivenKeyframe(hipY.modify[0]+'.minRotYLimit' ,
		                     cd=hipY.ctrl.limitOutRotation,
		                     dv=0, v=-45 )
		pm.setDrivenKeyframe(hipY.modify[0]+'.minRotYLimit',
		                     cd=hipY.ctrl.limitOutRotation,
		                     dv=10, v=0)
		pm.setDrivenKeyframe(hipY.modify[0]+'.maxRotYLimit',
		                     cd=hipY.ctrl.limitInRotation,
		                     dv=0, v=10)
		pm.setDrivenKeyframe(hipY.modify[0]+'.maxRotYLimit',
		                     cd=hipY.ctrl.limitInRotation,
		                     dv=10, v=0)

		rotCon = pm.orientConstraint(hipY.offset, hipY.modify[0], hipY.modify[1],
		                             mo=True)
		conTargets = rotCon.getWeightAliasList()
		pm.setDrivenKeyframe(conTargets[0],
		                     cd=hipY.ctrl.aimRotation,
		                     dv=0, v=1)
		pm.setDrivenKeyframe(conTargets[0],
		                     cd=hipY.ctrl.aimRotation,
		                     dv=10, v=0)
		connectReverse(name=side + '_hipYTarget', input=(conTargets[0], 0, 0),
		               output=(conTargets[1], 0, 0))

		# constrain shizzle

		legTop = rig_transform(0, name=side + '_legTop',
		                            target=legJnt, parent=legModule.skeleton).object

		pm.setAttr( legTop+'.inheritsTransform', 0 )
		pm.scaleConstraint( 'worldSpace_GRP', legTop )
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
		heel.ctrl.rotateX.setLocked(True)
		heel.ctrl.rotateZ.setKeyable(False)
		heel.ctrl.rotateZ.setLocked(True)

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

		pm.addAttr(ankle.ctrl, longName='footFangs', at='float', k=True, min=0,
		           max=10,
		           dv=0)
		pm.addAttr(ankle.ctrl, longName='toeFangs', at='float', k=True, min=0,
		           max=10,
		           dv=0)
		fangsJnt = pm.PyNode(side+'_toeFangsJA_JNT')
		toeFangsJnt = pm.PyNode(side + '_footFangsJA_JNT')
		fangsTranslate = fangsJnt.translate.get()
		pm.setDrivenKeyframe(fangsJnt.translateX, cd=ankle.ctrl.footFangs, dv=0,
		                     v=fangsTranslate[0])
		pm.setDrivenKeyframe(fangsJnt.translateY, cd=ankle.ctrl.footFangs, dv=0,
		                     v=fangsTranslate[1])
		pm.setDrivenKeyframe(fangsJnt.translateZ, cd=ankle.ctrl.footFangs, dv=0,
		                     v=fangsTranslate[2])
		pm.move(0, 1.5, 0, fangsJnt, r=True, os=True)
		fangsTranslate = fangsJnt.translate.get()
		pm.move(0, -1.5, 0, fangsJnt, r=True, os=True)
		pm.setDrivenKeyframe(fangsJnt.translateX, cd=ankle.ctrl.footFangs, dv=10,
		                     v=fangsTranslate[0])
		pm.setDrivenKeyframe(fangsJnt.translateY, cd=ankle.ctrl.footFangs, dv=10,
		                     v=fangsTranslate[1])
		pm.setDrivenKeyframe(fangsJnt.translateZ, cd=ankle.ctrl.footFangs, dv=10,
		                     v=fangsTranslate[2])

		# foot fangs
		fangsTranslate = toeFangsJnt.translate.get()
		pm.setDrivenKeyframe(toeFangsJnt.translateX, cd=ankle.ctrl.toeFangs, dv=0,
		                     v=fangsTranslate[0])
		pm.setDrivenKeyframe(toeFangsJnt.translateY, cd=ankle.ctrl.toeFangs, dv=0,
		                     v=fangsTranslate[1])
		pm.setDrivenKeyframe(toeFangsJnt.translateZ, cd=ankle.ctrl.toeFangs, dv=0,
		                     v=fangsTranslate[2])
		pm.move(0, 0, -4.7, toeFangsJnt, r=True, os=True)
		fangsTranslate = toeFangsJnt.translate.get()
		pm.move(0, 0, 4.7,toeFangsJnt, r=True, os=True)
		pm.setDrivenKeyframe(toeFangsJnt.translateX, cd=ankle.ctrl.toeFangs, dv=10,
		                     v=fangsTranslate[0])
		pm.setDrivenKeyframe(toeFangsJnt.translateY, cd=ankle.ctrl.toeFangs, dv=10,
		                     v=fangsTranslate[1])
		pm.setDrivenKeyframe(toeFangsJnt.translateZ, cd=ankle.ctrl.toeFangs, dv=10,
		                     v=fangsTranslate[2])


		pm.addAttr(ankle.ctrl, longName='toeCapRotate', at='float', k=True, dv=0)
		if side == 'l':
			pm.connectAttr( ankle.ctrl.toeCapRotate, 'l_footCapJA_JNT.rotateX', f=True)
		else:
			connectReverse( ankle.ctrl.toeCapRotate, 'r_footCapJA_JNT.rotateX' )


		# simple controls
		legSidesSimpleControls(legModule, side, secColour)

		armSidesSimpleControls(armModule, side, secColour)

	# asymettrical controls
	bodySimpleControls(bodyModule)




def kiddoFinish():
	print 'Finishing kiddo'

	# removing aim attribute temporary
	for side in ('l', 'r'):
		hip = pm.PyNode(side+'_hipYaw_CTRL')
		hip.aim.set(k=False, cb=False)

		# main space
		#pm.setAttr(side+'_foot_CTRL.space', 1)
		pm.setAttr(side + '_ankle_CTRL.pitchSpace', 2)
		pm.setAttr(side + '_ankle_CTRL.rollSpace', 2)
		pm.setAttr(side + '_heelRotY_CTRL.space', 1)

		pm.addAttr(side+'_foot_CTRL.twist', edit=1, minValue=-30, maxValue=30)



def bodySimpleControls(module):
	sc = simpleControls('missileJA_JNT', colour='white', scale=(7, 6, 8),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])
	missile = sc['missileJA_JNT']
	pm.move(0, 2.1, 2.5, missile.ctrl.cv, os=True, r=True)
	pm.addAttr(missile.ctrl, ln='MOTION', at='enum',
	           enumName='___________',
	           k=True)
	missile.ctrl.MOTION.setLocked(True)
	pm.addAttr(missile.ctrl, longName='cockFlaps', at='float',
	           k=True, dv=0, min=0, max=10)
	pm.addAttr(missile.ctrl, longName='offsetLeftFlaps', at='float',
	           k=True, dv=0, min=-10, max=10)
	pm.addAttr(missile.ctrl, longName='offsetRightFlaps', at='float',
	           k=True, dv=0, min=-10, max=10)

	ABC = list(string.ascii_uppercase)
	missileBayJnts = []
	missileBay = []
	missileBayHingeJnts = []
	missileBayHinge = []
	missileBayFlapJnts = []
	missileBayFlap = []
	for i in range(0, 5):
		missileBayJnts.append( 'missileBay'+ABC[i]+'JA_JNT')
		missileBayHingeJnts.append('missileBayHinge' + ABC[i] + 'JA_JNT')
		missileBayFlapJnts.append( 'missileBayFlap'+ABC[i]+'JA_JNT'  )

	scBay = simpleControls(missileBayJnts, colour='red', scale=(0.3, 0.3, 0.3),
	                    parentOffset=module.controls, modify=3,
	                    lockHideAttrs=['tx', 'tz', 'rx','ry', 'rz'])

	sc = simpleControls(missileBayHingeJnts+missileBayFlapJnts, colour='yellow',
	                    scale=(0.1, 0.3, 0.1), modify=3, shape='cylinder',
	                    parentOffset=module.controls,
	                    lockHideAttrs=['tx', 'tz', 'ty', 'ry', 'rx'])

	for i in range (0,5):
		missileBay.append(scBay[missileBayJnts[i]])
		missileBayHinge.append(sc[missileBayHingeJnts[i]])
		missileBayFlap.append(sc[missileBayFlapJnts[i]])

	missileBayHingeMods1 = []
	missileBayHingeMods2 = []
	missileBayFlapMods1 = []
	missileBayFlapMods2 = []
	for i in range(0,5):

		pm.move(0.2, 0, 0, missileBay[i].ctrl.cv, os=True, r=True)
		pm.rotate(missileBayHinge[i].ctrl.cv, -90, 0, 0, os=True, r=True)
		pm.rotate(missileBayFlap[i].ctrl.cv, -90, 0, 0, os=True, r=True)

		pm.transformLimits(missileBay[i].ctrl, ty=(-2.315, 0), ety=(1, 1))
		pm.transformLimits(missileBayHinge[i].ctrl, rz=(0, 0), erz=(0, 1))
		pm.transformLimits(missileBayFlap[i].ctrl, rz=(0, 0), erz=(0, 1))

		rig_animDrivenKey(missile.ctrl.cockFlaps, (2, 10),
		                  missileBay[i].modify[0] + '.translateY', (0,-2.315 ))
		rig_animDrivenKey(missile.ctrl.cockFlaps, (0, 5),
		                  missileBayHinge[i].modify[0] + '.rotateZ', (0, -45 ))
		rig_animDrivenKey(missile.ctrl.cockFlaps, (0, 5),
		                  missileBayFlap[i].modify[0] + '.rotateZ', (0, -45 ))
		missileBayHingeMods1.append(missileBayHinge[i].modify[1])
		missileBayHingeMods2.append(missileBayHinge[i].modify[2])
		missileBayFlapMods1.append(missileBayFlap[i].modify[1])
		missileBayFlapMods2.append(missileBayFlap[i].modify[2])

	offsetSDKControls(missile.ctrl, missileBayHingeMods1, transformAttr='rz',
	                  attr='offsetRightFlaps', sdkVal=-45)
	offsetSDKControls(missile.ctrl, missileBayFlapMods1, transformAttr='rz',
	                  attr='offsetRightFlaps', sdkVal=-45)
	offsetSDKControls(missile.ctrl, missileBayHingeMods2, transformAttr='rz',
	                  attr='offsetLeftFlaps', sdkVal=-45, reverse=1)
	offsetSDKControls(missile.ctrl, missileBayFlapMods2, transformAttr='rz',
	                  attr='offsetLeftFlaps', sdkVal=-45, reverse=1)

	simpleControls('l_buckleJA_JNT', colour='white', scale=(2, 2, 2),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	simpleControls('radarJA_JNT', colour='white', scale=(6, 4, 6),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	simpleControls('securityCamJA_JNT', colour='white', scale=(1.5, 0.5, 1.5),
	               parentOffset=module.controls, shape='cylinder',
	               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])

	sc = simpleControls('topHatchJA_JNT', colour='red', scale=(4, 0.3, 4),
	               parentOffset=module.controls, shape='cylinder',
	               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])

	topHatch = sc['topHatchJA_JNT']
	pm.move(0, 0.5, 0, topHatch.ctrl.cv, os=True, r=True)

	sc = simpleControls(('cockpitTopJA_JNT','cockpitBottomJA_JNT'), colour='yellow',
	               scale=(7, 3, 10),
	               parentOffset=module.controls, shape='circle',
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	cockpitTop = sc['cockpitTopJA_JNT']
	pm.move( 0, 0, 10,cockpitTop.ctrl.cv, os=True, r=True)
	cockpitBottom = sc['cockpitBottomJA_JNT']
	pm.rotate(cockpitBottom.ctrl.cv ,40, 0, 0,  os=True, r=True)
	pm.scale(cockpitBottom.ctrl.cv, 1, 1, 0.6, os=True, r=True)


	# engine controls
	colour = 'blue'
	for side in ('l', 'r'):
		sc = simpleControls( side+'_engineJA_JNT' , colour='white', scale=(4, 3, 4),
		               parentOffset=module.controls, shape='cylinder',
		               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])
		engine = sc[side+'_engineJA_JNT']
		pm.addAttr(engine.ctrl, ln='MOTION', at='enum',
		           enumName='___________',
		           k=True)
		engine.ctrl.MOTION.setLocked(True)

		pm.addAttr(engine.ctrl, longName='engineRPM', at='float',
		           k=True, dv=15)
		pm.addAttr(engine.ctrl, longName='reverseRPM', at='long',
		           k=True, dv=0, min=0, max=1)
		pm.addAttr(engine.ctrl, longName='rotateFlaps', at='float',
		           k=True, dv=0)

		if side == 'r':
			colour = 'red'
		sc = simpleControls(( side+'_engineFlapAJA_JNT', side+'_engineFlapBJA_JNT',
		               side+'_engineFlapCJA_JNT'), modify=1,
		               colour=colour, scale=(3,1.5,0.5),
		               parentOffset=module.controls,
		               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])
		for jnt in sc:
			engineFlap = sc[jnt]
			pm.connectAttr( engine.ctrl.rotateFlaps, engineFlap.modify+'.rotateX' )

		mayaTime = pm.PyNode('time1')
		engineRotMD = multiplyDivideNode(side+'_engineRotate', 'multiply',
		                   input1=[mayaTime.outTime, 0,0],
		                   input2=[0.25, 0, 0],
		                   output=[])
		multiplyDivideNode(side + '_engineRpm', 'multiply',
		                   input1=[engineRotMD.outputX, 0, 0],
		                   input2=[engine.ctrl.engineRPM, 0, 0],
		                   output=[side+'_engineSpinJA_JNT.rotateY'])
		pm.setDrivenKeyframe(engineRotMD.input2X,
		                     cd=engine.ctrl.reverseRPM,
		                     dv=0, v=1)
		pm.setDrivenKeyframe(engineRotMD.input2X,
		                     cd=engine.ctrl.reverseRPM,
		                     dv=1, v=-1)

def armSidesSimpleControls(module, side, colour):
	shieldRotYControl = simpleControls(side + '_shoulderShieldRotYJA_JNT',
	               colour=colour,
	               modify=1, scale=(4, 4, 4),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])
	shieldRotXControl = simpleControls(side + '_shoulderShieldRotXJA_JNT',
                    colour=colour,
                    modify=1, scale=(4, 4, 4),
                    parentOffset=module.controls,
                    lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	shieldRotY = shieldRotYControl[side + '_shoulderShieldRotYJA_JNT']
	shieldRotX = shieldRotXControl[side + '_shoulderShieldRotXJA_JNT']
	pm.delete( pm.listRelatives( shieldRotX.offset, type="constraint") )
	pm.parentConstraint( shieldRotY.con, shieldRotX.offset, mo=True )

	if side == 'r':
		simpleControls('r_gunBarrelJA_JNT', colour=colour, scale=(4, 4, 4),
		               parentOffset=module.controls,
		               lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'])
		blade = simpleControls('r_bladeJA_JNT', colour=colour, scale=(5, 2, 13),
		               parentOffset=module.controls,
		               lockHideAttrs=['tx', 'ty', 'rx', 'ry','rz'])

		bladeCtrl = blade['r_bladeJA_JNT']
		pm.move( 0,0,10, bladeCtrl.ctrl.cv, os=True, r=True  )
		pm.transformLimits(bladeCtrl.ctrl, tz=(-20, 0), etz=(1, 1))



def legSidesSimpleControls(module, side, colour):
	simpleControls(side + '_kneeCapJA_JNT', colour=colour,
	               modify=1, scale=(10, 10, 3),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	simpleControls(side + '_ballsJA_JNT', colour=colour,
	               modify=1, scale=(3, 6, 6),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	carvesBlade = ( side+'_carvesBladeAJA_JNT', side+'_carvesBladeBJA_JNT',
	                side+'_carvesBladeCJA_JNT', side+'_carvesBladeDJA_JNT')
	sc = simpleControls( carvesBlade, colour=colour,
	                modify=3, scale=( 3,1.5,0.5 ), parentOffset=module.controls,
	                lockHideAttrs=[ 'tx','ty','tz','ry','rz' ])
	bladeA = sc[side+'_carvesBladeAJA_JNT']
	pm.addAttr(bladeA.ctrl, ln='MOTION', at='enum',
	           enumName='___________',
	           k=True)
	bladeA.ctrl.MOTION.setLocked(True)
	pm.addAttr(bladeA.ctrl, longName='rotateFlaps', at='float',
	           k=True, dv=0)
	col = name_to_rgb('white')
	bladeA.ctrl.overrideColorRGB.set(col[0], col[1], col[2])
	bladeMods = []
	bladeMods2 = []
	for i in range(0,4):
		blade = sc[carvesBlade[i]]
		pm.connectAttr(bladeA.ctrl.rotateFlaps, blade.modify[0]+'.rotateX')
		bladeMods.append(blade.modify[1])
		bladeMods2.append(blade.modify[2])

	offsetSDKControls(bladeA.ctrl, bladeMods,transformAttr ='rx',
						attr='offsetRotationBottom', sdkVal=100)
	offsetSDKControls(bladeA.ctrl, bladeMods2, transformAttr='rx',
	                  attr='offsetRotationTop', sdkVal=100, reverse=1)