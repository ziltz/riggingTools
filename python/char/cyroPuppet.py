__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *
from create.rig_quadruped import *

from make.rig_tail import *
from make.rig_controls import *

import string

'''

# puppet build
import char.cyroPuppet as charPuppet
reload(charPuppet)
charPuppet.build()

charPuppet.buildScene()

'''

def buildScene():
	puppet( character='cyro',buildInScene=1 )

def build():
	puppet( character='cyro' )
	#puppet( character='cyro', rigBound = 'C:/Users/Jerry/Documents/maya/projects/cyro/scenes/rigBound/cyro_new_leg8.ma' )


def cyroPrepareRig():
	print 'Prepare cyro'

	#rig_transform(0, name='headJAWorld', target='headJALocal_GRP')
	#rig_transform(0, name='headShapeWorld', target='headJALocal_GRP')

	rig_quadPrepare()


def cyroRigModules():
	print 'Create cyro rig modules'

	biped = rig_biped()
	quad = rig_quadruped()

	quad.spine(ctrlSize=50)

	quad.pelvis(ctrlSize=35)

	neckMod = quad.neck(ctrlSize=15, splinePosList=[ 'neckStart_LOC', 'neckMidA_LOC', 'neckMidB_LOC', 'neckEnd_LOC'  ])

	headMod = quad.head(ctrlSize=35)

	# jaw control
	jawControl = rig_control(name='jaw', shape='circle', scale=(25,25,25),
	                         lockHideAttrs=['rx'],
	                         parentOffset=headMod.controls, colour='white')

	pm.rotate(jawControl.ctrl.cv, -90, 0, 0, r=True, os=True)
	pm.move(jawControl.ctrl.cv, 2, 0, 0, r=True, os=True)

	pm.delete(pm.parentConstraint( 'jawJA_JNT' ,jawControl.offset))
	pm.parentConstraint('headJA_JNT', jawControl.offset, mo=True)
	pm.parentConstraint(jawControl.con, 'jawJA_JNT', mo=True)
	jawPos = pm.xform('jawJA_JNT', translation=True, query=True, ws=True)
	jawEndPos = pm.xform( 'jawJEnd_JNT', translation=True, query=True, ws=True)
	jawLength = lengthVector(jawPos, jawEndPos)
	pm.move(pm.PyNode(jawControl.ctrl + '.cv[:]'), jawLength/2,0, 0, r=True, os=True)

	
	biped.spineFullBodyCtrl = quad.spineFullBodyCtrl
	biped.spineUpperCtrl = quad.spineUpperCtrl
	biped.spineLowerCtrl = quad.spineLowerCtrl

	biped.pelvisControl = quad.pelvisControl

	biped.elbowAxis = 'ry'
	
	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=12)

		fingersModule = biped.hand(side, ctrlSize=4, baseLimit=1)

		shoulderModule = biped.shoulder(side, ctrlSize=10)

		biped.connectArmShoulder(side)

		cyroShoulderUpgrade(side=side, ctrlSize=10)

		if side == 'l':
			quad.switchLoc = biped.switchLoc
		
		# make quadruped leg 
		legModule = quad.leg(side, ctrlSize = 30)

		toesModule = quad.foot(side, ctrlSize=7, baseLimit=1)

		quad.connectLegPelvis()



	tail = rig_tail( rootJoint = 'tailJA_JNT',numIKCtrls= 8, numFKCtrls=8  ,  ctrlSize = 15 )
	tail.make()

	pubisControl = rig_control(name='pubis', shape='box', scale=(25,25,25),
	                         parentOffset='spineControlsSecondary_GRP', colour='white')
	pm.delete(pm.parentConstraint( 'pubisJA_JNT' ,pubisControl.offset))
	pm.parentConstraint('pelvisJA_JNT', pubisControl.offset, mo=True)
	pm.parentConstraint(pubisControl.con, 'pubisJA_JNT', mo=True)

	pm.move(pubisControl.ctrl.cv, 36, 0, 0, r=True, os=True)
	pm.scale(pubisControl.ctrl.cv, 1, 0.5 ,1 )

	# belly controls

