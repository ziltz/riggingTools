__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *
from create.rig_skeleton import *
from create.rig_facial import *

from make.rig_controls import *
from make.rig_ik import rig_ik

from rutils.rig_modules import rig_module
from rutils.rig_utils import *
from rutils.rig_chain import *
from rutils.rig_nodes import *
from rutils.rig_anim import *
from rutils.rig_transform import rig_transform

import string

'''

import char.gizmoPuppet as char
char.buildGizmo()

'''

def buildGizmo():
	puppet( character='gizmo' )
	#puppet( character='gizmo', rigBound = 'C:/Users/Jerry/Documents/maya/projects/kuba/scenes/rigBound/gizmo_new_leg8.ma' )


def gizmoPrepareRig():
	print 'Prepare gizmo'

	rig_transform(0, name='headJAWorld', target='headJALocal_GRP')
	rig_transform(0, name='headShapeWorld', target='headJALocal_GRP')

	rig_bipedPrepare()


def gizmoRigModules():
	print 'Create gizmo rig modules'

	biped = rig_biped()
	biped.elbowAxis = 'ry'

	biped.spine(ctrlSize=6)

	biped.pelvis(ctrlSize=5)

	biped.neck( ctrlSize=2.5 )

	biped.head(ctrlSize=5)

	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=3)

		fingersModule = biped.hand(side, ctrlSize=0.5)

		shoulderModule = biped.shoulder(side, ctrlSize=2)

		biped.connectArmShoulder(side)

		legModule = biped.leg(side, ctrlSize=3)

		toesModule = biped.foot(side, ctrlSize=0.5)

		biped.connectLegPelvis()


	# make tail
	'''
	tailModule = rig_ikChainSpline('tail', 'tailJA_JNT', ctrlSize=1, parent='pelvisJA_JNT',
	                               numIkControls=4, numFkControls=4)

	chainList = rig_chain('tailJOTip_JNT').chain
	print '====== MAKING TAIL TIP =============='
	fkCtrls = fkControlChain(chainList, modify=1, scale=[1, 1, 1], directCon=1)
	for fk in fkCtrls:
		pm.parent(fk.offset, tailModule.controls)
	'''

	tailModule = rig_ikChainSpline('tail', 'tailHiJA_JNT', ctrlSize=1, parent='pelvisJA_JNT',
	                               numIkControls=12, numFkControls=12)


	# tail upgrade
	tailJnts = pm.listRelatives( 'tailskeleton_GRP', type='joint')
	for i in range (1, len(tailJnts)):
		tailNme = tailJnts[i].stripNamespace()
		tailIK = tailJnts[i]
		tailFK = tailNme.replace('IK', 'FK')
		tailFK = tailFK.replace('_JNT', '')

		constrainObject(tailFK+'Modify2_GRP',
		                [tailIK ,tailFK+'Modify1_GRP'],
		                tailFK+'_CTRL', ['IK', 'parent'], type='parentConstraint')

	pm.parentConstraint( 'tailFKACon_GRP', 'tailBaseIKOffset_GRP', mo=True )

	constrainObject(  'tailMidAIKOffset_GRP',
	                ['tailFKACon_GRP','pelvisCon_GRP', 'worldSpace_GRP'],
	                 'tailMidAIK_CTRL', ['base', 'pelvis', 'world'],
	                 type='parentConstraint')

	constrainObject('tailMidBIKOffset_GRP',
	                ['tailFKACon_GRP', 'tailMidAIKCon_GRP' , 'pelvisCon_GRP', 'worldSpace_GRP'],
	                'tailMidBIK_CTRL', ['base','FK', 'pelvis', 'world'],
	                type='parentConstraint')

	constrainObject('tailTipIKOffset_GRP',
	                ['tailFKACon_GRP', 'tailMidBIKCon_GRP', 'pelvisCon_GRP', 'worldSpace_GRP'],
	                'tailTipIK_CTRL', ['base', 'FK', 'pelvis', 'world'],
	                type='parentConstraint')

	tailPointer = rig_control(name='tailPointer', shape='pyramid',
	                            scale=(1,2,1), lockHideAttrs=['rx', 'ry', 'rz'],
	                            colour='white', parentOffset=tailModule.controls, rotateOrder=2)
	pm.delete(pm.parentConstraint('tailHiJEnd_JNT', tailPointer.offset ))
	constrainObject(tailPointer.offset,
	                ['pelvisCon_GRP', 'spineFullBodyCon_GRP', 'worldSpace_GRP'],
	                tailPointer.ctrl, ['pelvis', 'fullBody', 'world'], type='parentConstraint')

	tailPointerBase = rig_transform(0, name='tailPointerBase', type='locator',
	                        parent=tailModule.parts, target='tailFKA_CTRL').object
	tailPointerTip = rig_transform(0, name='tailPointerTip', type='locator',
	                        parent=tailModule.parts, target=tailPointer.con).object

	pm.rotate(tailPointerBase, 0, 0, -90, r=True, os=True)
	pm.rotate(tailPointerTip, 0, 0, -90, r=True, os=True)

	pm.parentConstraint('pelvisCon_GRP', tailPointerBase, mo=True)
	pm.parentConstraint(tailPointer.con, tailPointerTip, mo=True)

	tailPointerTop = mm.eval(
		'rig_makePiston("' + tailPointerBase + '", "' + tailPointerTip + '", "tailPointerAim");')

	pm.orientConstraint( tailPointerBase.replace('LOC','JNT'), 'tailFKAModify2_GRP', mo=True )

	pm.parent('tailMidAIKOffset_GRP', 'tailMidBIKOffset_GRP','tailTipIKOffset_GRP',
	          tailModule.controls)
	pm.parent(tailJnts, tailModule.skeleton)
	pm.parent('tail_cMUS','tailBaseIKOffset_GRP',tailPointerTop, tailModule.parts)

	pm.setAttr( tailModule.skeleton+'.inheritsTransform', 0 )


	# build facial

	facialModule = rig_module('facial')
	pm.parent(facialModule.top, 'rigModules_GRP')

	# build shape locators

	for side in ['l', 'r']:
		muzzleCtrl = fourWayShapeControl(side+'_muzzleShape_LOC', (side+'MuzzleUp',
		                                                          side+'MuzzleDown',
		                                              side+'MuzzleForward', side+'MuzzleBack'),
		                    'headShapeWorld_GRP', ctrlSize=1)

		pm.rotate(muzzleCtrl.ctrl.cv, 0, 0, 90,r=True, os=True)
		pm.rotate(muzzleCtrl.ctrl.cv, -45, 0, 0,r=True, os=True)

		browCtrl = twoWayShapeControl(side + '_browShape_LOC', (side + 'BrowUp', side + 'BrowDown'),
		                    'headShapeWorld_GRP', ctrlSize=0.8)

		pm.rotate(browCtrl.ctrl.cv, 90, 0, 0,r=True, os=True)
		pm.rotate(browCtrl.ctrl.cv, 0, -75, 0,r=True, os=True)

		blinkCtrl = oneWayShapeControl(side + '_blinkShape_LOC', side+'Blink',
		                   'headShapeWorld_GRP', ctrlSize=0.5)

		if side == 'r':
			pm.rotate(blinkCtrl.ctrl.cv, 0, 0, 180,r=True, os=True)
			#pm.move(blinkCtrl.ctrl.cv, 0, -0.4, 0, relative=True)

		#pm.parent( muzzleCtrl.offset, browCtrl.offset , blinkCtrl.offset ,facialModule.controls)

	pm.parent('headShapeWorld_GRP', facialModule.controls)
	pm.parentConstraint('headJA_JNT', 'headShapeWorld_GRP')

	# build simple controllers
	facialLocalWorldControllers(facialModule, 'headJAWorld_GRP', ctrlSize=0.1)

	pm.parentConstraint( 'headJA_JNT', 'headJAWorld_GRP' )

	pm.parent( 'headJAWorld_GRP', facialModule.controlsSec )

	pm.move(pm.PyNode('noseTwk_CTRL').cv, 0.15, 0, 0, r=True, os=True)
	pm.scale(pm.PyNode('noseTwk_CTRL').cv, 2.5, 2.5, 2.5)

	# jaw control
	jawControl = rig_control(name='jaw', shape='circle', scale=(2,2,2),
	                         lockHideAttrs=['rx'],
	                         parentOffset=facialModule.controls, colour='white')

	pm.rotate(jawControl.ctrl.cv, -90, 0, 0, r=True, os=True)
	pm.move(jawControl.ctrl.cv, 2, 0, 0, r=True, os=True)

	pm.delete(pm.parentConstraint( 'jawJA_JNT' ,jawControl.offset))
	pm.parentConstraint('headJA_JNT', jawControl.offset, mo=True)

	pm.parent( 'jawHeadOffset_LOC', jawControl.offset )
	pm.pointConstraint( jawControl.con, 'jawHeadOffset_LOC',mo=True )

	facialLoc = 'facialShapeDriver_LOC'

	rig_animDrivenKey(jawControl.ctrl.rotateY, (0, 35), facialLoc + '.jawOpen' , (0, 1))
	rig_animDrivenKey(jawControl.ctrl.rotateY, (0, -5), facialLoc + '.jawClosed', (0, 1))
	rig_animDrivenKey(jawControl.ctrl.rotateZ, (0, -10), facialLoc + '.rJawSide' , (0, 1))
	rig_animDrivenKey(jawControl.ctrl.rotateZ, (0, 10), facialLoc + '.lJawSide' , (0, 1))

	pm.transformLimits(jawControl.ctrl, ry=(-5, 35), ery=(1, 1))
	pm.transformLimits(jawControl.ctrl, rz=(-10, 10), erz=(1, 1))
	pm.transformLimits(jawControl.ctrl, tx=(-0.1, 0.1), etx=(1, 1))
	pm.transformLimits(jawControl.ctrl, ty=(-0.1, 0.1), ety=(1, 1))
	pm.transformLimits(jawControl.ctrl, tz=(0, 0.1), etz=(1, 1))

	upperLipCtrls = pm.ls("*upperLip*Twk*CTRL")
	for c in upperLipCtrls:
		pm.scale(c.cv, 0.6, 0.6, 0.6, r=True)
		pm.move(c.cv, 0, 0, 0.3, r=True)
		pm.move(c.cv, 0, 0.1, 0, r=True)

	lowerLipCtrls = pm.ls("*lowerLip*Twk*CTRL")
	for c in lowerLipCtrls:
		pm.scale(c.cv, 0.6, 0.6, 0.6, r=True)
		pm.move(c.cv, 0, 0, 0.3, r=True)
		pm.move(c.cv, 0, -0.1, 0, r=True)

	pm.setAttr( facialModule.parts+'.inheritsTransform', 0)

	pm.parent('tongueControls_GRP', facialModule.controls)

	# eye controls

	eyeModule = rig_module('eye')
	pm.parent(eyeModule.top, 'rigModules_GRP')

	eyeControl = rig_control(name='eye', shape='circle', modify=1,
	                         parentOffset=eyeModule.controls, scale=(1, 1, 1),
	                         rotateOrder=2, lockHideAttrs=['rx', 'ry', 'rz'])

	pm.delete(pm.parentConstraint(  'eyeAim_LOC' ,eyeControl.offset ))
	#pm.parentConstraint( 'headCon_GRP', eyeControl.offset, mo=True )

	pm.rotate(eyeControl.ctrl.cv, 90, 0, 0, r=True, os=True)

	pm.select(eyeControl.ctrl.cv[1], r=True )
	pm.select(eyeControl.ctrl.cv[5], add=True )
	pm.scale( 0,0 , 0, r=True)

	constrainObject(eyeControl.offset,
	                ['headCon_GRP', 'worldSpace_GRP'],
	                eyeControl.ctrl, ['head', 'world'],
	                type='parentConstraint')

	pm.parent( 'eyeAim_LOC', eyeControl.con )
	pm.hide('eyeAim_LOC')

	for side in ('l', 'r'):
		eyeBase = rig_transform(0, name=side + '_eyeBase', type='locator',
		                          target=side+'_eyeJA_JNT', parent=eyeModule.parts).object
		eyeTarget = rig_transform(0, name=side + '_eyeTarget', type='locator',
		                        target='eyeAim_LOC', parent=eyeModule.parts).object

		pm.parentConstraint('headJA_JNT', eyeBase, mo=True)
		pm.parentConstraint('eyeAim_LOC', eyeTarget, mo=True)

		eyeAimTop = mm.eval('rig_makePiston("' + eyeBase + '", "' + eyeTarget + '", '
		                                                                             '"' + side +
		                         '_eyeAim");')

		pm.orientConstraint( side+'_eyeBase_JNT', side+'_eyeJA_JNT', mo=True )

		pm.parent(eyeAimTop, eyeModule.parts)

		'''
		eyeControl = rig_control(side=side, name='eye', shape='circle', modify=1,
		                             parentOffset=eyeModule.controls, scale=(1,1,1),
		                             rotateOrder=2, lockHideAttrs=['rx', 'ry', 'rz'])
		'''




def gizmoFinish():
	print 'Finishing gizmo'

	rig_bipedFinalize()

	#pm.setAttr( "tailJLTip_JNT.inheritsTransform", 0 )
	pm.setAttr("spineUpper_CTRL.stretch", 0.2)

	for s in ('l', 'r'):
		pm.setAttr("displayModulesToggleControl."+s+"_fingers", 0)
		pm.setAttr("displayModulesToggleControl."+s+"_toes", 0)


	globalCtrl = pm.PyNode('global_CTRL')
	for hiGrps in ('headJAWorld_GRP', 'headShapeWorld_GRP', 'jawOffset_GRP', 'tongueControls_GRP' ):
		rig_animDrivenKey(globalCtrl.lodDisplay, (0.0, 1.0, 2.0),
		                  hiGrps+ '.visibility', (0.0, 0.0, 1.0 ))

	pm.delete('shapeLocs_GRP')

