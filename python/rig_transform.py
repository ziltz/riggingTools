__author__ = 'Jerry'


import maya.cmds as mc
import pymel.core as pm


from rig_utils import defaultReturn
from rig_object import rig_object

class rig_transform(rig_object):
	def __init__(self, object, **kwds):
		self.name = defaultReturn('rig_transform','name', param=kwds)
		self.type = defaultReturn('group', 'type', param=kwds)

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


		offset = None
		if pm.objExists(self.target):
			offset = rig_transform(0).object
			print self.object+' parent to offset target '+'\n'
			print self.target+' target to '+ offset+'\n'
			pm.parent(self.object, offset)
			pm.delete(pm.parentConstraint(self.target, offset))

		try :
			print self.object +' parent to '+self.parent+'\n'
			pm.parent(self.object, self.parent)
		except:
			print self.object+ ' parent to world '+'\n'
			pm.parent(self.object, w=True)
		finally:
			try:
				pm.delete(offset)
			except:
				offset = None

		super(rig_transform, self).__init__(self.object, **kwds)

	def _createTransform(self, _type):
		typeDict = {
			'group' : (mc.group(em=True, n=self.name+"_GRP"), "GRP" ) ,
			'locator' : ( mc.spaceLocator( n=self.name+"_LOC" )[0], "LOC" )
		}

		obj = (typeDict['group'])[0]
		self.suffix = (typeDict[_type])[1]
		try:
			for t in typeDict:
				if t is _type:
					obj = (typeDict[_type])[0]
				else:
					try:
						mc.delete( (typeDict[t])[0] )
					except:
						pm.warning(typeDict[t][0]+' does not exist')

		except KeyError:
			print 'No such type object in dictionary, making default group'
			for t in typeDict:
				if t is not 'group':
					try:
						mc.delete( (typeDict[t])[0] )
					except:
						pm.warning(typeDict[t][0]+' does not exist')

		return pm.PyNode(obj)

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

