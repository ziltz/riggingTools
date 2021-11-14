__author__ = 'Jerry'


from create.rig_bound import bound


'''

# bound build
import char.thingBound as charBound
reload(charBound)
charBound.build( )

'''


def build():
	bound( character='thing' )
	#bound( character='thing', rigBound = 'C:/Users/Jerry/Documents/maya/projects/creatures/scenes/rigBound/elephant_new_leg8.ma' )


def thingPrepareRig():
	print 'Prepare thing bound'

def thingRigModules():


	print 'Create thing bound modules'


def thingFinish():
	print 'Finishing thing bound'

