__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from char.kiddoBound import rig_kiddoBiped

from make.rig_controls import *
from make.rig_ik import rig_ik

from rutils.rig_modules import rig_module
from rutils.rig_utils import *
from rutils.rig_chain import *
from rutils.rig_nodes import *
from rutils.rig_anim import *

import string

'''

import char.kiddoPuppet as ckiddo
reload(ckiddo)
ckiddo.buildKiddo()

'''

def buildKiddo():
	puppet( character='kiddo' )
	#puppet( character='kiddo', rigBound = 'C:/Users/Jerry/Documents/maya/projects/kuba/scenes/rigBound/kiddo_new_leg8.ma' )

def kiddoPrepareRig():
	print 'Prepare kiddo'

	for side in ('l_', 'r_'):
		mc.parent(side+'clavicleJA_JNT', w=True)
		mc.parent(side+'armJA_JNT', w=True)
		mc.parent(side+'legJA_JNT', w=True )
		mc.parent(side+'hipZ_JA_JNT', w=True  )
		mc.parent(side+'hipY_JA_JNT', w=True)

		mc.rename( side+'thumbJA_JNT', side+'fngThumbJA_JNT' )
		mc.rename( side+'thumbJB_JNT', side+'fngThumbJB_JNT' )
		mc.rename( side+'thumbJC_JNT', side+'fngThumbJC_JNT' )
		mc.rename(side + 'thumbJEnd_JNT', side + 'fngThumbJEnd_JNT')

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

	biped = rig_kiddoBiped()
	biped.spineConnection = 'upperWaistX_JA_JNT'
	biped.pelvisConnection = 'lowerBodyJA_JNT'
	biped.centerConnection = 'mainJA_JNT'
	biped.fngThumb = 'thumbJA_JNT'
	biped.fngIndex = 'fngIndexJA_JNT'
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
		footBall = side+'_footAimRotate_GRP'
		footProxy = side+'_footProxy_GRP'

		pm.setAttr( hipYJnt+'.rotateOrder', 2 )


		# create foot control
		foot = rig_control(side=side, name='foot', shape='box', modify=1,
		                   scale=(13, 13, 13),
		                   parentOffset=legModule.controls)

		pm.delete(pm.pointConstraint(footProxy, foot.offset))
		pm.parentConstraint(foot.con, footProxy, mo=True)

		pm.move(foot.ctrl.cv, [0, 5, 0], relative=True, objectSpace=True)

		foot.gimbal = createCtrlGimbal(foot)
		foot.pivot = createCtrlPivot(foot)

		constrainObject(foot.offset,
		                [biped.pelvisConnection, biped.centerConnection,
		                 'worldSpace_GRP'],
		                foot.ctrl, ['pelvis', 'main', 'world'],
		                type='parentConstraint')

		pm.setAttr(foot.ctrl.space, 2)

		pm.addAttr(foot.ctrl, ln='MOTION', at='enum',
		           enumName='___________',
		           k=True)
		foot.ctrl.MOTION.setLocked(True)
		pm.addAttr(foot.ctrl, longName='twist', at='float', k=True)
		pm.addAttr(foot.ctrl, longName='ankleRotate', at='float', k=True)

		pm.connectAttr(foot.ctrl.twist, footBall+'.rotateX')
		pm.connectAttr(foot.ctrl.ankleRotate, footBall+'.rotateZ')

		pm.addAttr(foot.ctrl, ln='ROLLS', at='enum',
		           enumName='___________',
		           k=True)
		foot.ctrl.ROLLS.setLocked(True)
		pm.addAttr(foot.ctrl, longName='rollTip', at='float', k=True, min=0, max=10,dv=0)
		pm.addAttr(foot.ctrl, longName='rollHeel', at='float', k=True, min=0, max=10,dv=0)
		pm.addAttr(foot.ctrl, longName='rollOut', at='float', k=True, min=0, max=10,dv=0)
		pm.addAttr(foot.ctrl, longName='rollIn', at='float', k=True, min=0, max=10,dv=0)

		rig_animDrivenKey(foot.ctrl.rollTip, (0, 10),
		                  side + '_frontPivot_GRP.rotateX', (0, 90 ))
		rig_animDrivenKey(foot.ctrl.rollHeel, (0, 10),
		                  side + '_backPivot_GRP.rotateX', (0, -90 ))
		flipRoll = 1
		if (side == 'l'):
			flipRoll = -1
		rig_animDrivenKey(foot.ctrl.rollOut, (0, 10),
		                  side + '_outerPivot_GRP.rotateZ', (0, flipRoll*90 ))
		rig_animDrivenKey(foot.ctrl.rollIn, (0, 10),
		                  side + '_innerPivot_GRP.rotateZ', (0, flipRoll*-90 ))


		#  create hip aims
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
		           dv=5)

		pm.addAttr(hipY.ctrl, longName='limitOutRotation', at='float', k=True, min=0,
		           max=10,
		           dv=0)
		pm.addAttr(hipY.ctrl, longName='limitInRotation', at='float', k=True, min=0,
		           max=10,
		           dv=0)
		hipY.ctrl.limitOutRotation.set(cb=True)
		hipY.ctrl.limitInRotation.set(cb=True)

		pm.setDrivenKeyframe(hipY.modify[0]+'.minRotYLimit' ,
		                     cd=hipY.ctrl.limitOutRotation,
		                     dv=0, v=-100 )
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
		pm.setAttr(rotCon.interpType, 2)

		# constrain shizzle
		
		legTop = rig_transform(0, name=side + '_legTop',
		                            target=legJnt, parent=legModule.skeleton).object

		pm.setAttr( legTop+'.inheritsTransform', 0 )
		pm.scaleConstraint( 'worldSpace_GRP', legTop )
		legSkeletonParts = rig_transform(0, name=side + '_legSkeletonParts',
		                                 parent=legTop).object

		pm.parent( hipAimY, hipAimZ, legModule.parts )
		pm.parent( legJnt, legSkeletonParts )
		pm.parentConstraint( hipYJnt, legTop, mo=True, skipRotate=('x','y','z') )

		heelJnt = side+'_heelRotY_JA_JNT'
		pm.delete( pm.listRelatives( heelJnt ,type="constraint" ) )
		heel = rig_control(side=side, name='heel', shape='box', modify=1,
		                   scale=(10, 2, 18),
		                   parentOffset=legModule.controls, targetOffset=heelJnt,
		                   constrain=heelJnt,
		                   lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz'],
		                   rotateOrder=0)
		if side == 'l':
			pm.parentConstraint( side+'_innerPivot_GRP'  ,heel.offset, mo=True )
		else:
			pm.parentConstraint(side + '_outerPivot_GRP', heel.offset, mo=True)

		constrainObject(heel.modify,
		                [heel.offset, 'lowerBodyJA_JNT' , 'worldSpace_GRP'],
		                heel.ctrl, ['foot','pelvis' ,'world'], type='orientConstraint', skip=['x','z'])

		toeJnt = side + '_toeJA_JNT'
		toe = rig_control(side=side, name='toe', shape='box', modify=1,
		                   scale=(6, 3, 3),
		                   parentOffset=legModule.controls, targetOffset=toeJnt,
		                   constrain=toeJnt,
		                   lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'],
		                   rotateOrder=0)
		pm.parentConstraint(heel.con, toe.offset, mo=True)
		constrainObject(toe.modify,
		                [toe.offset, 'lowerBodyJA_JNT' ,'worldSpace_GRP'],
		                toe.ctrl, ['heel', 'pelvis', 'world'], type='orientConstraint', skip=[ 'y', 'z'])


		pm.parent( heelJnt,toeJnt, legModule.skeleton )
		pm.parent(hipZJnt, legModule.skeleton)
		pm.parent(hipYJnt, legModule.skeleton)

		# simple controls
		legSidesSimpleControls(legModule, side, secColour)

		armSidesSimpleControls(armModule, side, secColour)

	# asymettrical controls
	bodySimpleControls(bodyModule)

	# wires
	kiddoWiresSetup()

	# chair rig
	kiddoChairSetup()

