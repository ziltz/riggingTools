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
	print 'Create cyro bound modules'


def cyroFinish():
	print 'Finishing cyro bound'

