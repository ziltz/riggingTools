__author__ = 'Jerry'



import maya.cmds as mc
import pymel.core as pm



def defaultReturn(defaultVar, userVar, param):
	if param.get(userVar) == None:
		return defaultVar
	else:
		return param.get(userVar)

class rig_object(object):

	def __init__(self, object, **kwds):
		self.object = object
		try:
			self.type = pm.nodeType(object)
		except RuntimeError:
			print "Unknown Object"

	def getType(self):
		self.type = pm.nodeType(self.object)
		print "objectType = "+self.type+"\n"
		return self.type


class rig_transform(rig_object):
	def __init__(self, object, **kwds):
		self.name = defaultReturn('rig_transform_GRP','name', param=kwds)
		if mc.objExists(object):
			self.object = object
		else:
			self.object =  mc.group(em=True, n=self.name)
		self.targetObj = defaultReturn('','targetObj', param=kwds)
		self.parent = defaultReturn('','parent', param=kwds)
		self.translate = (0,0,0)
		self.rotation = (0,0,0)
		self.scale = (1,1,1)

		if mc.objExists(self.targetObj):
			self.moveTo()

		if mc.objExists(self.parent):
			mc.parent(self.object, self.parent)

		super(rig_transform, self).__init__(self.object, **kwds)

	def setTranslate(self, translate):
		self.translate = translate
		mc.setAttr(self.object  +".translateX", self.translate[0])
		mc.setAttr(self.object + ".translateY", self.translate[1])
		mc.setAttr(self.object + ".translateZ", self.translate[2])

	def setRotation (self, rotation):
		self.rotation = rotation
		mc.setAttr( ( "%s" +".rotateX") % self.object, self.rotation[0])
		mc.setAttr(self.object + ".rotateY", self.rotation[1])
		mc.setAttr(self.object + ".rotateZ", self.rotation[2])

	def setScale (self, scale):
		self.scale = scale
		mc.setAttr(self.object+".scaleX", self.scale[0])
		mc.setAttr(self.object + ".scaleY", self.scale[1])
		mc.setAttr(self.object + ".scaleZ", self.scale[2])

	def getTranslate(self):
		self.translate = mc.getAttr(self.object+".translate")[0]
		return self.translate

	def getRotation (self):
		self.rotation = mc.getAttr(self.object + ".rotate")[0]
		return self.rotation

	def getScale (self):
		self.scale = mc.getAttr(self.object + ".scale")[0]
		return self.scale

	def moveTo(self):
		if mc.objExists(self.targetObj):
			mc.delete(mc.parentConstraint(self.targetObj, self.object))
		else:
			mc.warning(self.targetObj+" doesn't exist")

	def group(self, origin=0, name='rig_transformOffset_GRP'):
		null = mc.group(em=True, n=name)
		if origin == 0:
			mc.delete(mc.parentConstraint(self.object, null))
		mc.parent(self.object, null)
		return null

class rig_control(rig_transform):

	def __init__(self, **kwds):
		self.name = defaultReturn('rig_CTRL','name', param=kwds)
		self.lockHideAttrs = defaultReturn(['sx','sy','sz','v'],'lockHideAttrs', param=kwds)
		self.showAttrs = defaultReturn([],'showAttrs', param=kwds)
		self.gimbal = 0
		self.pivot = 0
		self.con = ''
		self.offset = ''
		self.modify = defaultReturn(0,'modify', param=kwds)
		self.shape = 'circle'
		self.targetObj = defaultReturn('','targetObj', param=kwds)
		self.object = mc.circle(name = self.name)[0]

		self.setDefaultSettings()

		super(rig_control, self).__init__(self.offset,**kwds)


	def setDefaultSettings(self):
		for attr in self.lockHideAttrs:
			mc.setAttr(self.object+"."+attr, lock=True, keyable=False, channelBox=False)

		for attr in self.showAttrs:
			mc.setAttr(self.object + "." + attr, lock=False, keyable=True, channelBox=True)

		self.con = rig_transform(0, name=self.name.replace('_CTRL', 'Con_GRP'), parent=self.object ).object

		self.offset = rig_transform(0, name=self.name.replace('_CTRL', 'Offset_GRP') ).object
		mc.parent(self.object, self.offset)

		mods = []
		if self.modify > 0:
			for i in range(1, self.modify+1):
				mods.append(rig_transform(self.object).group(origin=1, name=self.name.replace('_CTRL', 'Modify'+str(i)+'_GRP') ))

			for i in range((len(mods)-1), 0, -1):
				mc.parent(mods[i], mods[i-1])

		self.modify = mods

		mc.parent(mods[0], self.offset)