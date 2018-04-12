__author__ = 'Jerry'

import maya.cmds as mc

import pymel.core as pm


from rig_utils import defaultReturn



class rig_transform(object):
	def __init__(self, object, **kwds):
		self.name = defaultReturn('rig_transform','name', param=kwds)
		self.type = defaultReturn('group', 'type', param=kwds)

		self.rotateOrder = defaultReturn('', 'rotateOrder', param=kwds)

		self.suffix = defaultReturn('GRP', 'suffix', param=kwds)

		if pm.objExists(object):
			self.object = object
		else:
			self.object = self._createTransform(self.type)

		self.target = defaultReturn('','target', param=kwds)
		self.parent = defaultReturn('','parent', param=kwds)
		self.child = defaultReturn('', 'child', param=kwds)

		if pm.objExists(self.child):
			pm.parent(self.child, self.object)

		offset = ''
		try:
			if pm.objExists(self.target):
				#offset = rig_transform(0, name='offsetTemp').object
				offset = mc.group(em=True, n="offsetTemp")
				pm.parent(self.object, offset)
				pm.delete(pm.parentConstraint(self.target, offset))
		except TypeError:
			offset = mc.group(em=True, n="offsetTemp")
			pm.parent(self.object, offset)
			pm.delete(pm.parentConstraint(self.target, offset))

		try :
			mc.parent(self.object, self.parent)
		except TypeError:
			pm.parent(self.object, self.parent)
		except ValueError:
			pm.parent(self.object, w=True)
		finally:
			if pm.objExists(offset):
				pm.delete(offset)
			else:
				offset = None

		#print 'object = ' + self.object
		#rig_object.__init__(self, self.object)
		#self.sup = super(rig_transform, self)
		#self.sup.__init__(self.object, **kwds)

	def _createTransform(self, _type):
		pm.select(cl=True)

		typeDict = {
			'group' : ( self._getTransform('_group') , "GRP" ) ,
			'locator' : ( self._getTransform('_locator'), "LOC" ),
			'joint': ( self._getTransform('_joint') , "JNT" )
		}

		obj=''
		self.suffix = (typeDict[_type])[1]
		try:
			for t in typeDict:
				if t is _type:
					obj = (typeDict[_type])[0]()
					break
		except KeyError:
			obj = (typeDict['group'])[0]()
			print 'No such type object in dictionary, making default group'

		return obj

	def _getTransform(self, transform):
		func = getattr(self, transform)
		return func

	def _group(self):
		return mc.group(em=True, n=self.name+"_GRP")

	def _locator (self):
		return mc.spaceLocator( n=self.name+"_LOC" )[0]

	def _joint (self):
		obj = ''
		if '_JNT' in self.name:
			obj = mc.joint(n=self.name)
		else:
			obj = mc.joint(n=self.name + "_JNT")
		
		if self.rotateOrder != '':
			pm.setAttr(pm.PyNode(obj).rotateOrder, self.rotateOrder)
		return obj

	def offsetGroup(self, origin=0, name=None):
		if name is None:
			offsetName = self.name+'Offset'
		else:
			offsetName = name
		if origin == 0 :
			group = rig_transform(0, name=offsetName, child=self.object, target=self.object)
		else:
			group = rig_transform(0, name=offsetName, child=self.object )
		return group

