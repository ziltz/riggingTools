

import pymel.core as pm
import maya.cmds as cmds

from make.rig_controls import *
from rutils.rig_transform import rig_transform
from rutils.rig_name import *
from rutils.rig_nodes import *
from rutils.rig_anim import *

'''

procs


import create.rig_facial as facial
facial.facialTransformHierarchy(cmds.ls(sl=True), 'headJALocal_JNT' )


snap tweakers to curve with knots of 10 (rebuild from hi curve)

grpList = pm.ls(sl=True)
_curve = pm.PyNode('upperLip_CRVShape')

u = 0 
for loc in grpList:
    nme = loc.replace('Offset_GRP', '_poi')
    poi = pm.createNode( 'pointOnCurveInfo', n=nme )
    fourByMat = cmds.shadingNode('fourByFourMatrix', asUtility=True)
    dMatr = cmds.shadingNode('decomposeMatrix', asUtility=True)
    pm.connectAttr( _curve+'.worldSpace', poi + '.inputCurve' )
    pm.setAttr( poi +'.parameter', u )
    pm.connectAttr( poi+'.position', loc+'.t')
    cmds.connectAttr( poi+'.normalizedTangentX', fourByMat+'.in00',f=True )
    cmds.connectAttr( poi+'.normalizedTangentY', fourByMat+'.in01',f=True )
    cmds.connectAttr( poi+'.normalizedTangentZ', fourByMat+'.in02',f=True )
    cmds.connectAttr( fourByMat+'.output', dMatr+'.inputMatrix',f=True )
    cmds.connectAttr( dMatr+'.outputRotate', loc+'.rotate',f=True )
    u += 0.1



'''



def defaultShapeDriverList():

	shapes = [ 'jawOpen',
	           'jawClosed',
	           'browSqueeze',
	           'lowerLipFunnel',
	           'upperLipFunnel',
	           'scalp'
	]

	sideShapes = []
	for s in ('l','r'):
		sideShapes.extend( [
			s+'MuzzleUp',
		    s+'MuzzleBack',
		    s+'MuzzleForward',
		    s+'MuzzleDown',
		    s+'BrowUp',
		    s+'BrowDown',
		    s+'CheekUp',
		    s+'CheekPuff',
		    s+'Blink'
		] )

	shapes.extend(sideShapes)

	return shapes


def connectShapesToShapeBS(shapeBS):

	shapeDriver = 'facialShapeDriver_LOC'
	#shapeBS = 'shapeBS'

	shapes = defaultShapeDriverList()

	for shape in shapes:
		if cmds.objExists(shapeBS+'.'+shape):
			pm.connectAttr(shapeDriver+'.'+shape, shapeBS+'.'+shape, f=True )


def facialShapeDriver():

	shapeDriver = 'facialShapeDriver_LOC'
	if not cmds.objExists(shapeDriver):
		shapeDriver = rig_transform(0, name='facialShapeDriver',
		                            type='locator',
		                            parent='rig_GRP').object

	shapeDriver = pm.PyNode(shapeDriver)

	shapes = defaultShapeDriverList()

	pm.addAttr(shapeDriver, ln='SHAPE', at='enum',
	           enumName='___________',
	           k=True)
	shapeDriver.SHAPE.setLocked(True)

	for shape in shapes:
		print shape
		pm.addAttr(shapeDriver, longName=shape, at='float', k=True, min=0,
		           max=1, dv=0)

'''

create one offset group, three locators above joint

pick left and middle joints
facialTransformHierarchy(['scalpJA_JNT'], 'headJALocal_JNT' )

does right side aswell
'''
def facialTransformHierarchy(joints,parent):

	parentTrans = parent.replace('_JNT','_GRP')
	if not cmds.objExists(parentTrans):
		parentTrans = rig_transform(0, name=parent.replace('_JNT',''),
		                            target = parent).object

	for jnt in joints:

		mirrorJnt = rig_nameMirror(jnt)
		if jnt == mirrorJnt:
			print 'joint ' +jnt+' is middle joint'
			mirrorJnt = ''
		for j in (jnt, mirrorJnt ):
			if cmds.objExists(j):
				offset = rig_transform(0, name=j.replace('JA_JNT', 'Offset'),
				                       target=j, parent=parentTrans ).object
				loc1 = rig_transform(0, name=j.replace('JA_JNT', '_sdk1'),
				                       target=offset,
				                       type='locator',
				                       parent=offset).object
				loc2 = rig_transform(0, name=j.replace('JA_JNT', '_sdk2'),
				                     target=loc1,
				                     type='locator',
				                     parent=loc1).object

				cmds.parent( j, loc2 )


'''
select all children joints to make tranforms
'''
def facialTransformHierarchyChildren(joints):

	for j in joints:
		parentJnt = cmds.listRelatives( j, p=True )[0]
		offset = rig_transform(0, name=j.replace('JA_JNT', 'Offset'),
		                       target=j, ).object
		loc1 = rig_transform(0, name=j.replace('JA_JNT', '_sdk1'),
		                     target=offset,
		                     type='locator',
		                     parent=offset).object
		loc2 = rig_transform(0, name=j.replace('JA_JNT', '_sdk2'),
		                     target=loc1,
		                     type='locator',
		                     parent=loc1).object

		cmds.parent(j, loc2)
		cmds.parentConstraint(parentJnt, offset, mo=True)



