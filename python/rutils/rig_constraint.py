


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



def rig_constraintExportPrintCmds(group):

	alltrans = pm.listRelatives(group, pa=True, c=True, ad=True, type='transform')

	for con in alltrans:
		if con.type() == 'parentConstraint':
			try:
				driver = con.getTargetList()[0]
				drivenObj = pm.listConnections(con+'.constraintTranslateX')[0]
				print 'pm.parentConstraint( "'+driver.stripNamespace()+'" ,"' \
				                                                      ''+drivenObj.stripNamespace()+'" , mo=True)'
			except IndexError:
				print 'More than one driver on constraint '+con.stripNamespace()

