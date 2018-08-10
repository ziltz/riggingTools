
from rutils.rig_transform import *

import pymel.core as pm
import maya.mel as mm
import maya.cmds as cmds

def extractShapes(geo , blendShape):
	bs = pm.listAttr(blendShape+'.weight', m=True)

	for shape in bs:
	    cmds.setAttr( blendShape+'.'+shape, 1 )
	    m = cmds.duplicate( geo, n=shape )
	    cmds.setAttr( blendShape+'.'+shape, 0 )
	    cmds.hide(m)



'''
Finds existing list of shapes in blendshapes from geo and
creates locator with same shape names attrs
'''
def connectShapesToLoc(locName='flexShapes', refGeo='skin_C_body_GS'):
	blendShapes = mm.eval('rig_returnDeformers("'+refGeo+'", "blendShape")')
	if len(blendShapes) == 1:
		bs = blendShapes[0]
		shapeList = pm.listAttr(bs+'.weight', m=True)
		loc = locName+'_LOC'
		if not cmds.objExists(loc):
			loc = rig_transform(0, name= locName, type='locator').object

		for shape in shapeList:
			attr = pm.addAttr(loc, longName=shape, attributeType="double",
                 min=0, max=1, defaultValue=0, keyable=True)
			print bs
			print shape
			pm.connectAttr(loc+'.'+shape, bs+'.'+shape, f=True )


'''
connects selected geo's blendshapes to locator

'''
def connectBlendShapesToLoc(geos, locator='flexShapes_LOC'):
	shapeList = pm.listAttr(locator, ud=True)
	for geo in geos:
		blendShapes = mm.eval('rig_returnDeformers("'+geo+'", "blendShape")')
		if len(blendShapes) == 1:
			bs = blendShapes[0]
			geoShapeList = pm.listAttr(bs+'.weight', m=True)
			for shape in geoShapeList:
				if shape in shapeList:
					pm.connectAttr(locator+'.'+shape, bs+'.'+shape, f=True )
					print 'Connected '+shape+' on '+geo