def facialMirrorSDKLocator(sdkLoc):

	mirror = 'facialtmpMirror_GRP'
	if cmds.objExists(mirror):
		cmds.delete(mirror)
	mirror = rig_transform(0, name='facialtmpMirror').object

	cmds.setAttr(mirror + '.scaleX', 1)

	copy = 'facialtmp_GRP'
	if cmds.objExists(copy):
		cmds.delete(copy)
	copy = rig_transform(0, name='facialtmp', target=sdkLoc, parent=mirror).object

	cmds.setAttr(mirror+'.scaleX', -1)

	mirrorLoc = rig_nameMirror(sdkLoc)

	print 'mirrorLoc = '+mirrorLoc

	if cmds.objExists(mirrorLoc):
		con = cmds.parentConstraint(copy, mirrorLoc)
		cmds.dgdirty(allPlugs=True)
		#cmds.delete(con)


'''
create multdouble linear from single shape to combination/corrective shape

'''
def connectFacialCorrectiveBS():
	shapeDriver = 'facialShapeDriver_LOC'
	correctiveBS = 'facialCorrectiveBS'
	tripleBS = 'facialTripleCorrectiveBS'

	comboShapes = pm.listAttr(correctiveBS+'.weight', m=True)
	tripleShapes = pm.listAttr(tripleBS+'.weight', m=True)


	for shape in comboShapes:

		try:
			con = pm.listConnections(correctiveBS+'.'+shape)[0]
		except IndexError:
			singleShapes = shape.split('_')
			# combo shapes only
			if len(singleShapes) == 2:
				multDoubleLinear( shapeDriver+'.'+singleShapes[0],
				                  shapeDriver+'.'+singleShapes[1],
				                  correctiveBS+'.'+shape )
			'''
			if len(singleShapes) == 3:
				multDoubleLinear( correctiveBS+'.'+singleShapes[0]+'_'+singleShapes[1],
				                  shapeDriver+'.'+singleShapes[2],
				                  correctiveBS+'.'+shape)
			'''

	for shape in tripleShapes:

		try:
			con = pm.listConnections(tripleBS + '.' + shape)[0]
		except IndexError:
			singleShapes = shape.split('_')
			# combo shapes only
			if len(singleShapes) == 3:
				multDoubleLinear(correctiveBS + '.' + singleShapes[0] + '_' + singleShapes[1],
				                 shapeDriver + '.' + singleShapes[2],
				                 tripleBS + '.' + shape)



# y and z four way control direct connect

def fourWayShapeControl(driver, shapes, parent, mult=1, ctrlSize=1, facialLoc='facialShapeDriver_LOC'):

	ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
	ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
	ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

	side = rig_nameGetSide(driver)
	base = rig_nameGetBase(driver)
	driverCtrl = rig_control(side=side, name=base, shape='pyramid',modify=1,
	                         lockHideAttrs=['rx', 'ry', 'rz', 'tx'],
	                         scale=ctrlSizeQuarter)

	pm.scale(driverCtrl.ctrl.cv, 1, 0, 1)

	pm.delete(pm.parentConstraint( driver, driverCtrl.offset ))
	#pm.parentConstraint(parent, driverCtrl.offset, mo=True)
	pm.parent(driverCtrl.offset, parent)

	rig_animDrivenKey(driverCtrl.ctrl.translateY, (0,mult), facialLoc+'.'+shapes[0], (0,1))
	rig_animDrivenKey(driverCtrl.ctrl.translateY, (0,-1*mult), facialLoc+'.'+shapes[1], (0,1))
	rig_animDrivenKey(driverCtrl.ctrl.translateZ, (0, mult), facialLoc+'.'+shapes[2], (0, 1))
	rig_animDrivenKey(driverCtrl.ctrl.translateZ, (0, -1*mult), facialLoc+'.'+shapes[3], (0, 1))


	multiplyDivideNode(side+base, 'multiply', input1=[driverCtrl.ctrl.translateY,
	                                                    driverCtrl.ctrl.translateZ, 0],
	                   input2=[-0.5*mult, -0.5*mult, 0.5*mult],
	                   output=[driverCtrl.modify+'.translateY',driverCtrl.modify+'.translateZ'])

	pm.transformLimits(driverCtrl.ctrl, ty=(-1*mult, mult), ety=(1, 1))
	pm.transformLimits(driverCtrl.ctrl, tz=(-1*mult, mult), etz=(1, 1))

	return driverCtrl


# y axis two way control direct connect

