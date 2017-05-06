__author__ = 'Jerry'

'''
try:
	from rutils.rig_object import rig_object
	from rutils.rig_utils import *
	from other.webcolors import name_to_rgb
	from rutils.rig_transform import rig_transform
#reload(sys.modules['rig_transform'])
#from rig_transform import rig_transform
except ImportError:
	from rig_object import rig_object
	from rig_utils import *
	from webcolors import name_to_rgb
	from rig_transform import rig_transform

'''

from rutils.rig_utils import *
from other.webcolors import name_to_rgb
from rutils.rig_transform import rig_transform


import pymel.core as pm
import maya.cmds as mc
import maya.mel as mm

'''

shapes: pointer, pyramid, circle, arrows

'''
class rig_control(object):

	def __init__(self, **kwds):

		self.side = defaultReturn('', 'side', param=kwds)
		self.name = defaultReturn('rigControl','name', param=kwds)
		self.base = self.name
		if self.side:
			self.name = self.side+'_'+self.name
		self.ctrlName = self.name + '_CTRL'
		self.lockHideAttrs = defaultAppendReturn(['sx','sy','sz','v'],'lockHideAttrs', param=kwds)
		self.showAttrs = defaultReturn([],'showAttrs', param=kwds)
		#self.gimbal = defaultReturn(0,'gimbal', param=kwds)
		#self.pivot = defaultReturn(0,'pivot', param=kwds)
		self.con = defaultReturn(1,'con', param=kwds)
		self.offset = defaultReturn(1,'offset', param=kwds)
		self.modify = defaultReturn(0,'modify', param=kwds)
		self.shape = defaultReturn('circle','shape', param=kwds)
		self.parentOffset = defaultReturn('rigModule_GRP','parentOffset', param=kwds)
		self.targetOffset = defaultReturn('','targetOffset', param=kwds)
		self.child = defaultReturn('', 'child', param=kwds)
		self.ctrl = self._returnShape(self.shape)
		self.rotateOrder = defaultReturn(0,'rotateOrder', param=kwds)
		self.colour = defaultReturn('yellow', 'colour', param=kwds)

		if self.colour == 'yellow':
			if self.side == ('l'):
				self.colour = 'blue'
			if self.side == ('r'):
				self.colour = 'red'

		self.scale = defaultReturn((1,1,1) ,'scale', param=kwds)

		self.parent = ''

		self._setDefaultSettings()

		# constrain setup

		self.constrain = defaultReturn(0, 'constrain', param=kwds)
		self.offsetConstrain = defaultReturn('', 'constrainOffset', param=kwds)

		if pm.objExists(self.offsetConstrain):
			pm.parentConstraint(self.offsetConstrain, self.offset, mo=True)

		if self.constrain is not 0:
			if type(self.constrain) is str: # single obj constrain
				if pm.objExists(self.constrain):
					print 'SINGLE CONSTRAINT'
					pm.parentConstraint(self.con, self.constrain, mo=True)
			else:
				try: # check if pyNode obj
					if self.constrain.exists():
						print 'SINGLE CONSTRAINING PYNODE'
						pm.parentConstraint(self.con, self.constrain, mo=True)
				except AttributeError: # if fail then it must be list
					if type(self.constrain) is list:
						for con in self.constrain:
							if pm.objExists( con ):
								print 'MULTI CONSTRAINING'
								pm.parentConstraint( self.con, con, mo=True )


	def _setDefaultSettings(self):

		lastParent = self.ctrl
		if self.con > 0:
			self.con = rig_transform(0, name=self.name+'Con', parent=self.ctrl
			).object
			pm.setAttr(self.con + ".rotateOrder", self.rotateOrder)
			lastParent = self.con

		if self.offset > 0:
			self.offset = rig_transform(0, name=self.name+'Offset',
			                            parent=self.parentOffset, target=self.targetOffset, child=self.ctrl ).object
			pm.setAttr(self.offset+".rotateOrder", self.rotateOrder)
			self.parent = self.offset


		mods = []
		if self.modify > 0:
			modParent = ''
			for i in range(1, self.modify+1):
				modParent = rig_transform(0, name=self.name+'Modify'+str(i),
				                          target=self.offset, parent=modParent).object
				pm.setAttr(modParent + ".rotateOrder", self.rotateOrder)
				mods.append(modParent)

			if len(mods) == 1:
				self.modify = mods[0]
			else:
				self.modify = mods

			pm.parent(mods[0], self.offset)

			lastMod = mods[-1:][0]
			self.parent = lastMod


		# parent ctrl to obj above, either offset or modify
		pm.parent(self.ctrl, self.parent)

		# set rotate order
		self.ctrl.rotateOrder.set(k=True)
		pm.setAttr(self.ctrl.rotateOrder, self.rotateOrder)

		# set scale
		pm.scale(self.ctrl.cv, self.scale[0], self.scale[1], self.scale[2])
		if self.side == 'r': # flip right ctrls to match left
			pm.scale(self.ctrl.cv, -1, -1, -1)

		# set colour
		self.ctrl.overrideEnabled.set(1)
		self.ctrl.overrideRGBColors.set(1)
		try:
			col = name_to_rgb(self.colour)
			self.ctrl.overrideColorRGB.set(col[0], col[1], col[2])
		except ValueError:
			pm.warning('Could not find specified '+self.colour+'... Using yellow'+'\n')
			col = name_to_rgb('yellow')
			self.ctrl.overrideColorRGB.set(col[0], col[1], col[2])

		# lock attrs
		for at in self.lockHideAttrs:
			self.ctrl.attr(at).setKeyable(False)
			self.ctrl.attr(at).setLocked(True)

		for at in self.showAttrs:
			self.ctrl.attr(at).setKeyable(True)
			self.ctrl.attr(at).setLocked(False)

		if pm.objExists(self.child):
			pm.parent(self.child, lastParent)

	def _returnShape(self, shape):
		func = getattr(self, shape)
		return pm.PyNode(func())

	def pointer(self):
		ctrl = mc.curve(n=self.ctrlName, d=1,
		                  p=[(0, 0, 1), (0, 0, -1), (0, 2, 0), (0, -2, 0), (0, 0, -1), (2, 0, 0), (-2, 0, 0),
		                     (0, 0, -1)], k=[0, 1, 2, 3, 4, 5, 6, 7])
		#mc.rotate(0, -90, 0, r=True, os=True)
		mc.setAttr(ctrl+'.scaleZ', 5)
		mc.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
		return ctrl

	def circle(self):
		return mc.circle(name=self.ctrlName, ch=False, nr=[0, 1, 0])[0]

	def pyramid(self):
		ctrl = mc.curve(n=self.ctrlName, d=1,
		                  p=[(0, 2, 0), (1, 0, -1), (-1, 0, -1), (0, 2, 0), (-1, 0, 1), (1, 0, 1), (0, 2, 0),
		                     (1, 0, -1), (1, 0, 1), (-1, 0, 1),
		                     (-1, 0, -1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

		mc.makeIdentity(ctrl,apply=True, t=1, r=1, s=1, n=0)
		return ctrl

	def arrows(self):
		ctrl = mc.curve(n= self.ctrlName, d=1,
		                        p=[(-1.8975, 0, 0), (-1.4025, 0, 0.37125), (-1.4025, 0, 0.12375), (-0.380966, 0, 0.157801),
		                           (-1.079222, 0, 0.904213), (-1.254231, 0, 0.729204), (-1.341735, 0, 1.341735),
		                           (-0.729204, 0, 1.254231), (-0.904213, 0, 1.079222), (-0.157801, 0, 0.380966),
		                           (-0.12375, 0, 1.4025), (-0.37125, 0, 1.4025), (0, 0, 1.8975), (0.37125, 0, 1.4025),
		                           (0.12375, 0, 1.4025), (0.157801, 0, 0.380966), (0.904213, 0, 1.079222),
		                           (0.729204, 0, 1.254231), (1.341735, 0, 1.341735), (1.254231, 0, 0.729204),
		                           (1.079222, 0, 0.904213), (0.380966, 0, 0.157801), (1.4025, 0, 0.12375),
		                           (1.4025, 0, 0.37125), (1.8975, 0, 0), (1.4025, 0, -0.37125), (1.4025, 0, -0.12375),
		                           (0.380966, 0, -0.157801), (1.079222, 0, -0.904213), (1.254231, 0, -0.729204),
		                           (1.341735, 0, -1.341735), (0.729204, 0, -1.254231), (0.904213, 0, -1.079222),
		                           (0.157801, 0, -0.380966), (0.12375, 0, -1.4025), (0.37125, 0, -1.4025), (0, 0, -1.8975),
		                           (-0.37125, 0, -1.4025), (-0.12375, 0, -1.4025), (-0.157801, 0, -0.380966),
		                           (-0.904213, 0, -1.079222), (-0.729204, 0, -1.254231), (-1.341735, 0, -1.341735),
		                           (-1.254231, 0, -0.729204), (-1.079222, 0, -0.904213), (-0.380966, 0, -0.157801),
		                           (-1.4025, 0, -0.12375), (-1.4025, 0, -0.37125), (-1.8975, 0, 0)],
		                        k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
		                           25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
		                           47, 48])
		mc.makeIdentity(ctrl,apply=True, t=1, r=1, s=1, n=0)
		return ctrl

	def box(self):

		ctrl = mm.eval('curve -n ' + self.ctrlName + ' -d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 '
		                                    '-p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 ;')
		return ctrl

	def sphere(self):

		ctrl = mm.eval('curve -n ' +self.ctrlName+ ' -d 1 -p 0 0.707107 0.707107 '
		                                           '-p 0 1 0 '
		                                  '-p 0 '
		               '0.707107 -0.707107 -p 0.5 0.707107 -0.5 -p 0.707107 0.707107 0 -p 0.5 0.707107 0.5 -p 0 0.707107 0.707107 -p -0.5 0.707107 0.5 -p -0.707107 0.707107 0 -p -0.5 0.707107 -0.5 -p 0 0.707107 -0.707107 -p 0 0 -1 -p -0.707107 0 -0.707107 -p -1 0 0 -p -0.707107 0 0.707107 -p 0 0 1 -p 0.707107 0 0.707107 -p 1 0 0 -p 0.707107 0 -0.707107 -p 0 0 -1 -p 0 -0.707107 -0.707107 -p -0.5 -0.707107 -0.5 -p 0 -1 0 -p -0.707107 -0.707107 0 -p -0.5 -0.707107 -0.5 -p -0.707107 0 -0.707107 -p -0.5 0.707107 -0.5 -p 0 1 0 -p -0.707107 0.707107 0 -p -1 0 0 -p -0.707107 -0.707107 0 -p -0.5 -0.707107 0.5 -p 0 -1 0 -p -0.5 -0.707107 0.5 -p -0.707107 0 0.707107 -p -0.5 0.707107 0.5 -p 0 1 0 -p 0 0.707107 0.707107 -p 0 0 1 -p 0 -0.707107 0.707107 -p -0.5 -0.707107 0.5 -p 0 -1 0 -p 0 -0.707107 0.707107 -p 0.5 -0.707107 0.5 -p 0.707107 0 0.707107 -p 0.5 0.707107 0.5 -p 0 1 0 -p 0.707107 0.707107 0 -p 1 0 0 -p 0.707107 -0.707107 0 -p 0 -1 0 -p 0.5 -0.707107 -0.5 -p 0.707107 0 -0.707107 -p 0.5 0.707107 -0.5 -p 0 1 0 -p 0 0.707107 -0.707107 -p 0 0 -1 -p 0 -0.707107 -0.707107 -p 0.5 -0.707107 -0.5 -p 0.707107 -0.707107 0 -p 0.5 -0.707107 0.5 -p 0 -1 0 -p 0 -0.707107 -0.707107 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -k 25 -k 26 -k 27 -k 28 -k 29 -k 30 -k 31 -k 32 -k 33 -k 34 -k 35 -k 36 -k 37 -k 38 -k 39 -k 40 -k 41 -k 42 -k 43 -k 44 -k 45 -k 46 -k 47 -k 48 -k 49 -k 50 -k 51 -k 52 -k 53 -k 54 -k 55 -k 56 -k 57 -k 58 -k 59 -k 60 -k 61 -k 62 ;')

		return ctrl

	def cylinder(self):
		ctrl = mm.eval('curve -n '+self.ctrlName+' -d 1 -p 1 1 0 -p 0.92388 1 -0.382683 -p 0.707107 1 -0.707106 -p 0.382684 1 -0.923879 -p 5.06639e-007 1 -1 -p -0.382683 1 -0.92388 -p -0.707106 1 -0.707107 -p -0.923879 1 -0.382684 -p -1 1 -3.57628e-007 -p -0.92388 1 0.382683 -p -0.707107 1 0.707107 -p -0.382684 1 0.923879 -p -1.49012e-007 1 1 -p 0.382683 1 0.92388 -p 0.707107 1 0.707107 -p 0.92388 1 0.382683 -p 1 1 0 -p 1 -1 0 -p 0.92388 -1 -0.382683 -p 0.707107 -1 -0.707106 -p 0.382684 -1 -0.923879 -p 5.06639e-007 -1 -1 -p -0.382683 -1 -0.92388 -p -0.707106 -1 -0.707107 -p -0.923879 -1 -0.382684 -p -1 -1 -3.57628e-007 -p -1 1 -3.57628e-007 -p -1 -1 -3.57628e-007 -p -0.92388 -1 0.382683 -p -0.707107 -1 0.707107 -p -0.382684 -1 0.923879 -p -1.49012e-007 -1 1 -p -1.49012e-007 1 1 -p -1.49012e-007 -1 1 -p 0.382683 -1 0.92388 -p 0.707107 -1 0.707107 -p 0.92388 -1 0.382683 -p 1 -1 0 -p 0.92388 -1 -0.382683 -p 0.707107 -1 -0.707106 -p 0.382684 -1 -0.923879 -p 5.06639e-007 -1 -1 -p 5.06639e-007 1 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -k 25 -k 26 -k 27 -k 28 -k 29 -k 30 -k 31 -k 32 -k 33 -k 34 -k 35 -k 36 -k 37 -k 38 -k 39 -k 40 -k 41 -k 42 ;')


		return ctrl

'''

'''
def simpleControls(joints=None, **kwds ):

	print type(joints)
	jointList = joints
	if type(joints) is str or type(joints) is unicode:
		jointList = [joints]

	controlDict = {}
	ctrlShape = 'box'
	try:
		ctrlShape = kwds['shape']
		kwds.pop('shape', 0)
	except KeyError:
		pass

	for jnt in jointList:
		parent = None

		print 'joint ' + jnt
		try:
			parent = pm.listRelatives(jnt, type="joint", p=True)[0]
		except IndexError:
			print 'No parent found'

		side = ''
		if jnt.startswith('l_'):
			side = 'l'
		if jnt.startswith('r_'):
			side = 'r'

		naming = jnt.replace('_JNT', '')
		if jnt.endswith( 'JA_JNT' ):
			naming = jnt.replace( 'JA_JNT', '' )
		if jnt.endswith( '_JA_JNT' ):
			naming = jnt.replace( '_JA_JNT', '' )

		name = naming
		if side:
			name = naming.replace( side+'_', '' )

		print 'ctrlShape = '+ctrlShape

		control = rig_control(side=side, name=name, shape=ctrlShape,
		                      targetOffset=jnt, constrainOffset=parent,
		                      constrain=jnt,
		                      **kwds)

		controlDict[jnt] = control

	return controlDict


def createCtrlPivot( ctrlClass, overrideScale=None  ):

	side = getattr( ctrlClass, 'side')
	base = getattr( ctrlClass, 'base')
	ctrl = getattr( ctrlClass, 'ctrl')

	scale = getattr(ctrlClass, 'scale')
	if overrideScale is not None:
		scale = overrideScale

	pivot = rig_control(side=side, name=base + 'Pivot',
	                         shape='sphere',
	                         parentOffset=ctrl,
	                         targetOffset=ctrl, con=0, pivot=0,
	                         lockHideAttrs=['rx', 'ry', 'rz'])
	pm.scale(pivot.ctrl.cv, 0.1, 0.1, 0.1)
	pm.scale(pivot.ctrl.cv, scale[0], scale[1], scale[2])
	pm.connectAttr(pivot.ctrl.translate, ctrl.rotatePivot, f=True)
	pm.connectAttr(pivot.ctrl.scale, ctrl.scalePivot, f=True)
	connectAttrToVisObj(ctrl, 'pivotVis', pivot.ctrl.getShape())

	return pivot

def createCtrlGimbal( ctrlClass, overrideScale=None ):

	side = getattr(ctrlClass, 'side')
	base = getattr(ctrlClass, 'base')
	ctrl = getattr(ctrlClass, 'ctrl')
	con = getattr(ctrlClass, 'con')

	scale = getattr(ctrlClass, 'scale')
	if overrideScale is not None:
		scale = overrideScale

	gimbal = rig_control(side=side, name=base + "Gimbal",
	                          parentOffset=ctrl, targetOffset=ctrl,
	                          con=0, pivot=0, child=con)
	pm.scale(gimbal.ctrl.cv, 0.75, 0.75, 0.75)
	pm.scale(gimbal.ctrl.cv, scale[0], scale[1], scale[2])
	connectAttrToVisObj(ctrl, 'gimbalVis', gimbal.ctrl.getShape())
	'''
	pm.addAttr(ctrl, longName='gimbalVis', at='long', k=False, min=0, max=1)
	ctrl.gimbalVis.set(cb=True)
	pm.connectAttr(ctrl.gimbalVis, gimbal.ctrl.getShape().visibility)
	'''
	return gimbal

'''

if multiple objects passed in to constrain then add space switch
if not just normal constrain

# constrain single
constrainObject('l_armOffset_GRP', 'target1_GRP')
constrainObject('l_armOffset_GRP', 'target1_GRP', mo=False)

# constrain multiple
constrainObject('l_armOffset_GRP', ['target1_GRP', 'target2_GRP','target3_GRP', 'target4_GRP'], 'l_arm_CTRL',  ['world', 'local', 'target', 'spacing'])

# interpType
0 = no flip
1 = average
2 = shortest
3 = longest
4 = cache

TODO parentConstraint skip translate and rotation

'''
def constrainObject( obj, multipleConstrainer, ctrl='',enumName=[], **kwds):

	maintainOffset = defaultReturn(True,'mo', param=kwds)
	constrainType = defaultReturn('parentConstraint', 'type', param=kwds)
	skip = defaultReturn(None, 'skip', param=kwds)
	#skipTranslate = defaultReturn(None, 'skipTranslate', param=kwds)
	#skipRotate = defaultReturn(None, 'skipRotate', param=kwds)
	interp = defaultReturn(0, 'interp', param=kwds)

	doSpace = 1
	if type(multipleConstrainer) is str:
		doSpace = 0

	obj = pm.PyNode(obj)

	if pm.objExists(obj):
		try:
			con = ''
			if constrainType is 'parentConstraint':
				if skip is None:
					con = pm.parentConstraint(multipleConstrainer, obj,
					                          mo=maintainOffset)
				else:
					con = pm.parentConstraint(multipleConstrainer, obj,
				                          mo=maintainOffset, skip=skip)

			if constrainType is 'orientConstraint':
				if skip is None:
					con = pm.orientConstraint(multipleConstrainer, obj,
					                          mo=maintainOffset)
				else:
					con = pm.orientConstraint(multipleConstrainer, obj,
				                          mo=maintainOffset, skip=skip)

			if constrainType is 'pointConstraint':
				if skip is None:
					con = pm.pointConstraint(multipleConstrainer, obj,
					                          mo=maintainOffset)
				else:
					con = pm.pointConstraint(multipleConstrainer, obj,
				                          mo=maintainOffset, skip=skip)

			pm.setAttr(con.interpType, interp)

			if doSpace:
				ctrl = pm.PyNode(ctrl)
				if len(multipleConstrainer) is len(enumName):
					targets = con.getWeightAliasList()

					enumList = enumName[0]
					for i in range (1, len(enumName)):
						enumList += ':'+enumName[i]

					if not ctrl.hasAttr('space'):
						pm.addAttr(ctrl, ln='space', at='enum', enumName=enumList, k=True)

					valueDict = {}
					for t in targets:
						list = []
						for ta in targets:
							if ta is t:
								list.append(1)
							else:
								list.append(0)
						valueDict[t] = list

					for v in valueDict:
						for i in range (0,len(valueDict)):
							pm.setDrivenKeyframe( v, cd=ctrl.space, dv=i, v=(valueDict[v])[i])

				else:
					pm.error(' Unequal amount of constrainer to enum names ')

		except pm.MayaNodeError:
			for m in multipleConstrainer:
				print m + ' does not exist'+'\n'
	else:
		print obj+' does not exist'+'\n'




def fkControlChain( jointChain, modify=1, scale=[1,1,1]):

	controls = []

	i = 0
	for jnt in jointChain:
		constrainOffset = 0
		if i > 0:
			constrainOffset = controls[i-1].con

		name = jnt.replace('_JNT', '')
		side = ''
		ctrlName = ''
		if jnt.startswith('l_') or jnt.startswith('r_'):
			side = jnt[:1]
			ctrlName = name[2:]
		else:
			ctrlName = name

		scale[0] = scale[0] * 0.8
		scale[2] = scale[2] * 0.8

		fkCtrl = rig_control( side=side, name=ctrlName, shape='box', modify=modify,
		                      lockHideAttrs=['tx','ty','tz'], targetOffset=jnt,
		                      constrain=pm.PyNode(jnt),
		                      constrainOffset=constrainOffset,scale=scale )

		controls.append(fkCtrl)
		i += 1


	return controls


def offsetSDKControls( ctrl, modifyList, transformAttr='rx',attr='offsetControl',
                       sdkVal=60, reverse=0 ):

	try:
		print getattr(ctrl, attr)+' exists'
	except AttributeError:
		pm.addAttr(ctrl, longName=attr, at='float',
		           k=True, dv=0, min=-10, max=10)

	val = sdkVal / len(modifyList)
	if reverse:
		rCount = len(modifyList)-1
		for i in range(0, len(modifyList)):
			multiplier = i
			if i == 0:
				multiplier = 0.5
			pm.setDrivenKeyframe(modifyList[rCount] + '.' + transformAttr,
			                     cd=getattr(ctrl, attr),
			                     dv=0, v=0)
			pm.setDrivenKeyframe(modifyList[rCount] + '.' + transformAttr,
			                     cd=getattr(ctrl, attr),
			                     dv=10, v=val * multiplier)
			pm.setDrivenKeyframe(modifyList[rCount] + '.' + transformAttr,
			                     cd=getattr(ctrl, attr),
			                     dv=-10, v=val * (multiplier * -1))
			rCount = rCount - 1
	else:
		for i in range(0, len(modifyList)):
			multiplier = i
			if i == 0:
				multiplier = 0.5
			pm.setDrivenKeyframe(modifyList[i]+'.'+transformAttr,
			                     cd=getattr(ctrl,attr),
			                     dv=0, v=0)
			pm.setDrivenKeyframe(modifyList[i]+'.'+transformAttr,
			                     cd=getattr(ctrl,attr),
			                     dv=10, v=val*multiplier)
			pm.setDrivenKeyframe(modifyList[i]+'.'+transformAttr,
			                     cd=getattr(ctrl,attr),
			                     dv=-10, v=val*(multiplier*-1))






