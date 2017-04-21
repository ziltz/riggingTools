__author__ = 'Jerry'


import sys
import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm

from rig_utils import *
from rig_transform import rig_transform
#reload(sys.modules['rig_transform'])
#from rig_transform import rig_transform

'''

shapes: pointer, pyramid, circle, arrows

'''
class rig_control(rig_transform):

	def __init__(self, **kwds):
		self.name = defaultReturn('rigControl','name', param=kwds)
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
		self.parent = ''

		self.constrain = defaultReturn(0,'constrain', param=kwds)
		self.offsetConstrain = defaultReturn('','constrainOffset', param=kwds)

		self._setDefaultSettings()

		self.sup = super(rig_control, self)
		self.sup.__init__(self.ctrl, parent=self.parent ,**kwds)

		if pm.objExists(self.offsetConstrain):
			pm.parentConstraint(self.offsetConstrain, self.offset, mo=True)

		if self.constrain:
			constrainList = self.constrain
			if type(self.constrain) is str:
				constrainList = [self.constrain]
			for con in constrainList:
				print 'self.con = '+self.con
				print 'con = ' + con
				pm.parentConstraint( self.con, con, mo=True )

	def _setDefaultSettings(self):

		if self.con > 0:
			self.con = rig_transform(0, name=self.name+'Con', parent=self.ctrl ).object

		if self.offset > 0:
			self.offset = rig_transform(0, name=self.name+'Offset', parent=self.parentOffset, target=self.targetOffset, child=self.ctrl ).object
			self.parent = self.offset

		mods = []
		if self.modify > 0:
			modParent = ''
			for i in range(1, self.modify+1):
				modParent = rig_transform(0, name=self.name+'Modify'+str(i),target=self.offset, parent=modParent).object
				mods.append(modParent)

			if len(mods) == 1:
				self.modify = mods[0]
			else:
				self.modify = mods

			mc.parent(mods[0], self.offset)

			lastMod = mods[-1:][0]
			self.parent = lastMod


		if self.pivot > 0:
			self.pivot = rig_control(name=self.name+'Pivot', parentOffset=self.ctrl, targetOffset=self.ctrl, con=0, pivot=0, lockHideAttrs=['rx','ry','rz'] ).object
			pm.connectAttr(  self.pivot.translate, self.ctrl.rotatePivot, f=True)
			pm.connectAttr(  self.pivot.scale, self.ctrl.scalePivot, f=True)
			connectAttrToVisObj( self.ctrl, 'pivotVis', self.pivot.getShape() )
			#pm.addAttr(self.ctrl, longName='pivotVis', at='long', k=False, min=0,
			#  max=1)
			#self.ctrl.pivotVis.set(cb=True)
			#pm.connectAttr( self.ctrl.pivotVis,  self.pivot.getShape().visibility )

		if self.gimbal > 0:
			self.gimbal = rig_control( name=self.name+"Gimbal", parentOffset=self.ctrl, targetOffset=self.ctrl, con=0, pivot=0, child=self.con ).ctrl
			pm.addAttr(self.ctrl, longName='gimbalVis', at='long', k=False, min=0, max=1)
			self.ctrl.gimbalVis.set(cb=True)
			pm.connectAttr(self.ctrl.gimbalVis, self.gimbal.getShape().visibility)

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
		ctrl = mc.curve(n=self.name+'_CTRL', d=1,
		                  p=[(0, 0, 1), (0, 0, -1), (0, 2, 0), (0, -2, 0), (0, 0, -1), (2, 0, 0), (-2, 0, 0),
		                     (0, 0, -1)], k=[0, 1, 2, 3, 4, 5, 6, 7])
		#mc.rotate(0, -90, 0, r=True, os=True)
		mc.setAttr(ctrl+'.scaleZ', 5)
		mc.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
		return ctrl

	def circle(self):
		return mc.circle(name=self.name + '_CTRL', ch=False, nr=[0, 1, 0])[0]

	def pyramid(self):
		ctrl = mc.curve(n=self.name + '_CTRL', d=1,
		                  p=[(0, 2, 0), (1, 0, -1), (-1, 0, -1), (0, 2, 0), (-1, 0, 1), (1, 0, 1), (0, 2, 0),
		                     (1, 0, -1), (1, 0, 1), (-1, 0, 1),
		                     (-1, 0, -1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

		mc.makeIdentity(ctrl,apply=True, t=1, r=1, s=1, n=0)
		return ctrl

	def arrows(self):
		ctrl = mc.curve(n= self.name+"_CTRL", d=1,
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

		ctrlName = self.name+'_CTRL'
		ctrl = mm.eval('curve -n ' + ctrlName + ' -d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 ;')
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

		ctrlName = jnt.replace('_JNT', '')
		fkCtrl = rig_control( name=ctrlName, shape='box', modify=modify,
		                      lockHideAttrs=['tx','ty','tz'], targetOffset=jnt,
		                      constrain=jnt, constrainOffset=constrainOffset )

		controls.append(fkCtrl)
		i += 1


	return controls

