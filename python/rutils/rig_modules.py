


from rig_transform import rig_transform

import pymel.core as pm

class rig_module(object):

	def __init__(self, name):
		self.top = rig_transform(0, name=name+'Module').object

		self.controls = rig_transform(0, name=name+'Controls', parent=self.top).object
		self.skeleton = rig_transform(0, name=name+'Skeleton', parent=self.top).object
		self.parts = rig_transform(0, name=name+'Parts', parent=self.top).object

		self.controlsList = []
		self.skeletonList = []
		self.partsList = []

		if pm.objExists('rigModule_GRP'):
			pm.parent(self.top, 'rigModule_GRP')