def kiddoFinish():
	print 'Finishing kiddo'

	# removing aim attribute temporary
	for side in ('l', 'r'):
		hip = pm.PyNode(side+'_hipYaw_CTRL')
		hip.aim.set(k=False, cb=False)

		pm.setAttr( side+"_kneeCap_CTRL.space", 1  )

		pm.setAttr(side + "_footCap_CTRL.space", 2)
		pm.setAttr(side + "_toe_CTRL.space", 2)


	#pm.setAttr( "r_footCapModify1_GRP_orientConstraint1.offsetX", 0)
	#pm.setAttr( "r_toeModify1_GRP_orientConstraint1.offsetX", 0)
	#pm.setAttr( "r_kneeCapModify1_GRP_orientConstraint1.offsetX", -180)

	globalCtrl = pm.PyNode('global_CTRL')
	pm.addAttr(globalCtrl, ln='visSettings', at='enum',
	           enumName='___________',
	           k=True)
	globalCtrl.visSettings.setLocked(True)
	pm.addAttr(globalCtrl, longName='kiddoVis', at='long',
	           k=True, min=0,
	           max=1, defaultValue=1)
	pm.addAttr(globalCtrl, longName='interiorVis', at='long',
	           k=True, min=0,
	           max=1, defaultValue=0)
	pm.addAttr(globalCtrl, longName='chairVis', at='long',
	           k=True, min=0,
	           max=1, defaultValue=0)

	pm.connectAttr( globalCtrl.kiddoVis, 'waist_grp.v' )
	pm.connectAttr( globalCtrl.kiddoVis, 'waist_gimbal_grp.v' )
	pm.connectAttr(globalCtrl.interiorVis, 'int_cockpit_grp.v')
	pm.connectAttr(globalCtrl.chairVis, 'masterChair_geo_grp.v')

	chairCtrls = pm.listRelatives('chairControls_GRP', typ='transform')
	chairControlVis = rig_transform(0, name= 'chairControlsVis').object
	pm.parent(chairControlVis, 'chairModule_GRP')
	pm.parent(  'chairControls_GRP',chairControlVis)

	for c in chairCtrls:
		try:
			pm.connectAttr(globalCtrl.chairVis, c+'.v')
		except RuntimeError:
			pass

	rig_animDrivenKey(globalCtrl.lodDisplay, (0, 1, 2),
	                  chairControlVis + '.v', (0, 1, 1 ))

	allCtrlGrps = pm.ls('*Controls_GRP')
	for grp in allCtrlGrps:
		grpName = grp.stripNamespace()
		if 'chair' not in grpName and 'belt' not in grpName:
			parent = pm.listRelatives(grp, typ='transform', p=True)[0]
			controlVis = rig_transform(0, name=grpName.replace('Controls_GRP',
			                                                        'ControlsVis_GRP')).object
			pm.parent(controlVis, parent)
			pm.parent(grp, controlVis)

			pm.connectAttr(globalCtrl.kiddoVis, controlVis+'.v')

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

	simpleControls(['l_buckleJA_JNT', 'r_backBuckleJA_JNT', 'l_backBuckleJA_JNT'], colour='white', scale=(2, 2, 2),
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
	sc = simpleControls(side + '_kneeCapJA_JNT', colour=colour,
	               modify=1, scale=(10, 10, 3),
	               parentOffset=module.controls,
	               lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])
	kneeCap = sc[side+'_kneeCapJA_JNT']
	constrainObject(kneeCap.modify,
	                [kneeCap.offset, 'lowerBodyJA_JNT', 'worldSpace_GRP'],
	                kneeCap.ctrl, ['leg', 'pelvis', 'world'], type='orientConstraint', skip=['y', 'z'])

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


	sc = simpleControls(side + '_footCapJA_JNT', colour=colour,
	                    modify=1, scale=(6,3, 3),
	                    parentOffset=module.controls,
	                    lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])
	footCap = sc[side + '_footCapJA_JNT']
	constrainObject(footCap.modify,
	                [footCap.offset, 'lowerBodyJA_JNT', 'worldSpace_GRP'],
	                footCap.ctrl, ['heel', 'pelvis', 'world'], type='orientConstraint', skip=[ 'y', 'z'])

	sc = simpleControls([side + '_toeFangsOuterJA_JNT', side+'_toeFangsInnerJA_JNT'], colour=colour,
	                    modify=1, scale=(3, 6, 3),
	                    parentOffset=module.controls,
	                    lockHideAttrs=['tx', 'rx', 'tz', 'ry', 'rz'])
	toeFangOuter = sc[side + '_toeFangsOuterJA_JNT']
	toeFangInner = sc[side + '_toeFangsInnerJA_JNT']
	if side == 'l':
		pm.transformLimits(toeFangOuter.ctrl, ty=(-5, 1.5), ety=(1, 1))
		pm.transformLimits(toeFangInner.ctrl, ty=(-5, 1.5), ety=(1, 1))
	else:
		pm.transformLimits(toeFangOuter.ctrl, ty=(-1.5, 5), ety=(1, 1))
		pm.transformLimits(toeFangInner.ctrl, ty=(-1.5, 5), ety=(1, 1))

	sc = simpleControls([side + '_toeOuterBaseJA_JNT', side + '_toeOuterJA_JNT', side+'_toeInnerBaseJA_JNT', side+'_toeInnerJA_JNT'], colour=colour,
	                    modify=1, scale=(2, 2, 2),
	                    parentOffset=module.controls,
	                    lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'])

	if side == 'l':
		sc = simpleControls('l_footFangsJA_JNT', colour=colour,
		                    modify=1, scale=(2, 1.5, 6),
		                    parentOffset=module.controls,
		                    lockHideAttrs=['tx', 'rx', 'ty ', 'ry', 'rz'])
		lFootFangs = sc['l_footFangsJA_JNT']
		pm.transformLimits(lFootFangs.ctrl, tz=(-4.7, 0.6), etz=(1, 1))


	if side == 'r':
		sc = simpleControls('r_shinJA_JNT', colour=colour, scale=(8, 3, 3),
		                    parentOffset=module.controls,
		                    lockHideAttrs=['tx', 'tz', 'ty ', 'ry', 'rz'])
		shin = sc[ 'r_shinJA_JNT']
		pm.move( shin.ctrl.cv,[0, 1.8, 6.1] ,relative=True, objectSpace=True )


	sc = simpleControls(side + '_heelPipeJA_JNT', colour=colour, scale=(7, 2, 5),
	                    parentOffset=module.controls)
	heelPipe = sc[side+'_heelPipeJA_JNT']
	heelPipe.pivot = createCtrlPivot(heelPipe, overrideScale=(5, 5, 5))


def kiddoWiresSetup():

	tubesModule = rig_module('wires')

	tubes1 = pm.ls("*Tube?JA_JNT")
	tubes2 = pm.ls("*TubeJA_JNT")

	tubes = tubes1 + tubes2

	sc = simpleControls(tubes, scale=(1,1,1),
	                    parentOffset=tubesModule.controls,
	                    lockHideAttrs=['rx', 'ry', 'rz'])


	globalCtrl = pm.PyNode('global_CTRL')
	tubeOffsets = pm.listRelatives('wiresControls_GRP', type='transform')
	for hiGrps in tubeOffsets:
		rig_animDrivenKey(globalCtrl.lodDisplay, (0.0, 1.0, 2.0),
		                  hiGrps + '.visibility', (0.0, 1.0, 1.0 ))


def kiddoChairSetup():

	print 'Start chair setup'

	chairModule = rig_module('chair')
	module = chairModule

	pm.parent( 'beltSkeleton_GRP', module.skeleton )
	pm.parent( 'beltControls_GRP', module.controls )
	pm.parent('beltParts_GRP', module.parts)

	pm.parent('chairLegJA_JNT', module.skeleton)

	# chair leg

	sc = simpleControls(['chairBaseJA_JNT'],
	                    colour='white', scale=(8,2, 4),
	                    parentOffset=module.controls)

	chairBase = sc['chairBaseJA_JNT']
	pm.parent('chairBaseJA_JNT', module.skeleton)

	pm.addAttr(chairBase.ctrl, longName='scaleChair', at='float',
	           k=True, min=0.1,
	           max=3, defaultValue=1)
	pm.connectAttr( chairBase.ctrl.scaleChair, module.top+'.scaleX' )
	pm.connectAttr(chairBase.ctrl.scaleChair, module.top + '.scaleY')
	pm.connectAttr(chairBase.ctrl.scaleChair, module.top + '.scaleZ')

	springIK = rig_ik('chairLeg', 'chairLegJA_JNT', 'chairTiltXJA_JNT', 'ikRPsolver')

	poleVector = springIK.poleVector( mid='chairLegJB_JNT', posMultiplier=2 )

	pm.parentConstraint(chairBase.con, poleVector, mo=True)

	pm.parent(springIK.handle,poleVector, module.parts)

	chairLeg = rig_control(name='chairLeg', shape='box', modify=1, scale=(5, 7, 1),
	                       lockHideAttrs=['tx'],
	                        colour='yellow', parentOffset=module.controls, rotateOrder=2)

	pm.move(chairLeg.ctrl.cv, (0, 0, 2), relative=True,
	        objectSpace=True)

	pm.delete(pm.parentConstraint( 'chairTiltXJA_JNT', chairLeg.offset ))
	pm.parentConstraint( chairBase.con, chairLeg.offset,mo=True )
	pm.parentConstraint( chairBase.con, 'chairLegJA_JNT', mo=True )
	pm.parentConstraint(chairLeg.con,springIK.handle, mo=True)

	chairTiltX = rig_control(name='chairTiltX', shape='box', modify=1, scale=(2, 2, 2),
	                       lockHideAttrs=['tx', 'ty', 'tz'],
	                       colour='yellow', parentOffset=module.controls, rotateOrder=2)

	pm.delete(pm.parentConstraint( 'chairTiltXJA_JNT',chairTiltX.offset ))
	pm.pointConstraint( chairLeg.con ,chairTiltX.offset, mo=True )
	pm.orientConstraint(chairBase.con, chairTiltX.offset, mo=True)
	pm.orientConstraint( chairTiltX.con, 'chairTiltXJA_JNT')


	sc = simpleControls(['chairPanYJA_JNT','chairRollZJA_JNT'],
	                    colour='yellow', scale=(2, 2, 2), modify=1,
	                    parentOffset=module.controls,
	                    lockHideAttrs=['tx', 'ty', 'tz'])

	pm.parent( chairTiltX.offset, sc['chairPanYJA_JNT'].offset, sc['chairRollZJA_JNT'].offset,
	           module.parts )

	pm.connectAttr( chairLeg.ctrl.rotateX, chairTiltX.ctrl.rotateX )
	pm.connectAttr( chairLeg.ctrl.rotateY, sc['chairPanYJA_JNT'].ctrl.rotateY )
	pm.connectAttr(chairLeg.ctrl.rotateZ, sc['chairRollZJA_JNT'].ctrl.rotateZ)


	constrainObject(chairLeg.modify,
	                [chairLeg.offset, 'worldSpace_GRP'],
	                chairLeg.ctrl, ['upperBody', 'world'], type='parentConstraint',
	                skipTrans=('x'), skipRot=('x','y','z'))

	#mm.eval('CBdeleteConnection "chairLegModify1_GRP.tx";')
	#mm.eval('CBdeleteConnection "chairLegModify1_GRP.rx";')
	#mm.eval('CBdeleteConnection "chairLegModify1_GRP.ry";')
	#mm.eval('CBdeleteConnection "chairLegModify1_GRP.rz";')

	constrainObject(chairTiltX.modify,
	                [chairTiltX.offset, 'worldSpace_GRP'],
	                chairLeg.ctrl, ['upperBody', 'world'], type='orientConstraint',
	                skip=('y', 'z'))

	constrainObject(sc['chairPanYJA_JNT'].modify,
	                [sc['chairPanYJA_JNT'].offset, 'worldSpace_GRP'],
	                chairLeg.ctrl, ['upperBody', 'world'], type='orientConstraint',
	                skip=('z', 'x'))

	constrainObject(sc['chairRollZJA_JNT'].modify,
	                [sc['chairRollZJA_JNT'].offset, 'worldSpace_GRP'],
	                chairLeg.ctrl, ['upperBody', 'world'], type='orientConstraint',
	                skip=('y', 'x'))

	# belt
	sc = simpleControls(['seatbeltJA_JNT'],
	                    colour='yellow', scale=(1,0.5,1),
	                    parentOffset='beltControls_GRP')

	beltMD = multiplyDivideNode('beltScale', 'multiply',
	                                         input1=['rig_GRP.worldScale', 0, 0],
	                                         input2=[ module.top.scaleX, 0, 0],
	                                         output=[])
	beltJnts = pm.listRelatives('beltSkeleton_GRP', type='joint')
	for jnt in beltJnts:
		for attr in ('X', 'Y','Z'):
			pm.connectAttr( beltMD+'.outputX', jnt+'.scale'+attr )

	# generic controls for both sides
	for side in ('l', 'r'):
		sc = simpleControls([side+'_joystickJA_JNT'], scale=(0.5, 0.8, 0.5),
		                    lockHideAttrs=['tx', 'ty', 'tz'],
		                    parentOffset=module.controls)

		sc = simpleControls([side + '_monitorBasePanYJA_JNT'],
		                    scale=(1, 1, 1),lockHideAttrs=['tx', 'ty', 'tz','rx','rz'],
		                    parentOffset=module.controls)

		sc = simpleControls([side + '_monitorBaseTiltZJA_JNT',side+'_monitorBaseRollZJA_JNT'],
		                    scale=(0.5, 0.5, 0.5), lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'ry'],
		                    parentOffset=module.controls, modify=1)

		constrainObject(sc[side+'_monitorBaseRollZJA_JNT'].modify,
		                [ 'chairRollZJA_JNT', sc[side+'_monitorBaseRollZJA_JNT'].offset],
		                sc[side+'_monitorBaseRollZJA_JNT'].ctrl, ['chair','parent'],
		                type='orientConstraint',
		                skip=('y', 'x'))


		# monitor arm translate Y
		sc = simpleControls([side + '_monitorArmJA_JNT'],
		                    scale=(0.3, 2, 0.3), lockHideAttrs=['tx', 'tz', 'rx', 'ry', 'rz'],
		                    parentOffset=module.controls)


		# rotation z monitor controls
		sc = simpleControls([side + '_monitorHeadZJA_JNT',
		                     side + '_keyboardBUpperZJA_JNT', side + '_keyboardBLowerZJA_JNT',
		                     side + '_keyboardAZJA_JNT'],
		                    scale=(0.3, 0.3, 0.3), lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'ry' ],
		                    parentOffset=module.controls)

		# rotation y monitor controls
		sc = simpleControls([side + '_monitorAPanYJA_JNT', side + '_monitorBPanYJA_JNT',
		                     side+'_keyboardBPanYJA_JNT'],
		                    scale=(0.5, 0.5, 0.5), lockHideAttrs=['tx', 'ty', 'tz', 'rx', 'rz' ],
		                    parentOffset=module.controls)

		pm.move( sc[side+'_monitorAPanYJA_JNT'].ctrl.cv,(0,0,-0.5), relative=True, objectSpace=True)
		pm.move(sc[side+'_monitorBPanYJA_JNT'].ctrl.cv, (0, 0, 0.5), relative=True,
		        objectSpace=True)

		# free rotation monitor/keyboard controls
		sc = simpleControls([side+'_keyboardBJA_JNT'],
		                    scale=(0.2, 0.2, 0.2), lockHideAttrs=['tx', 'ty', 'tz'], shape='sphere',
		                    parentOffset=module.controls)
		sc = simpleControls([ side+'_monitorBJA_JNT', side+'_monitorAJA_JNT'],
		                    scale=(0.2, 1.5, 2.0), lockHideAttrs=['tx', 'ty', 'tz'], shape='box',
		                    parentOffset=module.controls)

	# rotation z right monitor controls
	sc = simpleControls(['r_monitorATiltZJA_JNT','r_monitorBTiltZJA_JNT'],
	                    scale=(0.3, 0.3, 0.3), lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rx'],
	                    parentOffset=module.controls)
	# rotation y left monitor controls
	sc = simpleControls(['l_monitorATiltYJA_JNT', 'l_monitorBTiltYJA_JNT'],
	                    scale=(0.3, 0.3, 0.3), lockHideAttrs=['tx', 'ty', 'tz', 'rz', 'rx'],
	                    parentOffset=module.controls)

	# rotation x monitor controls
	sc = simpleControls([ 'r_monitorAntennaXJA_JNT'],
	                    scale=(0.1, 0.1, 0.1), lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'],
	                    parentOffset=module.controls)


	# chair foot rest
	sc = simpleControls(['footRestBaseJA_JNT'],
	                    scale=(1, 1, 1), lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'],
	                    parentOffset=module.controls)
	sc = simpleControls(['footRestTiltJA_JNT', 'footRestPadsJA_JNT',
	                     'l_footPadJA_JNT','r_footPadJA_JNT'],
	                    scale=(0.5, 0.5, 0.5), lockHideAttrs=['tx', 'ty', 'tz', 'ry', 'rz'],
	                    parentOffset=module.controls)

	sc = simpleControls(['footRestExtensionJA_JNT'],
	                    scale=(0.3, 0.3, 1.0), lockHideAttrs=['tx', 'ty', 'rx','ry', 'rz'],
	                    parentOffset=module.controls)


	print 'Finished chair setup'




