__author__ = 'Jerry'


import pymel.core as pm

class rig_object(object):

	def __init__(self, object, **kwds):
		try:
			self.object = pm.PyNode(object)
			self.name = str(self.object)
		except pm.MayaObjectError:
			print ("Rig Object "+object+" doesn't exist")
			self.object = ''
			self.name = ''

