__author__ = 'Jerry'


from utils.rig_object import rig_object
from utils.rig_utils import *
from other.webcolors import name_to_rgb
from utils.rig_transform import rig_transform
#reload(sys.modules['rig_transform'])
#from rig_transform import rig_transform

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
		self.gimbal = defaultReturn(0,'gimbal', param=kwds)
		self.pivot = defaultReturn(0,'pivot', param=kwds)
		self.con = defaultReturn(1,'con', param=kwds)
		self.offset = defaultReturn(1,'offset', param=kwds)
		self.modify = defaultReturn(0,'modify', param=kwds)
		self.shape = defaultReturn('circle','shape', param=kwds)
		self.parentOffset = defaultReturn('','parentOffset', param=kwds)
		self.targetOffset = defaultReturn('','targetOffset', param=kwds)
		self.ctrl = self._returnShape(self.shape)
		self.colour = defaultReturn('yellow','colour', param=kwds)
		if self.side is 'l':
			self.colour = 'blue'
		if self.side is 'r':
			self.colour = 'red'

		self.scale = defaultReturn((1,1,1) ,'scale', param=kwds)

		self.parent = ''

		self._setDefaultSettings()

		# constrain setup

		self.constrain = defaultReturn(0, 'constrain', param=kwds)
		self.offsetConstrain = defaultReturn('', 'constrainOffset', param=kwds)

		if pm.objExists(self.offsetConstrain):
			pm.parentConstraint(self.offsetConstrain, self.offset, mo=True)

		print 'self.constrain = ' +str(self.constrain)
		if self.constrain:
			if type(self.constrain) is str:
				print 'single obj constrain'
				if pm.objExists(self.constrain):
					pm.parentConstraint(self.con, self.constrain, mo=True)
			elif type(self.constrain) is list:
				print 'multiple obj constrain'
				for con in self.constrain:
					print 'self.con = '+self.con
					print 'con = ' + con
					if pm.objExists( con ):
						pm.parentConstraint( self.con, con, mo=True )


	def _setDefaultSettings(self):

		if self.con > 0:
			self.con = rig_transform(0, name=self.name+'Con', parent=self.ctrl
			).object

		if self.offset > 0:
			self.offset = rig_transform(0, name=self.name+'Offset',
			                            parent=self.parentOffset, target=self.targetOffset, child=self.ctrl ).object
			self.parent = self.offset

		mods = []
		if self.modify > 0:
			modParent = ''
			for i in range(1, self.modify+1):
				modParent = rig_transform(0, name=self.name+'Modify'+str(i),
				                          target=self.offset, parent=modParent).object
				mods.append(modParent)

			if len(mods) == 1:
				self.modify = mods[0]
			else:
				self.modify = mods

			mc.parent(mods[0], self.offset)

			lastMod = mods[-1:][0]
			self.parent = lastMod


		if self.pivot > 0:
			self.pivot = rig_control(side=self.side, name=self.base+'Pivot',
			                         shape='sphere',
			                         parentOffset=self.ctrl,
			                         targetOffset=self.ctrl, con=0, pivot=0,
			                         lockHideAttrs=['rx','ry','rz'] ).ctrl
			pm.scale(self.pivot.cv, self.scale[0], self.scale[1], self.scale[2])
			pm.connectAttr(  self.pivot.translate, self.ctrl.rotatePivot, f=True)
			pm.connectAttr(  self.pivot.scale, self.ctrl.scalePivot, f=True)
			connectAttrToVisObj( self.ctrl, 'pivotVis', self.pivot.getShape() )
			#pm.addAttr(self.ctrl, longName='pivotVis', at='long', k=False, min=0,
			#  max=1)
			#self.ctrl.pivotVis.set(cb=True)
			#pm.connectAttr( self.ctrl.pivotVis,  self.pivot.getShape().visibility )

		if self.gimbal > 0:
			self.gimbal = rig_control( side=self.side,name=self.base+"Gimbal",
			                           parentOffset=self.ctrl, targetOffset=self.ctrl, con=0, pivot=0, child=self.con ).ctrl
			pm.scale(self.gimbal.cv, 0.75, 0.75, 0.75)
			pm.scale(self.gimbal.cv, self.scale[0], self.scale[1], self.scale[2])
			pm.addAttr(self.ctrl, longName='gimbalVis', at='long', k=False, min=0, max=1)
			self.ctrl.gimbalVis.set(cb=True)
			pm.connectAttr(self.ctrl.gimbalVis, self.gimbal.getShape().visibility)

		# parent ctrl to obj above, either offset or modify
		pm.parent(self.ctrl, self.parent)

		# set scale
		pm.scale(self.ctrl.cv, self.scale[0], self.scale[1], self.scale[2])

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
'''

if multiple objects passed in to constrain then add space switch
if not just normal constrain

# constrain single
constrainObject('l_armOffset_GRP', 'target1_GRP')
constrainObject('l_armOffset_GRP', 'target1_GRP', mo=False)

# constrain multiple
constrainObject('l_armOffset_GRP', ['target1_GRP', 'target2_GRP','target3_GRP', 'target4_GRP'], 'l_arm_CTRL',  ['world', 'local', 'target', 'spacing'])

'''
def constrainObject( obj, multipleConstrainer, ctrl='',enumName=[], **kwds):

	maintainOffset = defaultReturn(True,'mo', param=kwds)

	doSpace = 1
	if type(multipleConstrainer) is str:
		doSpace = 0

	obj = pm.PyNode(obj)

	if pm.objExists(obj):
		try:
			con = pm.parentConstraint(multipleConstrainer, obj, mo=maintainOffset)

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




def fkControlChain( jointChain, modify=1):

	controls = []

	i = 0
	for jnt in jointChain:
		constrainOffset = 0
		if i > 0:
			constrainOffset = controls[i-1].con

		print 'constraintOffset = '+str(constrainOffset)
		print 'jnt = '+jnt

		name = jnt.replace('_JNT', '')
		side = ''
		ctrlName = ''
		if jnt.startswith('l_') or jnt.startswith('r_'):
			side = jnt[:1]
			ctrlName = name[2:]

		print 'name = ' + name
		print 'side = ' + side
		print 'ctrlName = ' + ctrlName

		fkCtrl = rig_control( side=side, name=ctrlName, shape='box', modify=modify,
		                      lockHideAttrs=['tx','ty','tz'], targetOffset=jnt,
		                      constrain=pm.PyNode(jnt),
		                      constrainOffset=constrainOffset )

		controls.append(fkCtrl)
		i += 1


	return controls

