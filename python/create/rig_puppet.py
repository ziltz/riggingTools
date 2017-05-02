__author__ = 'Jerry'



from rutils.rig_object import rig_object
from rutils.rig_utils import *
from make.rig_controls import *
from rutils.rig_transform import rig_transform


import pymel.core as pm
import maya.cmds as cmds
import glob, os

class puppet(rig_object):
	
	def __init__(self,  **kwds):

		self.character = defaultReturn('jerry', 'character', param=kwds)
		self.rigBound = defaultReturn(None, 'rigBound', param=kwds)

		self.charModule = importlib.import_module('char.' + self.character)
		print self.charModule

		#cmds.file(f=True, new=True)
		pm.newFile(f=True)
		pm.evaluationManager(mode='serial')

		pm.workspace(update=True)
		projectRoot = pm.workspace(q=True, rd=True) +'scenes/release/rigBound/'
		print ' project root '+projectRoot+' found'

		if self.rigBound is None:
			#projectRoot = pm.workspace(q=True, rd=True) + 'scenes/release/rigBound/'
			fileList = []
			os.chdir(projectRoot)
			for file in glob.glob("*.ma"):
				fileList.append(file)

			fileList.sort()
			latestFile = fileList[-1:][0]
			self.rigBound = projectRoot + latestFile
		else:
			self.rigBound = projectRoot + self.rigBound + '.ma'

		print 'rigBound file path = '+self.rigBound
		# import rigBound file
		try:
			#filePath = cmds.file(self.rigBound, f=True, ignoreVersion=True,
			# typ="mayaAscii", o=True)
			filePath = cmds.file(self.rigBound, i=True, ignoreVersion=True,
			                     ra = False, mergeNamespacesOnClash =False,
			                     typ="mayaAscii", loadReferenceDepth='none')

		except RuntimeError:
			print self.rigBound + ' file not found'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		# unparent skeleton
		skeleton = pm.parent(pm.listRelatives('skeleton_GRP', typ='joint'), w=True)

		self.globalCtrl = rig_control(name='global', colour='white', shape='arrows',
		                              con=0, showAttrs=['sx', 'sy','sz'])

		self.globalCtrl.gimbal = createCtrlGimbal( self.globalCtrl ).ctrl

		self.topNode = rig_transform(0, name=self.character + 'RigPuppetTop', child=self.globalCtrl.offset).object

		try:
			self.rigGrp = pm.parent('rig_GRP', self.globalCtrl.gimbal)[0]
		except:
			self.rigGrp = rig_transform(0, name='rig',
			                            parent=self.globalCtrl.gimbal).object

		try:
			self.rigModule = pm.parent('rigModules_GRP',
			                           self.globalCtrl.gimbal)[0]
		except:
			self.rigModule = rig_transform(0, name='rigModules',
			                               parent=self.globalCtrl.gimbal).object

		try:
			self.model = pm.parent('model_GRP', self.topNode)[0]
		except:
			self.model = rig_transform(0, name='model', parent=self.topNode).object

		try:
			self.rigModel = pm.parent('rigModel_GRP', self.model)[0]
		except:
			self.rigModel = rig_transform(0, name='rigModel', parent=self.model).object

		self.worldSpace = rig_transform(0, name= 'worldSpace',
		                                parent=self.globalCtrl.gimbal).object

		# create attributes on global ctrl
		pm.addAttr(self.globalCtrl.ctrl, ln='puppetSettings', at='enum',
		           enumName='___________',
		           k=True)
		self.globalCtrl.ctrl.puppetSettings.setLocked(True)

		# model and skeleton vis
		# model
		connectAttrToVisObj(self.globalCtrl.ctrl, 'modelVis', self.model,
		                    defaultValue=1)
		# skeleton
		pm.addAttr(self.globalCtrl.ctrl, longName='skeletonVis', at='long',
		           k=True, min=0,
		           max=1, defaultValue=0)
		self.globalCtrl.ctrl.skeletonVis.set(cb=True)
		# controls
		pm.addAttr(self.globalCtrl.ctrl, longName='controlsVis', at='long',
		           k=True, min=0,
		           max=1, defaultValue=1)
		self.globalCtrl.ctrl.controlsVis.set(cb=True)

		# referencing and selecting
		pm.addAttr(self.globalCtrl.ctrl, ln='model', at='enum',
		           enumName='Selectable:Reference',
		           k=True, defaultValue = 1)
		pm.addAttr(self.globalCtrl.ctrl, ln='skeleton', at='enum',
		           enumName='Selectable:Reference',
		           k=True, defaultValue = 1)

		# LOD vis
		pm.addAttr(self.globalCtrl.ctrl, ln='lodSetting', at='enum',
		           enumName='___________',
		           k=True)
		self.globalCtrl.ctrl.lodSetting.setLocked(True)
		pm.addAttr(self.globalCtrl.ctrl, ln='lodDisplay', at='enum',
		           enumName='Low:Mid:High',
		           k=True, defaultValue=0)

		lodModel = ['lowLOD_GRP', 'lowMidLOD_GRP', 'midLOD_GRP', 'midHighLOD_GRP',
		            'highLOD_GRP']

		for lod in lodModel:
			if pm.objExists(lod):
				lodGRP = pm.PyNode(lod)
				if 'low' in lod:
					pm.setDrivenKeyframe(lodGRP.visibility,
					                     cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=0,v=1)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=1, v=0)
				if 'mid' in lod:
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=0, v=0)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=1, v=1)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=2, v=0)
				if 'high' in lod:
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=0, v=0)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=0, v=0)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=2, v=1)
				if 'lowMid' in lod:
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=0, v=1)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=1, v=1)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=2, v=0)
				if 'midHigh' in lod:
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=0, v=0)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=1, v=1)
					pm.setDrivenKeyframe(lodGRP.visibility, cd=self.globalCtrl.ctrl.lodDisplay,
					                     dv=2, v=1)

		# scale global control
		bbox = self.model.boundingBox()
		width = bbox.width() * 0.15
		cvsGlobal = pm.PyNode(self.globalCtrl.ctrl + '.cv[:]')
		cvsGimbal = pm.PyNode(self.globalCtrl.gimbal + '.cv[:]')
		pm.scale(cvsGlobal, width, width, width )
		pm.scale(cvsGimbal, width/1.5, width/1.5, width/1.5)

		pm.delete( "|*RigBoundTop_GRP" )
		pm.hide(self.rigGrp, self.rigModel)

		self.prepareRig()

		self.createRigModules()

		self.finishRig()

		self.sup = super(puppet, self)
		self.sup.__init__(self.topNode, **kwds)

		pm.evaluationManager(mode='parallel')


	def prepareRig(self):
		print 'Prepare core rig'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()


		func = getattr(self.charModule, self.character+'PrepareRig')()

	def createRigModules(self):
		print 'Creating core rig modules'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()


		func = getattr(self.charModule, self.character + 'RigModules')()

	def finishRig(self):
		print 'Finishing core rig'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()


		# ik fk switches
		# FK = 0, IK = 10 on switch
		try:
			pm.addAttr(self.globalCtrl.ctrl, ln='ikFkSwitch', at='enum',
			           enumName='___________',
			           k=True)
			self.globalCtrl.ctrl.ikFkSwitch.setLocked(True)

			switchLoc = pm.PyNode('ikFkSwitch_LOC')
			attrs = pm.listAttr(switchLoc, ud=True)

			for a in attrs:
				locAttr = getattr(switchLoc, a)

				pm.addAttr(self.globalCtrl.ctrl, longName=a, at='float', k=True,
				           min=0,
				           max=10)

				globalCtrlAttr = getattr(self.globalCtrl.ctrl, a )
				pm.setDrivenKeyframe(locAttr, cd=globalCtrlAttr, dv=10,v=1)
				pm.setDrivenKeyframe(locAttr, cd=globalCtrlAttr, dv=0, v=0)

				pm.setAttr(globalCtrlAttr, 10)

		except pm.MayaNodeError:
			print 'ikFkSwitch_LOC does not exists !'


		# make skeleton and model reference
		if pm.objExists('model_GRP'):
			#geoList = rig_geoUnderGroupHierarchy('model_GRP')
			#for g in geoList:
			#	obj = pm.PyNode(g)
			#	pm.setAttr( obj.overrideEnabled, 1 )
			obj = pm.PyNode(self.model)
			pm.setAttr(obj.overrideEnabled, 1)
			pm.setDrivenKeyframe(obj.overrideDisplayType,
			                     cd=self.globalCtrl.ctrl.model, dv=0, v=0)
			pm.setDrivenKeyframe(obj.overrideDisplayType,
			                     cd=self.globalCtrl.ctrl.model, dv=1, v=2)

		# remove display layers
		displayLayers = pm.ls( type='displayLayer' )
		for layer in displayLayers:
			if layer.stripNamespace() not in 'defaultLayer':
				pm.delete(layer)

		func = getattr(self.charModule, self.character + 'Finish')()


# make default human puppet
def defaultRigPuppet(self, rig_puppet):

	defaultRig = rig_puppet()