def cyroFinish():
	print 'Finishing cyro'

	rig_quadFinalize()

	pm.setAttr("neckFocus_CTRL.focusNeck", 0.75)

	pm.setAttr("spineUpperPivot_CTRL.translateY", -17.164)
	pm.setAttr("spineUpperPivot_CTRL.translateZ", 1.81)
	pm.setAttr("spineUpper_CTRL.stretch", 0.2)

	pm.move( 'tailUpperAim_LOCUp', 0, 1000, 0,r=True,os=True )
	pm.move('tailLowerAim_LOCUp', 0, 1000, 0, r=True, os=True)

	pm.move(pm.PyNode( 'neckTipIK_CTRL.cv[:]'), 0 , 0, -5, r=True, os=True)
	pm.move(pm.PyNode( 'neckMidBIK_CTRL.cv[:]'), 0 ,-8.5, -13, r=True, os=True)
	pm.move(pm.PyNode( 'neckMidAIK_CTRL.cv[:]'), 0 , -1 , -23, r=True, os=True)
	
	controlSet = pm.PyNode('cyroRigPuppetControlSet')
	for s in ('l', 'r'):
		pm.setAttr("displayModulesToggleControl."+s+"_fingers", 0)
		pm.setAttr("displayModulesToggleControl."+s+"_toes", 0)

		pm.setAttr(s+"_armPV_CTRL.space", 1)
		#pm.setAttr(s+"_shoulder_CTRL.followArm", 1)

		pm.rotate(pm.PyNode(s+'_handBall_CTRL').cv, 0, 90, 0, r=True, os=True)
		pm.scale(pm.PyNode(s+'_handBall_CTRL').cv, 2, 2, 2)

		pm.parentConstraint( s+'_anklePos_JNT', s+'_toeThumbModify1_GRP' ,mo=True )

		controlSet.removeMembers([ s+'_shoulder_CTRL' ])

	hiDeltaMush = mm.eval('rig_returnDeformers("skin_C_body_GV", "deltaMush")')
	if len(hiDeltaMush) > 0:
		cNode = conditionNode( 'hiDeltaMush', 'equal', ('',0), ('', 2), ('', 1), ('', 0) )
		pm.connectAttr( "global_CTRL.lodDisplay", cNode+'.secondTerm')
		pm.connectAttr( cNode+'.outColorR', hiDeltaMush[0]+'.envelope')
	
	pm.delete('combineSkinningCut_GEO')

	'''
	select -r curveShape68.cv[1:2] curveShape68.cv[6:7] curveShape68.cv[12:15] curveShape69.cv[1:2] curveShape69.cv[6:7] curveShape69.cv[12:15] ;
move -r -os -wd 0 9.132614 0.639246 ;
select -r curveShape67.cv[1:2] curveShape67.cv[6:7] curveShape67.cv[12:15] ;
move -r -os -wd 0 12.489067 4.494289 ;
	'''