def kiddoConstrainNewModel():
	pm.parentConstraint("r_backBuckleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|gluteus_grp|hookTether_geo_01|hookTether_geo_R_grp|Cylinder313",

	                    mo=True)
	pm.parentConstraint("l_backBuckleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|gluteus_grp|hookTether_geo_02|hookTether_geo_L_grp|Cylinder313",
	                    mo=True)
	pm.parentConstraint("r_hipPistonAB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hipPiston2_male_R_grp",
	                    mo=True)
	pm.parentConstraint("r_hipPistonAA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hipPiston2_female_R_grp",
	                    mo=True)
	pm.parentConstraint("r_hipZ_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp"
	                    "|hipJoint_R_geo",
	                    mo=True)
	pm.parentConstraint("r_hipPistonBA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hipPiston1_female_R_grp",
	                    mo=True)
	pm.parentConstraint("r_hipPistonBB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp"
	                    "|hip_R_geo|hipPiston1_male_R_grp",
	                    mo=True)
	pm.parentConstraint("r_kneeCapJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|knee_R_grp",
	                    mo=True)
	pm.parentConstraint("r_legPistonA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp"
	                    "|hip_R_grp|upperLeg_R_grp|thigh_R_grp|leg_topPiston_grp",
	                    mo=True)
	pm.parentConstraint("r_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|ankle_R_geo",
	                    mo=True)
	pm.parentConstraint("r_footCapJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|foot_R_Cap_grp",
	                    mo=True)
	pm.parentConstraint("r_toeFangsOuterJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|toe_R_r_grp|Object127",
	                    mo=True)
	pm.parentConstraint("r_toeOuterJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|toe_R_r_grp|polySurface393",
	                    mo=True)
	pm.parentConstraint("r_toeOuterBaseJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|toe_R_r_grp",
	                    mo=True)
	pm.parentConstraint("r_toeFangsInnerJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|toe_R_l_grp|Object127",
	                    mo=True)
	pm.parentConstraint("r_toeInnerJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|toe_R_l_grp|polySurface393",
	                    mo=True)
	pm.parentConstraint("r_toeInnerBaseJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp|toe_R_l_grp",
	                    mo=True)
	pm.parentConstraint("r_toeJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp|footTip_R_grp",
	                    mo=True)
	pm.parentConstraint("r_heelRotY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp"
	                    "|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp|footBase_R_grp",
	                    mo=True)
	pm.parentConstraint("r_footRotY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|foot_R_grp|footHeel_R_grp",
	                    mo=True)
	pm.parentConstraint("r_carvesBladeAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp"
	                    "|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|lowerLeg_R_geo|carvesJet_blades_R_grp|carvesJet_blades_geo_04",
	                    mo=True)
	pm.parentConstraint("r_carvesBladeBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|lowerLeg_R_geo|carvesJet_blades_R_grp|carvesJet_blades_geo_01",
	                    mo=True)
	pm.parentConstraint("r_carvesBladeCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|lowerLeg_R_geo|carvesJet_blades_R_grp|carvesJet_blades_geo_03",
	                    mo=True)
	pm.parentConstraint("r_carvesBladeDJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|lowerLeg_R_geo|carvesJet_blades_R_grp|carvesJet_blades_geo_02",
	                    mo=True)
	pm.parentConstraint("r_legPistonB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp|lowerLeg_R_geo|legBottomPiston_R_grp",
	                    mo=True)
	pm.parentConstraint("r_ankleAimJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|lowerLeg_R_grp",
	                    mo=True)
	pm.parentConstraint("r_kneeJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp",
	                    mo=True)
	pm.parentConstraint("r_legJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp",
	                    mo=True)
	pm.parentConstraint("r_hipY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp",
	                    mo=True)
	pm.parentConstraint("l_hipPistonAB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hipPiston2_male_L_grp",
	                    mo=True)
	pm.parentConstraint("l_hipPistonAA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hipPiston2_female_L_grp",
	                    mo=True)
	pm.parentConstraint("l_hipPistonBA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hipPiston1_female_L_grp",
	                    mo=True)
	pm.parentConstraint("l_hipPistonBB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_geo|hipPiston1_male_L_grp",
	                    mo=True)
	pm.parentConstraint("l_kneeCapJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|knee_L_grp",
	                    mo=True)
	pm.parentConstraint("l_legPistonA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp"
	                    "|hip_L_grp|upperLeg_L_grp|thigh_L_grp|leg_topPiston_grp",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp"
	                    "|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface503",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface508",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface509",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface510",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface511",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface521",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface522",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface523",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface524",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface504",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface525",
	                    mo=True)
	pm.parentConstraint("l_footRotX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|ankle_L_geo|polySurface513",
	                    mo=True)
	pm.parentConstraint("l_footFangsJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|foot_L_Cap_grp|footFangs_L_grp|footFangs_L_geo",
	                    mo=True)
	pm.parentConstraint("l_footCapJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp"
	                    "|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|foot_L_Cap_grp",
	                    mo=True)
	pm.parentConstraint("l_toeFangsOuterJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_l_grp|Object127",
	                    mo=True)
	pm.parentConstraint("l_toeOuterJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp"
	                    "|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_l_grp|polySurface393",
	                    mo=True)
	pm.parentConstraint("l_toeOuterBaseJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_l_grp",
	                    mo=True)
	pm.parentConstraint("l_toeFangsInnerJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_r_grp1|Object127",
	                    mo=True)
	pm.parentConstraint("l_toeInnerBaseJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_r_grp1|polySurface386",
	                    mo=True)
	pm.parentConstraint("l_toeInnerJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_r_grp1|polySurface393",
	                    mo=True)
	pm.parentConstraint("l_toeInnerBaseJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp|footTip_L_grp|toe_L_r_grp1",
	                    mo=True)
	pm.parentConstraint("l_heelRotY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp|footBase_L_grp",
	                    mo=True)
	pm.parentConstraint("l_footRotY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|foot_L_grp|footHeel_L_grp",
	                    mo=True)
	pm.parentConstraint("l_carvesBladeAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|lowerLeg_L_geo|carvesJet_blades_L_grp|carvesJet_blades_geo_04",
	                    mo=True)
	pm.parentConstraint("l_carvesBladeBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|lowerLeg_L_geo|carvesJet_blades_L_grp|carvesJet_blades_geo_01",
	                    mo=True)
	pm.parentConstraint("l_carvesBladeCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|lowerLeg_L_geo|carvesJet_blades_L_grp|carvesJet_blades_geo_03",
	                    mo=True)
	pm.parentConstraint("l_carvesBladeDJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|lowerLeg_L_geo|carvesJet_blades_L_grp|carvesJet_blades_geo_02",
	                    mo=True)
	pm.parentConstraint("l_legPistonB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp|lowerLeg_L_geo|legBottomPiston_L_grp",
	                    mo=True)
	pm.parentConstraint("l_ankleAimJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp"
	                    "|hip_L_grp|upperLeg_L_grp|lowerLeg_L_grp",
	                    mo=True)
	pm.parentConstraint("l_kneeJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp",
	                    mo=True)
	pm.parentConstraint("l_legJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp"
	                    "|hip_L_grp",
	                    mo=True)
	pm.parentConstraint("l_hipY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp",
	                    mo=True)
	pm.parentConstraint("l_hipZ_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp", mo=True)
	# pm.parentConstraint( "r_ballsJA_JNT" ,"r_balls_GRP" , mo=True)
	#pm.parentConstraint( "l_ballsJA_JNT" ,"l_balls_GRP" , mo=True)
	pm.parentConstraint("lowerBodyJA_JNT", "newModel_GRP|CHR_KIDDO_grp|waist_grp", mo=True)
	pm.parentConstraint("r_waistPistonAimB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_L_grp|waistPistons_L_female_grp",
	                    mo=True)
	pm.parentConstraint("r_waistPistonAimA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_L_grp|waistPistons_L_male_grp",
	                    mo=True)
	pm.parentConstraint("l_waistPistonAimB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_R_grp|waistPistons_R_female_grp",
	                    mo=True)
	pm.parentConstraint("l_waistPistonAimA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_R_grp|waistPistons_R_male_grp",
	                    mo=True)
	pm.parentConstraint("r_engineFlapAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_R_grp|engineExhaust_directionRot_R_grp|exhaustFlaps_R_grp|Box346",
	                    mo=True)
	pm.parentConstraint("r_engineFlapBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_R_grp|engineExhaust_directionRot_R_grp|exhaustFlaps_R_grp|Box357",
	                    mo=True)
	pm.parentConstraint("r_engineFlapCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_R_grp|engineExhaust_directionRot_R_grp|exhaustFlaps_R_grp|Box358",
	                    mo=True)
	pm.parentConstraint("r_engineSpinJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_R_grp|engineExhaust_directionRot_R_grp|polySurface1572",
	                    mo=True)
	pm.parentConstraint("r_engineJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_R_grp|engineExhaust_directionRot_R_grp",
	                    mo=True)
	pm.parentConstraint("l_engineFlapAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_L_grp|engineExhaust_directionRot_L_grp|exhaustFlaps_L_grp|Box346",
	                    mo=True)
	pm.parentConstraint("l_engineFlapBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_L_grp|engineExhaust_directionRot_L_grp|exhaustFlaps_L_grp|Box357",
	                    mo=True)
	pm.parentConstraint("l_engineFlapCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_L_grp|engineExhaust_directionRot_L_grp|exhaustFlaps_L_grp|Box358",
	                    mo=True)
	pm.parentConstraint("l_engineSpinJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_L_grp|engineExhaust_directionRot_L_grp|polySurface1572",
	                    mo=True)
	pm.parentConstraint("l_engineJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|backpackEngines_grp|enginePack_L_grp|engineExhaust_directionRot_L_grp",
	                    mo=True)
	pm.parentConstraint("topHatchJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp"
	                    "|waist_gimbal_Z_grp|upperBody_grp|hatch_grp|topHatch_grp",
	                    mo=True)
	pm.parentConstraint("securityCamJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|hatch_grp|securityCam_hatch_grp",
	                    mo=True)
	pm.parentConstraint("cockpitBottomJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|cockpit_grp|cockpitHingeBOTTOM_grp|cockpitHingeBOTTOM_PIVOT_grp",
	                    mo=True)
	pm.parentConstraint("cockpitTopJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|cockpit_grp|cockpitHingeTOP_antenna_grp|cockpitHingeTOP_PIVOT_grp",
	                    mo=True)
	pm.parentConstraint("cockpitTopJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|cockpit_grp|cockpit_doors_grp|cockpit_doorTop_grp",
	                    mo=True)
	pm.parentConstraint("cockpitBottomJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp"
	                    "|waist_gimbal_Z_grp|upperBody_grp|cockpit_grp|cockpit_doors_grp|cockpit_doorBottom_grp",
	                    mo=True)
	#pm.parentConstraint("l_buckleJA_JNT",
	 #                   "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp
	 # |waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|Rectangle011",
	  #                  mo=True)
	pm.parentConstraint("radarJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|torso_mainAntenna_grp|radar_L_grp",
	                    mo=True)
	pm.parentConstraint("missilePistonAimA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|pistonMale_geo",
	                    mo=True)
	pm.parentConstraint("missileBayFlapAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|missileDoorFlap_grp|group54|_Cylinder196",
	                    mo=True)
	pm.parentConstraint("missileBayHingeAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|missileDoorFlap_grp|group54|_Cylinder197",
	                    mo=True)
	pm.parentConstraint("missileBayAJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|missileDoorFlap_grp",
	                    mo=True)
	pm.parentConstraint("missileBayFlapBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|missileDoorFlap_grp|group55|_Cylinder196",
	                    mo=True)
	pm.parentConstraint("missileBayHingeBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|missileDoorFlap_grp|group55|_Cylinder197",
	                    mo=True)
	pm.parentConstraint("missileBayBJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|missileDoorFlap_grp",
	                    mo=True)
	pm.parentConstraint("missileBayFlapCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|missileDoorFlap_grp|group56|_Cylinder196",
	                    mo=True)
	pm.parentConstraint("missileBayHingeCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|missileDoorFlap_grp|group56|_Cylinder197",
	                    mo=True)
	pm.parentConstraint("missileBayCJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|missileDoorFlap_grp",
	                    mo=True)
	pm.parentConstraint("missileBayHingeDJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|missileDoorFlap_grp|group58|_Cylinder197",
	                    mo=True)
	pm.parentConstraint("missileBayFlapDJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|missileDoorFlap_grp|group58|_Cylinder196",
	                    mo=True)
	pm.parentConstraint("missileBayDJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|missileDoorFlap_grp",
	                    mo=True)
	pm.parentConstraint("missileBayFlapEJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|missileDoorFlap_grp|group57|_Cylinder196",
	                    mo=True)
	pm.parentConstraint("missileBayHingeEJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|missileDoorFlap_grp|group57|_Cylinder197",
	                    mo=True)
	pm.parentConstraint("missileBayEJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|missileDoorFlap_grp",
	                    mo=True)
	pm.parentConstraint("missileJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp",
	                    mo=True)
	pm.parentConstraint("missilePistonAimB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|_pistonFemale_geo",
	                    mo=True)
	pm.parentConstraint("r_shoulderBPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|piston_B_R_grp|piston_B_R_male_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderBPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|piston_B_R_grp|piston_C_R_female_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderAPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|piston_C_R_grp|piston_B_R_male_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderAPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|piston_C_R_grp|piston_B_R_female_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderCPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|piston_A_R_grp|piston_A_R_male_grp",

	                    mo=True)
	pm.parentConstraint("r_shoulderCPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|piston_A_R_grp|piston_A_R_female_grp",
	                    mo=True)
	pm.parentConstraint("r_clavicleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_roll_geo|group52|brush22Main",
	                    mo=True)
	pm.parentConstraint("r_clavicleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_roll_geo|group52|nutBolt01_geo_01",
	                    mo=True)
	pm.parentConstraint("r_bladeJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|foreArm_R_geo|bladeShield_R_grp|blade_grp",
	                    mo=True)
	pm.parentConstraint("r_gunBarrelJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|foreArm_R_geo|forearmGun_R_grp|foreArm_GunBarrel_grp",
	                    mo=True)
	pm.parentConstraint("r_thumbJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|thumb_R_01_grp|thumb_R_01_grp|thumb_R_02_grp|thumb_R_03_grp|thumb_R_03_geo",
	                    mo=True)
	pm.parentConstraint("r_thumbJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|thumb_R_01_grp|thumb_R_01_grp|thumb_R_02_grp",
	                    mo=True)
	pm.parentConstraint("r_thumbJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|thumb_R_01_grp",
	                    mo=True)
	pm.parentConstraint("r_fngIndexJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_01_R_grp|Finger1_01_R_grp|Finger1_02_R_grp|Finger1_03_R_grp|Finger1_03_R_geo",
	                    mo=True)
	pm.parentConstraint("r_fngIndexJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_01_R_grp|Finger1_01_R_grp|Finger1_02_R_grp",
	                    mo=True)
	pm.parentConstraint("r_fngIndexJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_01_R_grp|Finger1_01_R_grp",
	                    mo=True)
	pm.parentConstraint("r_fngMidJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_02_R_grp|Finger1_02_R_grp|Finger2_02_grp|Finger2_03_grp",
	                    mo=True)
	pm.parentConstraint("r_fngMidJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_02_R_grp|Finger1_02_R_grp|Finger2_02_grp",
	                    mo=True)
	pm.parentConstraint("r_fngMidJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_02_R_grp|Finger1_02_R_grp",
	                    mo=True)
	pm.parentConstraint("r_fngRingJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_03_R_grp|Finger3_01_R_grp|Finger3_02_grp|Finger3_03_grp",
	                    mo=True)
	pm.parentConstraint("r_fngRingJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_03_R_grp|Finger3_01_R_grp|Finger3_02_grp",
	                    mo=True)
	pm.parentConstraint("r_fngRingJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp|fingers_R_geo|Finger1_03_R_grp|Finger3_01_R_grp",
	                    mo=True)
	pm.parentConstraint("r_handRotYJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_TILT_Z_gro|wristJoint_ROLL_Y_grp",
	                    mo=True)
	pm.parentConstraint("r_wristAimA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo",
	                    mo=True)
	pm.parentConstraint("r_upperArmPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|tricepPiston_male_R_grp",
	                    mo=True)
	pm.parentConstraint("r_elbowJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderShieldRotXJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|shoulderUV_R_grp|shoulderShield_hinge_R_grp|shoulderShield_R_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderShieldRotYJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|shoulderUV_R_grp|shoulderShield_hinge_R_grp",
	                    mo=True)
	pm.parentConstraint("r_upperArmPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|shoulderUV_R_grp|bicep_R_grp|tricepPiston_female_grp|tricepPiston_female_geo",
	                    mo=True)
	pm.parentConstraint("r_armJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderRollX_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp",
	                    mo=True)
	pm.parentConstraint("r_shoulderRollZ_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp",
	                    mo=True)
	pm.parentConstraint("r_clavicleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp"
	                    "|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderBPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|piston_B_L_grp|piston_B_R_male_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderBPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|piston_B_L_grp|piston_C_R_female_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderAPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|piston_C_L_grp|piston_B_R_male_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderAPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|piston_C_L_grp|piston_B_R_female_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderCPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|piston_A_L_grp|piston_A_R_male_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderCPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|piston_A_L_grp|piston_A_R_female_grp",
	                    mo=True)
	pm.parentConstraint("l_clavicleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_roll_geo|group51|brush22Main",
	                    mo=True)
	pm.parentConstraint("l_clavicleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_roll_geo|group51|nutBolt01_geo_01",
	                    mo=True)
	pm.parentConstraint("l_thumbJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|thumb_L_01_grp|thumb_R_01_grp|thumb_R_02_grp|thumb_R_02_geo",
	                    mo=True)
	pm.parentConstraint("l_thumbJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|thumb_L_01_grp|thumb_R_01_grp|thumb_R_02_grp|thumb_R_03_grp",
	                    mo=True)
	pm.parentConstraint("l_thumbJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp"
	                    "|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|thumb_L_01_grp|thumb_R_01_grp",
	                    mo=True)
	pm.parentConstraint("l_fngIndexJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_01_L_grp|Finger1_01_R_grp|Finger1_02_grp|Finger1_03_grp",
	                    mo=True)
	pm.parentConstraint("l_fngIndexJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_01_L_grp|Finger1_01_R_grp|Finger1_02_grp",
	                    mo=True)
	pm.parentConstraint("l_fngIndexJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_01_L_grp|Finger1_01_R_grp",
	                    mo=True)
	pm.parentConstraint("l_fngMidJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_02_L_grp|Finger1_02_R_grp|Finger2_02_grp|Finger2_03_grp",
	                    mo=True)
	pm.parentConstraint("l_fngMidJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_02_L_grp|Finger1_02_R_grp|Finger2_02_grp",
	                    mo=True)
	pm.parentConstraint("l_fngMidJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_02_L_grp|Finger1_02_R_grp",
	                    mo=True)
	pm.parentConstraint("l_fngRingJC_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_03_L_grp|Finger3_01_L_grp|Finger3_02_L_grp|Finger3_03_L_grp",
	                    mo=True)
	pm.parentConstraint("l_fngRingJB_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_03_L_grp|Finger3_01_L_grp|Finger3_02_L_grp",
	                    mo=True)
	pm.parentConstraint("l_fngRingJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp|fingers_L_geo|Finger1_03_L_grp",
	                    mo=True)
	pm.parentConstraint("l_handRotYJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_TILT_Z_grp|wristJoint_ROLL_Y_grp",
	                    mo=True)
	pm.parentConstraint("l_wristAimA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo",
	                    mo=True)
	pm.parentConstraint("l_upperArmPistonB_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|tricepPiston_male_grp",
	                    mo=True)
	pm.parentConstraint("l_elbowJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderShieldRotXJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|shoulderUV_L_grp|shoulderShield_hinge_L_grp|shoulderShield_L_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderShieldRotYJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|shoulderUV_L_grp|shoulderShield_hinge_L_grp",
	                    mo=True)
	pm.parentConstraint("l_upperArmPistonA_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|shoulderUV_L_grp|bicep_L_grp|tricepPiston_female_grp|tricepPiston_female_geo",
	                    mo=True)
	pm.parentConstraint("l_shoulderRollY_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|shoulderUV_L_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderRollXCon_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp",
	                    mo=True)
	pm.parentConstraint("l_shoulderRollZCon_LOC",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp",
	                    mo=True)
	pm.parentConstraint("l_clavicleJA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp",
	                    mo=True)
	pm.parentConstraint("upperWaistX_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp",
	                    mo=True)
	pm.parentConstraint("upperWaistZ_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp",
	                    mo=True)
	pm.parentConstraint("upperWaistY_JA_JNT",
	                    "newModel_GRP|CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp", mo=True)



