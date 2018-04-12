__author__ = 'Jerry'


from create.rig_bound import bound


'''

# bound build
import char.cyroBound as charBound
charBound.build( )

'''


def build():
	bound( character='cyro' )
	#bound( character='cyro', rigBound = 'C:/Users/Jerry/Documents/maya/projects/cyro/scenes/rigBound/cyro_new_leg8.ma' )


def cyroPrepareRig():
	print 'Prepare cyro bound'


def cyroRigModules():


	'''
	setAttr "r_upperArmEndTwist_LOCUp_aimConstraint1.upVectorX" 1;

	'''

	print 'Create cyro bound modules'


def cyroFinish():
	print 'Finishing cyro bound'