def cyroShoulderUpgrade(side='', ctrlSize=1):
	name = side+'_quadShoulder'

	module = rig_module(name)

	ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
	ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

	shoulderControl = rig_control( side=side, name='quadShoulder', shape='pyramid',
		                            targetOffset=side+'_clavicleJA_JNT', modify=1,
		                            parentOffset=module.controls,lockHideAttrs=[
				'rx','ry','rz'], scale =ctrlSize, rotateOrder=0 )

	clavPos = pm.xform(side+'_clavicleJA_JNT', translation=True, query=True, ws=True)
	armPos = pm.xform(side+'_scapulaJA_JNT', translation=True, query=True, ws=True)
	clavLength = lengthVector( armPos, clavPos )
	if side == 'l':
		pm.move( pm.PyNode( shoulderControl.offset ), clavLength,0,0, r=True,
		         os=True )
	else:
		pm.move(pm.PyNode(shoulderControl.offset), -1*clavLength, 0, 0, r=True,
		        os=True)
	pm.rotate( pm.PyNode( shoulderControl.offset ), 0,0,-90, r=True, os=True )
	

	pm.parentConstraint( 'spineJF_JNT', shoulderControl.offset, mo=True )

	clavicleAim = rig_transform(0, name=side + '_clavicleAim', type='locator',
		                            parent=module.parts, target=side+'_clavicleJA_JNT').object
	armAim = rig_transform(0, name=side + '_quadShoulderAim', type='locator',
	                        parent=module.parts).object


	pm.pointConstraint( 'spineJF_JNT', clavicleAim,mo=True )
	pm.pointConstraint( shoulderControl.con, armAim )

	quadShoulderAimTop = mm.eval('rig_makePiston("'+clavicleAim+'", "'+armAim+'", "'+side+'_quadShoulderAim");')


	#pm.orientConstraint( clavicleAim, side+'_shoulder_CTRL', mo=True )
	
	pm.delete(pm.listRelatives(side+'_shoulderOffset_GRP', type='constraint'))
	pm.parentConstraint( clavicleAim, side+'_shoulderOffset_GRP', mo=True )

	pm.addAttr(shoulderControl.ctrl, longName='followArm',
				           at='float', k=True, min=0,
				           max=10, defaultValue=1)

	pm.connectAttr( shoulderControl.ctrl.followArm, side+'_shoulder_CTRL.followArm'  )

	baseLimit = 15
	pm.transformLimits(shoulderControl.ctrl, tx=(-1 * baseLimit, baseLimit), etx=(1, 1))
	pm.transformLimits(shoulderControl.ctrl, ty=(-1 * baseLimit, baseLimit), ety=(1, 1))
	pm.transformLimits(shoulderControl.ctrl, tz=(-1 * baseLimit, baseLimit), etz=(1, 1))

	scapulaControl = rig_control( side=side, name='quadScapula', shape='box',
		                            targetOffset=side+'_scapulaJEnd_JNT', modify=1,
		                            parentOffset=module.controls,lockHideAttrs=[
				'rx','ry','rz'], scale =ctrlSize, rotateOrder=0 )

	pm.delete( pm.orientConstraint( side+'_scapulaJA_JNT', scapulaControl.offset ) )


	scapulaAim = rig_transform(0, name=side + '_quadScapulaAim', type='locator',
		                            parent=module.parts).object
	scapulaEndAim = rig_transform(0, name=side + '_quadScapulaEndAim', type='locator',
	                        parent=module.parts).object

	pm.delete( pm.parentConstraint(side+'_scapulaJA_JNT', scapulaAim ) )
	pm.pointConstraint( side+'_clavicleJA_JNT', scapulaAim,mo=True )
	pm.pointConstraint( scapulaControl.con, scapulaEndAim )
	pm.delete( pm.orientConstraint( side+'_scapulaJA_JNT', scapulaEndAim ) )

	quadScapulaAimTop = mm.eval('rig_makePiston("'+scapulaAim+'", "'+scapulaEndAim+'", "'+side+'_quadScapulaAim");')

	#pm.parentConstraint( side+'_clavicleJA_JNT', 'spineJE_JNT', scapulaControl.offset, mo=True )

	constrainObject(  scapulaControl.offset,
                [side+'_clavicleJA_JNT','spineJE_JNT'], '', [],
                 type='parentConstraint', doSpace=0, setVal=(0.5,1))

	baseLimit = 5
	pm.transformLimits(scapulaControl.ctrl, tx=(-1 * baseLimit, baseLimit), etx=(1, 1))
	pm.transformLimits(scapulaControl.ctrl, ty=(-1 * baseLimit, baseLimit), ety=(1, 1))
	pm.transformLimits(scapulaControl.ctrl, tz=(-1 * baseLimit, baseLimit), etz=(1, 1))


	pm.orientConstraint( scapulaAim, side+'_scapulaJA_JNT', mo=True )

	pm.hide(side+'_shoulderOffset_GRP')

	pm.parent( quadShoulderAimTop, quadScapulaAimTop, module.parts )


	