'''
select -r _polySurface1411 _polySurface1377 _polySurface1403 _polySurface1409 _polySurface1378 _polySurface1314 _polySurface1288 _polySurface1322 _polySurface1348 _polySurface1412 _polySurface1367 _polySurface1368 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_L_grp|waistPistons_L_female_grp|_polySurface1274 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_L_grp|waistPistons_L_male_grp|_polySurface1277 |CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|thigh_R_grp|brush13Main |CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hip_R_grp|hip_R_grp|upperLeg_R_grp|thigh_R_grp|brush14Main |CHR_KIDDO_grp|waist_grp|leg_R_grp|hipJoint_R_grp|hipJoint_R_geo|brush25Main |CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|thigh_L_grp|brush14Main |CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hip_L_grp|hip_L_grp|upperLeg_L_grp|thigh_L_grp|brush13Main group59a|polySurface457 group59a|polySurface454 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface976 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1006 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1007 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1008 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1009 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1012 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1010 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1040 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1041 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1042 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1043 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1044 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1045 |CHR_KIDDO_grp|waist_grp|groin_grp|balls_grp|polySurface1046 |CHR_KIDDO_grp|waist_grp|leg_L_grp|hipJoint_L_grp|hipJoint_L_geo|brush25Main polySurface3016 group60a|polySurface454 group60a|polySurface457 _polySurface2256 _polySurface2297 _polySurface2257 _polySurface2258 _polySurface2249 _polySurface2250 _polySurface2251 _polySurface2252 _polySurface2253 _polySurface2254 _polySurface2305 _polySurface2338 _polySurface2339 _polySurface2335 _polySurface2321 _polySurface2342 _polySurface2341 _polySurface2311 _polySurface2331 _torso_mainAntenna_GRP_radar_Cylinder315 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|torso_mainAntenna_grp|radar_L_grp|antennaComsBox_grp|_Box05 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|torso_mainAntenna_grp|radar_L_grp|antennaComsBox_grp|_Box08 _torso_mainAntenna_GRP_radar_Cylinder316 _cables_geo _polySurface2627 _polySurface2628 _polySurface2629 _polySurface2634 _polySurface2635 _polySurface2636 _polySurface2637 _polySurface2643 _polySurface2644 _polySurface2630 _polySurface2647 _polySurface2631 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|pistonMale_geo|_Object131 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|_Box28 _polySurface2605 _polySurface2604 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|_Box208 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|box_01|_polySurface2427 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|box_01|_polySurface2428 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|box_02|_polySurface2427 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|box_02|_polySurface2428 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|box_03|_polySurface2427 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|box_03|_polySurface2428 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|frame_01|_polySurface2419 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|frame_01|_polySurface2426 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|frame_01|_polySurface2422 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|missileDoorFlap_grp|_Line366 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|missileDoorFlap_grp|group54|_Cylinder196 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_01_grp|missileDoorFlap_grp|group54|_Cylinder197 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|frame_01|_polySurface2419 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|frame_01|_polySurface2426 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|frame_01|_polySurface2422 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|missileDoorFlap_grp|_Line366 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|missileDoorFlap_grp|group55|_Cylinder196 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_02_grp|missileDoorFlap_grp|group55|_Cylinder197 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|frame_01|_polySurface2419 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|frame_01|_polySurface2426 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|frame_01|_polySurface2422 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|missileDoorFlap_grp|_Line366 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|missileDoorFlap_grp|group56|_Cylinder196 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_03_grp|missileDoorFlap_grp|group56|_Cylinder197 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|_Object125 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|missileDoorFlap_grp|_Line366 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|missileDoorFlap_grp|group58|_Cylinder197 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_04_grp|missileDoorFlap_grp|group58|_Cylinder196 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|_Object125 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|missileDoorFlap_grp|_Line366 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|missileDoorFlap_grp|group57|_Cylinder196 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|missileBay_05_grp|missileDoorFlap_grp|group57|_Cylinder197 _polySurface2626 _polySurface2624 _polySurface2539 _polySurface2516 _polySurface2515 _polySurface2469 _polySurface2586 _polySurface2579 _polySurface2540 _polySurface2541 _polySurface2578 _polySurface2445 _polySurface2430 _polySurface2429 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_L_grp|waistPistons_L_male_grp|_polySurface1276 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_R_grp|waistPistons_R_female_grp|_polySurface1274 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_R_grp|waistPistons_R_male_grp|_polySurface1277 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|waist_gimbal_Z_grp|waistPistons_grp|waistPiston_R_grp|waistPistons_R_male_grp|_polySurface1276 _polySurface1374 _polySurface1420 _polySurface1431 _polySurface1430 _polySurface1426 _polySurface1423 _polySurface1432 _polySurface1437 _polySurface1438 _polySurface1439 _polySurface1429 _polySurface1433 _polySurface1436 _polySurface1425 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|underbelly_grp|underbellyBack_geo|_polyMesh24 _polySurface1782 _polySurface1783 _polySurface1784 _polySurface1785 _polySurface1770 _polySurface1775 _polySurface1777 _polySurface1778 _polySurface1746 _polySurface1749 _polySurface1752 _polySurface1776 _polySurface1747 _polySurface1748 _polySurface1780 _polySurface1779 _polySurface1740 _polySurface1736 _polySurface1742 _polySurface1758 _polySurface1759 _polySurface1764 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|_Line405 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|_Rectangle011 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|_Spring05 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|_Spring06 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|_Box349 _polySurface1828 _polySurface1833 _polySurface1841 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|Box352|_Cylinder305 _polySurface1842 _polySurface1844 _polySurface1845 _polySurface1847 _polySurface1848 _polySurface1849 _polySurface1850 _polySurface1851 _polySurface1852 _polySurface1860 _polySurface1888 _polySurface1904 _polySurface1911 _polySurface1933 _polySurface1922 _polySurface1881 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp|group41|_polySurface1931 _polySurface1870 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp|group41|_polySurface1920 _polySurface1916 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp|_polySurface1923 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp|_polySurface1934 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|lights_grp|lightBox_L_grp|_polySurface1861 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|lights_grp|lightBox_L_grp|_polySurface1864 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|lights_grp|lightBox_L_grp|group40|_polySurface1865 _polySurface3006 _polySurface3008 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|lights_grp|lightBox_R_grp|_polySurface1861 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|lights_grp|lightBox_R_grp|_polySurface1864 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|lights_grp|lightBox_R_grp|group40|_polySurface1865 _polySurface3005 _polySurface3007 _polySurface1867 _polySurface1868 _polySurface1869 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp1|group41|_polySurface1931 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp1|group41|_polySurface1920 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp1|_polySurface1923 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|chinWinch_grp|rollersHooks_grp1|_polySurface1934 _polySurface2244 _polySurface2243 _polySurface2248 _polySurface2245 _polySurface2298 _polySurface2303 _polySurface2299 _polySurface2255 _polySurface2464 _polySurface2465 _polySurface2466 _blades_geo |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_01|_polySurface2587 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_01|_Object121 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_01|_polySurface2594 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_01|_polySurface2603 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_02|_polySurface2587 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_02|_Object121 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_02|_polySurface2594 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_02|_polySurface2603 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_03|_polySurface2587 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_03|_Object121 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_03|_polySurface2594 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|missileLauch_TILT_grp|backBox_geo_03|_polySurface2603 _brush9Main _brush8Main _brush7Main _polySurface2616 _polySurface2606 _polySurface2617 _polySurface2608 _missileLauch_GRP_Dummy68_Object118_Object134 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missileLauch_grp|_pistonFemale_geo _polySurface2343 _polySurface2347 _polySurface2370 _polySurface2373 _polySurface2385 _polySurface2398 _polySurface2401 _polySurface2393 _polySurface2372 _polySurface2378 _polySurface2344 _polySurface2377 _polySurface2350 _polySurface2352 _polySurface2402 _polySurface2403 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|missileLauch_grp|missleBase_grp|_polyMesh27 _polySurface2404 _polySurface2415 _polySurface2406 _polySurface2418 _polySurface2416 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_roll_geo|group52|brush19Main |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_roll_geo|group52|brush20Main brush12Main |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|foreArm_R_geo|polySurface3000 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|forearmElbow_R_grp|wristJoint_R_geo|wristJoint_PAN_X_gro|wristJoint_PAN_X_geo |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_R_grp|arm_R_Clavicle_grp|shoulderJoint_A_R_grp|shoulderJoint_B_R_roll_grp|shoulderJoint_B_R_tilt_grp|upperArm_R_grp|shoulderUV_R_grp|bicep_R_grp|tricepPiston_female_grp|tricepPiston_female_geo|brush24Main |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_roll_geo|group51|brush20Main |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_roll_geo|group51|brush19Main |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|foreArm_L_geo|polySurface3000 |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|wristJoint_L_geo|wristJoint_PAN_X_grp|wristJoint_PAN_X_geo |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|forearmElbow_L_grp|forearmShield_L_grp|brush18Main |CHR_KIDDO_grp|waist_gimbal_grp|waist_gimbal_Y_grp|waist_gimbal_Z_grp|upperBody_grp|arm_L_grp|arm_L_Clavicle_grp|shoulderJoint_A_L_grp|shoulderJoint_B_L_roll_grp|shoulderJoint_B_L_tilt_grp|upperArm_L_grp|shoulderUV_L_grp|bicep_L_grp|tricepPiston_female_grp|tricepPiston_female_geo|brush24Main ;

'''