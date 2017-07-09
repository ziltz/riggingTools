__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *
from create.rig_skeleton import *

from make.rig_controls import *
from make.rig_ik import rig_ik

from rutils.rig_modules import rig_module
from rutils.rig_utils import *
from rutils.rig_chain import *
from rutils.rig_nodes import *
from rutils.rig_anim import *

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

	rig_bipedPrepare()

	#mc.delete('tailJO_JNT')
	#loadPose('tailJLTip_JNT', 'tPose')



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

def gizmoFinish():
	print 'Finishing gizmo'

	rig_bipedFinalize()

	#pm.setAttr( "tailJLTip_JNT.inheritsTransform", 0 )
	pm.setAttr("spineUpper_CTRL.stretch", 0.2)

	for s in ('l', 'r'):
		pm.setAttr("displayModulesToggleControl."+s+"_fingers", 0)
		pm.setAttr("displayModulesToggleControl."+s+"_toes", 0)
