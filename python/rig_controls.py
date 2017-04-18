__author__ = 'Jerry'


import sys
import maya.cmds as mc
import pymel.core as pm

from rig_utils import defaultReturn, defaultAppendReturn
from rig_transform import rig_transform
reload(sys.modules['rig_transform'])
from rig_transform import rig_transform

class rig_control(rig_transform):

	def __init__(self, **kwds):
		self.name = defaultReturn('rigControl','name', param=kwds)
		self.lockHideAttrs = defaultAppendReturn(['sx','sy','sz','v'],'lockHideAttrs', param=kwds)
		self.showAttrs = defaultReturn([],'showAttrs', param=kwds)
		self.gimbal = defaultReturn(0,'gimbal', param=kwds)
		self.pivot = defaultReturn(1,'pivot', param=kwds)
		self.con = defaultReturn(1,'con', param=kwds)
		self.offset = defaultReturn(1,'offset', param=kwds)
		self.modify = defaultReturn(0,'modify', param=kwds)
		self.shape = defaultReturn('circle','shape', param=kwds)
		self.parentOffset = defaultReturn('','parentOffset', param=kwds)
		self.targetOffset = defaultReturn('','targetOffset', param=kwds)
		self.object = pm.PyNode(mc.circle(name = self.name+'_CTRL')[0])
		self.parent = ''

		self.constrain = defaultReturn(0,'constrain', param=kwds)
		self.offsetConstrain = defaultReturn('','constrainOffset', param=kwds)

		self._setDefaultSettings()

		super(rig_control, self).__init__(self.object, parent=self.parent ,**kwds)

		if pm.objExists(self.offsetConstrain):
			pm.parentConstraint(self.offsetConstrain, self.offset, mo=True)

		if self.constrain:
			constrainList = self.constrain
			if type(self.constrain) == str:
				constrainList = [self.constrain]
			for con in constrainList:
				pm.parentConstraint( self.con, con, mo=True )

	def _setDefaultSettings(self):

		if self.con > 0:
			self.con = rig_transform(0, name=self.name+'Con', parent=self.object ).object

		if self.offset > 0:
			self.offset = rig_transform(0, name=self.name+'Offset', parent=self.parentOffset, target=self.targetOffset, child=self.object ).object
			self.parent = self.offset
			print 'Created offset group 1 '+self.offset

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

			pm.parent(mods[0], self.offset)

			lastMod = mods[-1:][0]
			self.parent = lastMod


		if self.pivot > 0:
			pivot = rig_control(name=self.name+'Pivot', parentOffset=self.object, targetOffset=self.object, con=0, pivot=0, lockHideAttrs=['rx','ry','rz'] )
			print 'Created offset group 3 ' + self.offset
			self.pivot = pivot.object
			pm.connectAttr(  self.pivot.translate, self.object.rotatePivot, f=True)
			pm.connectAttr(  self.pivot.scale, self.object.scalePivot, f=True)
			pm.addAttr(self.object, longName='pivotVis', type='long', k=False)
			self.object.pivotVis.set(cb=True)
			print 'offset group = '+str(pivot.offset)
			pm.connectAttr( self.object.pivotVis,  pivot.offset.visibility )

		if self.gimbal > 0:
			gimbal = rig_control( name=self.name+"Gimbal", parentOffset=self.object, targetOffset=self.object, con=0, pivot=0, child=self.con )
			self.gimbal = gimbal.object
			pm.addAttr(self.object, longName='gimbalVis', type='long', k=False)
			self.object.gimbalVis.set(cb=True)
			pm.connectAttr(self.object.gimbalVis, gimbal.offset.visibility)

		for at in self.lockHideAttrs:
			self.object.attr(at).setKeyable(False)
			self.object.attr(at).setLocked(True)

		for at in self.showAttrs:
			self.object.attr(at).setKeyable(True)
			self.object.attr(at).setLocked(False)

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
								print 'target 1 '+ta
								list.append(1)
								valueDict[t] = list
							else:
								print 'target 0 '+ta
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






