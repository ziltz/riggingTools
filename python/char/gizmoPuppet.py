__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *

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


def gizmoRigModules():
	print 'Create gizmo rig modules'

	biped = rig_biped()
	biped.elbowAxis = 'ry'
	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=3)

		fingersModule = biped.hand(side, ctrlSize=0.5)

		shoulderModule = biped.shoulder(side, ctrlSize=2)

		biped.connectArmShoulder(side)

	

def gizmoFinish():
	print 'Finishing gizmo'






