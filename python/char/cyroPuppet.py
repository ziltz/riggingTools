__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *
from create.rig_quadruped import *

from make.rig_tail import *

import string

'''

# puppet build
import char.cyroPuppet as charPuppet
reload(charPuppet)
charPuppet.build()

'''

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

	#biped.spine(ctrlSize=20)
	quad.spine(ctrlSize=50)

	quad.pelvis(ctrlSize=35)

	# make neck
	
	#neckModule = rig_ikChainSpline( 'neck' , 'neckJA_JNT', ctrlSize=25, parent='spineJF_JNT',
    #               numIkControls=4, numFkControls=4)

	'''
	neckName = 'neck'
	neckSize = 15
	mm.eval(
	'string $ctrls[];string $reads[];rig_makeSpline( "neck", 4, "cube", 8, 10, "joint", $ctrls, $reads, 0);')
	pm.delete(pm.parentConstraint( 'neckStart_LOC', neckName+'BaseIKOffset_GRP' ))
	pm.delete(pm.parentConstraint( 'neckMidA_LOC', neckName+'MidAIKOffset_GRP' ))
	pm.delete(pm.parentConstraint( 'neckMidB_LOC', neckName+'MidBIKOffset_GRP' ))
	pm.delete(pm.parentConstraint( 'neckEnd_LOC', neckName+'TipIKOffset_GRP' ))
	for ctrl in (neckName+'MidAIK_CTRL', neckName+'MidBIK_CTRL', neckName+'TipIK_CTRL'):
			c = pm.PyNode( ctrl )
			pm.scale(c.cv, neckSize, neckSize, neckSize )
			pm.move(c.cv, [0, 2*neckSize, 0], relative=True, worldSpace=True)
	
	neckMod = rig_tail( name='neck', rootJoint = 'neckJA_JNT',parent='spineJF_JNT',parentName='spine',spine='spineUpperCon_GRP',
							numIKCtrls= 10, numFKCtrls=10  ,  ctrlSize = 15 )
	neckMod.splinePosList = [ 'neckStart_LOC', 'neckMidA_LOC', 'neckMidB_LOC', 'neckEnd_LOC'  ]
	neckMod.make()
	pm.setAttr("neckTipIK_CTRL.space", 1)
	neckCtrls = cmds.ls('neckFK?_CTRL')
	# set to ik space
	for ctrl in neckCtrls:
		pm.setAttr(ctrl+".space", 1)
	
	pm.parent( 'neckJA_JNT', 'neckSkeleton_GRP' )
	'''

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

	#biped.switchLoc = quad.switchLoc

	biped.elbowAxis = 'ry'

	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=12)

		fingersModule = biped.hand(side, ctrlSize=4)

		shoulderModule = biped.shoulder(side, ctrlSize=10)

		biped.connectArmShoulder(side)

		if side == 'l':
			quad.switchLoc = biped.switchLoc
		# make quadruped leg 
		legModule = quad.leg(side, ctrlSize = 30)

		toesModule = quad.foot(side, ctrlSize=7)

		quad.connectLegPelvis()



	tail = rig_tail( rootJoint = 'tailJA_JNT',numIKCtrls= 8, numFKCtrls=8  ,  ctrlSize = 15 )
	tail.make()



	# make pubis and belly controls

def cyroFinish():
	print 'Finishing cyro'

	rig_quadFinalize()



	pm.setAttr("spineUpperPivot_CTRL.translateY", -30.535)
	pm.setAttr("spineUpperPivot_CTRL.translateZ", 5.384)
	#pm.setAttr("spineUpper_CTRL.stretch", 0.2)

	pm.move( 'tailUpperAim_LOCUp', 0, 1000, 0,r=True,os=True )
	pm.move('tailLowerAim_LOCUp', 0, 1000, 0, r=True, os=True)

	pm.move(pm.PyNode( 'neckTipIK_CTRL.cv[:]'), 0 , 0, -5, r=True, os=True)
	pm.move(pm.PyNode( 'neckMidBIK_CTRL.cv[:]'), 0 ,-8.5, -13, r=True, os=True)
	pm.move(pm.PyNode( 'neckMidAIK_CTRL.cv[:]'), 0 , -1 , -23, r=True, os=True)

	#pm.setAttr("neckSkeleton_GRP.inheritsTransform", 1)
	
	for s in ('l', 'r'):
		pm.setAttr("displayModulesToggleControl."+s+"_fingers", 0)
		pm.setAttr("displayModulesToggleControl."+s+"_toes", 0)

		pm.rotate(pm.PyNode(s+'_handBall_CTRL').cv, 0, 90, 0, r=True, os=True)
		pm.scale(pm.PyNode(s+'_handBall_CTRL').cv, 2, 2, 2)

		pm.parentConstraint( s+'_anklePos_JNT', s+'_toeThumbModify1_GRP' ,mo=True )