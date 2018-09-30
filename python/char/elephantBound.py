__author__ = 'Jerry'


from create.rig_bound import bound


'''

# bound build
import char.elephantBound as charBound
charBound.build( )

'''


def build():
	bound( character='elephant' )
	#bound( character='elephant', rigBound = 'C:/Users/Jerry/Documents/maya/projects/creatures/scenes/rigBound/elephant_new_leg8.ma' )


def elephantPrepareRig():
	print 'Prepare elephant bound'


def elephantRigModules():


	'''
	setAttr "r_upperArmEndTwist_LOCUp_aimConstraint1.upVectorX" 1;

	'''

	print 'Create elephant bound modules'


def elephantFinish():
	print 'Finishing elephant bound'

