


import pymel.core as pm
from rutils.rig_utils import *


def rig_constrainByType( type, targetObjects, conObject, **kwds ):

	maintainOffset = defaultReturn(1, 'mo', param=kwds)

	try:
		pm.delete(pm.listRelatives(conObject, type='constraint'))

		if 'parent' in type:
			pm.parentConstraint( targetObjects, conObject, mo=maintainOffset  )

		if 'orient' in type:
			pm.orientConstraint( targetObjects, conObject, mo=maintainOffset )

		if 'point' in type:
			pm.pointConstraint(targetObjects, conObject, mo=maintainOffset)
	except Exception as e:
		print 'No Such object'