def twoWayShapeControl(driver, shapes, parent, mult=1, ctrlSize=1, facialLoc='facialShapeDriver_LOC'):

	ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
	ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
	ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

	side = rig_nameGetSide(driver)
	base = rig_nameGetBase(driver)
	driverCtrl = rig_control(side=side, name=base, shape='circle',modify=1,
	                         lockHideAttrs=['rx', 'ry', 'rz', 'tx', 'tz'],
	                         scale=ctrlSizeQuarter)

	pm.scale(driverCtrl.ctrl.cv, 0.5, 1, 1)

	pm.delete(pm.parentConstraint( driver, driverCtrl.offset ))
	#pm.parentConstraint(parent, driverCtrl.offset, mo=True)
	pm.parent(driverCtrl.offset, parent)

	rig_animDrivenKey(driverCtrl.ctrl.translateY, (0,mult), facialLoc+'.'+shapes[0], (0,1))
	rig_animDrivenKey(driverCtrl.ctrl.translateY, (0,-1*mult), facialLoc+'.'+shapes[1], (0,1))

	multiplyDivideNode(side + base, 'multiply', input1=[driverCtrl.ctrl.translateY,0, 0],
	                   input2=[0.5*mult, 0.5*mult, 0.5*mult],
	                   output=[driverCtrl.modify + '.translateY',])

	pm.transformLimits(driverCtrl.ctrl, ty=(-1*mult, mult), ety=(1, 1))

	return driverCtrl

# y axis one way control direct connect

def oneWayShapeControl(driver, shape, parent, mult=1, ctrlSize=1, facialLoc='facialShapeDriver_LOC'):

	ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
	ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
	ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

	side = rig_nameGetSide(driver)
	base = rig_nameGetBase(driver)
	driverCtrl = rig_control(side=side, name=base, shape='pyramid',modify=1,
	                         lockHideAttrs=['rx', 'ry', 'rz', 'tx', 'tz'],
	                         scale=ctrlSizeQuarter)

	pm.scale(driverCtrl.ctrl.cv, 0, 1, 1)

	pm.delete(pm.parentConstraint( driver, driverCtrl.offset ))
	#pm.parentConstraint(parent, driverCtrl.offset, mo=True)
	pm.parent( driverCtrl.offset, parent)

	#pm.connectAttr( driverCtrl.ctrl.translateY, facialLoc+'.'+shape )
	rig_animDrivenKey(driverCtrl.ctrl.translateY, (0,mult), facialLoc+'.'+shape, (0,1))

	multiplyDivideNode(side + base, 'multiply', input1=[driverCtrl.ctrl.translateY,0,0],
	                   input2=[0.5*mult, 0.5*mult, 0.5*mult],
	                   output=[driverCtrl.modify + '.translateY', ])

	pm.transformLimits(driverCtrl.ctrl, ty=(0, mult), ety=(1, 1))

	return driverCtrl


'''

finds all sdk2_LOC transforms and make local/world facial controllers to the driving joints

two local groups, offset and con with parentConstraint from sdk2_LOC
world control, offset parentConstraint from world skeleton, modify direct connect from
localCon, ctrl direct connection back to joint under sdk2_LOC

'''
def facialLocalWorldControllers(module,parent, ctrlSize=1):

	ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
	ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
	ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

	transLocs = cmds.ls("*_sdk2_LOC" , type="transform")

	for loc in transLocs:
		locName = loc.replace('_sdk2', '')

		side = rig_nameGetSide(locName)
		base = locName
		#if side:
		base = rig_nameGetBase(locName)

		print 'side = ' + side
		print 'base = ' + base

		name = loc.replace('_sdk2_LOC', '')

		print 'name = ' + name

		localOffset = rig_transform(0, name=name+'LocalOffset',
	                        parent=module.parts, target=loc ).object
		localCon = rig_transform(0, name=name + 'LocalCon',
		                            parent=localOffset, target=localOffset).object

		pm.parentConstraint( loc, localCon, mo=True )

		ctrlName = base+'Twk'
		if 'Tweak' in base:
			ctrlName = base.replace('Tweak','Twker')

		print 'ctrlName = ' + ctrlName

		ctrl = rig_control(side=side, name=ctrlName, shape='circle', modify=1, scale=ctrlSize,
		            directCon=1,parentOffset=module.controlsSec , secColour=1,
		            directConAttrs=('tx','ty','tz','rx','ry','rz'))

		pm.rotate(ctrl.ctrl.cv, 0, 0, 90, r=True, os=True)
		if side == 'r':
			pm.move(ctrl.ctrl.cv, -0.2, 0, 0, r=True, os=True)
		else:
			pm.move(ctrl.ctrl.cv, 0.2, 0, 0, r=True, os=True)

		jnt = pm.listRelatives(loc, type='joint', c=True)[0]

		pm.delete(pm.parentConstraint( loc, ctrl.offset ))
		pm.parent( ctrl.offset, parent )
		for at in ('tx','ty','tz','rx','ry','rz'):
			pm.connectAttr( localCon+'.'+at, ctrl.modify+'.'+at )
			pm.connectAttr( ctrl.ctrl + '.' + at, jnt + '.' + at)




'''

'''

def createJointsFromCVs(curve):

	crv = pm.PyNode(curve)

	crvShape = crv.getShape()
	crvCVs = crvShape.getCVs()

	for p in crvCVs:
	    print p
	    cmds.select(cl=True)
	    cmds.joint(p=p)




