__author__ = 'Jerry'



from rutils.rig_object import rig_object
from rutils.rig_utils import *
from make.rig_controls import rig_control
from rutils.rig_transform import rig_transform


import pymel.core as pm
import maya.cmds as cmds


class puppet(rig_object):
	
	def __init__(self, rigBound=None, **kwds):

		self.character = defaultReturn('jerry', 'character', param=kwds)

		self.charModule = importlib.import_module('char.' + self.character)
		print self.charModule

		#cmds.file(f=True, new=True)
		pm.newFile(f=True)

		pm.workspace(update=True)
		projectRoot = pm.workspace(q=True, rd=True) +'/release/rigBound/'

		self.rigBound = projectRoot + rigBound + '.ma'

		print 'rigBound file path = '+self.rigBound
		# import rigBound file
		try:
			filePath = cmds.file(self.rigBound, f=True, ignoreVersion=True, typ="mayaAscii", o=True)
		except RuntimeError:
			print self.rigBound + ' file not found'

		# unparent skeleton
		skeleton = pm.parent(pm.listRelatives('skeleton_GRP', typ='joint'), w=True)

		self.globalCtrl = rig_control(name='global', colour='white', shape='arrows',
		                              con=0,
		                              gimbal=1, showAttrs=['sx', 'sy','sz'])

		self.topNode = rig_transform(0, name=self.character + 'RigPuppetTop', child=self.globalCtrl.offset).object

		try:
			self.rigGrp = pm.parent('rig_GRP', self.globalCtrl.gimbal)[0]
		except:
			self.rigGrp = rig_transform(0, name='rig', parent=self.globalCtrl.gimbal).object

		try:
			self.rigModule = pm.parent('rigModule_GRP', self.globalCtrl.gimbal)[0]
		except:
			self.rigModule = rig_transform(0, name='rigModule', parent=self.globalCtrl.gimbal).object

		try:
			self.model = pm.parent('model_GRP', self.topNode)[0]
		except:
			self.model = rig_transform(0, name='model', parent=self.topNode).object

		try:
			self.rigModel = pm.parent('rigModel_GRP', self.model)[0]
		except:
			self.rigModel = rig_transform(0, name='rigModel', parent=self.model).object

		# create attributes on global ctrl
		pm.addAttr(self.globalCtrl.ctrl, ln='puppetSettings', at='enum',
		           enumName='___________',
		           k=True)
		self.globalCtrl.ctrl.puppetSettings.setLocked(True)

		# model and skeleton vis
		connectAttrToVisObj(self.globalCtrl.ctrl, 'modelVis', self.model,
		                    defaultValue=1)
		pm.addAttr(self.globalCtrl.ctrl, longName='skeletonVis', at='long',
		           k=True, min=0,
		           max=1, defaultValue=1)
		self.globalCtrl.ctrl.skeletonVis.set(cb=True)

		# ik fk switches
		pm.addAttr(self.globalCtrl.ctrl, ln='ikFkSwitch', at='enum',
		           enumName='___________',
		           k=True)
		self.globalCtrl.ctrl.ikFkSwitch.setLocked(True)


		# scale global control
		bbox = self.model.boundingBox()
		width = bbox.width() * 0.3
		cvsGlobal = pm.PyNode(self.globalCtrl.ctrl + '.cv[:]')
		cvsGimbal = pm.PyNode(self.globalCtrl.gimbal + '.cv[:]')
		pm.scale(cvsGlobal, width, width, width )
		pm.scale(cvsGimbal, width/1.5, width/1.5, width/1.5)

		pm.delete( "|*RigBoundTop_GRP" )
		pm.hide(self.rigGrp)

		self.prepareRig()

		self.createRigModules()

		self.finishRig()

		self.sup = super(puppet, self)
		self.sup.__init__(self.topNode, **kwds)

	def prepareRig(self):
		print 'Prepare core rig'

		func = getattr(self.charModule, self.character+'PrepareRig')()

	def createRigModules(self):
		print 'Creating core rig modules'

		func = getattr(self.charModule, self.character + 'RigModules')()

	def finishRig(self):
		print 'Finishing core rig'

		func = getattr(self.charModule, self.character + 'Finish')()



def defaultRigPuppet(self, rig_puppet):

	defaultRig = rig_puppet()