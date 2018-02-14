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

	rig_bipedPrepare()


def cyroRigModules():
	print 'Create cyro rig modules'

	biped = rig_biped()
	quad = rig_quadruped()

	#biped.spine(ctrlSize=20)
	quad.spine(ctrlSize=50)

	quad.pelvis(ctrlSize=35)

	# make neck
	#biped.neck( ctrlSize=2.5 )

	#biped.head(ctrlSize=5)

	
	biped.spineFullBodyCtrl = quad.spineFullBodyCtrl
	biped.spineUpperCtrl = quad.spineUpperCtrl
	biped.spineLowerCtrl = quad.spineLowerCtrl

	biped.pelvisControl = quad.pelvisControl

	#biped.switchLoc = quad.switchLoc

	biped.elbowAxis = 'ry'

	for side in ['l', 'r']:
		armModule = biped.arm(side, ctrlSize=12)

		fingersModule = biped.hand(side, ctrlSize=5)

		shoulderModule = biped.shoulder(side, ctrlSize=10)

		biped.connectArmShoulder(side)

		if side == 'l':
			quad.switchLoc = biped.switchLoc
		# make quadruped leg 
		legModule = quad.leg(side, ctrlSize = 30)

		toesModule = quad.foot(side, ctrlSize=10)

		quad.connectLegPelvis()



	tail = rig_tail( rootJoint = 'tailJA_JNT', ctrlSize = 30 )
	tail.make()


	# make pubis and belly controls

def cyroFinish():
	print 'Finishing cyro'

	rig_bipedFinalize()

	#pm.setAttr("spineUpper_CTRL.stretch", 0.2)

