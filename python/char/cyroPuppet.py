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
	neckName = 'neck'
	mm.eval(
	'string $ctrls[];string $reads[];rig_makeSpline( "neck", 4, "cube", 8, 8, "joint", $ctrls, $reads, 0);')
	pm.delete(pm.parentConstraint( 'neckStart_LOC', neckName+'BaseIKOffset_GRP' ))
	pm.delete(pm.parentConstraint( 'neckMidA_LOC', neckName+'MidAIKOffset_GRP' ))
	pm.delete(pm.parentConstraint( 'neckMidB_LOC', neckName+'MidBIKOffset_GRP' ))
	pm.delete(pm.parentConstraint( 'neckEnd_LOC', neckName+'TipIKOffset_GRP' ))

	#biped.head(ctrlSize=5)
	
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

