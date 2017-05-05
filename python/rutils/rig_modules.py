


from rig_transform import rig_transform

import pymel.core as pm

class rig_module(object):

	def __init__(self, name):

		self.side = ''
		print name
		if name.startswith('l_'):
			self.side = 'l'
		if name.startswith('r_'):
			self.side = 'r'

		self.top = pm.PyNode(rig_transform(0, name=name+'Module').object)

		self.controls = pm.PyNode(rig_transform(0, name=name+'Controls',
		                                        parent=self.top).object)
		self.skeleton = pm.PyNode(rig_transform(0, name=name+'Skeleton',
		                                        parent=self.top).object)
		self.parts = pm.PyNode(rig_transform(0, name=name+'Parts',
		                                     parent=self.top).object)

		pm.hide(self.parts)

		pm.addAttr(self.top, longName='skeletonVis', at='long', k=True, min=0,
		           max=1)
		pm.connectAttr(self.top.skeletonVis, self.skeleton.visibility)

		pm.addAttr(self.top, longName='controlsVis', at='long', k=True, min=0,
		           max=1)
		pm.connectAttr(self.top.controlsVis, self.controls.visibility)

		pm.addAttr(self.top, longName='ikFkSwitch', at='long', k=True, min=0,
		           max=1)


		if pm.objExists('global_CTRL'):
			globalCtrl = pm.PyNode('global_CTRL')
			pm.connectAttr(globalCtrl.skeletonVis, self.top.skeletonVis)
			pm.connectAttr(globalCtrl.controlsVis, self.top.controlsVis)
			pm.setAttr(self.skeleton.overrideEnabled, 1)
			pm.setDrivenKeyframe(self.skeleton.overrideDisplayType,
			                     cd=globalCtrl.skeleton, dv=0, v=0)
			pm.setDrivenKeyframe(self.skeleton.overrideDisplayType,
			                     cd=globalCtrl.skeleton, dv=1, v=2)

		self.controlsList = []
		self.skeletonList = []
		self.partsList = []

		rigModule = 'rigModules_GRP'
		if pm.objExists(rigModule):
			pm.parent(self.top, rigModule)
			pm.addAttr(rigModule, longName=name+'Module', at='long', k=True,
			           min=0, max=1, dv=1)
			pm.connectAttr( rigModule+'.'+name+'Module', self.top.visibility  )



