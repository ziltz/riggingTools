__author__ = 'Jerry'



from rutils.rig_object import rig_object
from rutils.rig_utils import *
from make.rig_controls import *
from rutils.rig_transform import rig_transform
from create.rig_skeleton import *

import pymel.core as pm
import maya.cmds as cmds
import glob, os, collections

'''

Build rigBound from model and skeleton

Stages :-

Init:
Load model and skeleton and build rig connections

Prepare
Do anything to model/skeleton

RigModules
Load maya buildScene
Build any rigModules needed including character specific
Load skinning/constraints

Finalise
Finish building rigBound

'''

class bound(rig_object):
	
	def __init__(self,  **kwds):

		self.character = defaultReturn('jerry', 'character', param=kwds)
		self.model = defaultReturn(None, 'model', param=kwds)
		self.skeleton = defaultReturn(None, 'skeleton', param=kwds)
		
		
		self.mayaScene = self.character + '_rigBound_buildScene'

		self.makeBiped = defaultReturn(False, 'biped', param=kwds)
		self.makeQuadruped = defaultReturn(False, 'quadruped', param=kwds)

		pm.newFile(f=True)

		print "START: rigBound build "+self.character
		pm.timer(s=True)
		pm.undoInfo(state=False)
		pm.evaluationManager(mode='serial')

		try:
			self.charModule = importlib.import_module('char.' + self.character+'Bound')
			print self.charModule

			pm.workspace(update=True)
			projectRoot = pm.workspace(q=True, rd=True) +'scenes/release/'
			print ' project root '+projectRoot+' found'

			modelPath = projectRoot+'model/'
			if self.model is None:
				fileList = []
				os.chdir(modelPath)
				for f in glob.glob("*.ma"):
					fileList.append(f)

				fileList.sort()
				latestFile = fileList[-1:][0]
				self.model = modelPath + latestFile
			else:
				self.model = modelPath + self.model + '.ma'

			print 'model file path = '+self.rigBound
			# import model file
			try:
				filePath = cmds.file(self.model, i=True, ignoreVersion=True,
				                     ra = False, mergeNamespacesOnClash =False,
				                     typ="mayaAscii", loadReferenceDepth='none')
			except RuntimeError:
				print self.model + ' file not found'

			cmds.dgdirty(allPlugs=True)
			cmds.refresh()
			
			skeletonPath = projectRoot + 'skeleton/'
			if self.skeleton is None:
				fileList = []
				os.chdir(skeletonPath)
				for f in glob.glob("*.ma"):
					fileList.append(f)
				
				fileList.sort()
				latestFile = fileList[-1:][0]
				self.skeleton = skeletonPath + latestFile
			else:
				self.skeleton = skeletonPath + self.skeleton + '.ma'
			
			print 'skeleton file path = ' + self.skeleton
			# import model file
			try:
				filePath = cmds.file(self.skeleton, i=True, ignoreVersion=True,
				                     ra=False, mergeNamespacesOnClash=False,
				                     typ="mayaAscii", loadReferenceDepth='none')
			except RuntimeError:
				print self.skeleton + ' file not found'
			
			cmds.dgdirty(allPlugs=True)
			cmds.refresh()

			self.characterModel = pm.ls("|*GRP")
			
			# unparent skeleton
			skeleton = pm.listRelatives('skeleton_GRP', typ='joint')

			self.globalCtrl = rig_control(name='global', colour='white', shape='arrows',
			                              con=0, showAttrs=['sx', 'sy','sz'])

			self.topNode = rig_transform(0, name=self.character + 'RigBoundTop', child=self.globalCtrl.offset).object

			self.rigGrp = rig_transform(0, name='rig',
				                            parent=self.globalCtrl.ctrl).object
			pm.addAttr(self.rigGrp, longName='worldScale', at='float',
			           k=True, min=0, defaultValue=1)
			self.rigGrp.worldScale.set(cb=True)
			pm.connectAttr( self.globalCtrl.ctrl.scaleX, self.rigGrp.worldScale )

			self.modelGrp = rig_transform(0, name='model', parent=self.topNode).object

			self.rigModel = rig_transform(0, name='rigModel', parent=self.model).object

			self.skeleton = rig_transform(0, name='skeleton', parent=self.globalCtrl.ctrl, child=skeleton).object


			# create attributes on global ctrl
			pm.addAttr(self.globalCtrl.ctrl, ln='boundSettings', at='enum',
			           enumName='___________',
			           k=True)
			self.globalCtrl.ctrl.boundSettings.setLocked(True)

			# model and skeleton vis
			# model
			connectAttrToVisObj(self.globalCtrl.ctrl, 'modelVis', self.modelGrp,
			                    defaultValue=1)
			# skeleton
			connectAttrToVisObj(self.globalCtrl.ctrl, 'skeletonVis', self.skeleton,
			                    defaultValue=1)

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
					pm.parent( lodGRP, self.modelGrp )
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
			self.bbox = self.modelGrp.boundingBox()
			width = self.bbox.width() * 0.3
			cvsGlobal = pm.PyNode(self.globalCtrl.ctrl + '.cv[:]')
			pm.scale(cvsGlobal, width, width, width )

			try:
				pm.delete( "|*RigSkeletonTop_GRP" )
			except pm.MayaNodeError:
				print 'RigSkeleton top node does not exist'
				
			pm.hide(self.rigGrp, self.rigModel)

			self.prepareRig()

			self.createRigModules()

			self.finishRig()

			pm.select(cl=True)

			self.sup = super(bound, self)
			self.sup.__init__(self.topNode, **kwds)

		except Exception as e:
			print "*************************************"
			print "=========== Error happened ========="
			raise
		finally:
			pm.evaluationManager(mode='parallel')

			mayaTimer = pm.timer(e=True)

			pm.undoInfo(state=True)
			print ''
			print ''
			print "END: rigBound built in %g seconds" % mayaTimer
			print ''


	def prepareRig(self):
		print 'Prepare core rig'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		getattr(self.charModule, self.character+'PrepareRig')()

	def createRigModules(self):
		print 'Creating core rig modules'

		# import maya build scene
		importLatestAsset(self.mayaScene, type='mayaScene')

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()


		getattr(self.charModule, self.character + 'RigModules')()

	def finishRig(self):
		print 'Finishing core rig'
		
		# remove display layers
		displayLayers = pm.ls(type='displayLayer')
		for layer in displayLayers:
			if layer.stripNamespace() not in 'defaultLayer':
				pm.delete(layer)
		
		cmds.dgdirty(allPlugs=True)
		cmds.refresh()
		
		getattr(self.charModule, self.character + 'Finish')()


'''

do checks before releasing

'''
def rig_boundChecks():
	rootJoint = cmds.listRelatives('skeleton_GRP', typ='joint')[0]
	listJoints = listSkeletonHierarchy(rootJoint)
	print listJoints
	duplicates = [item for item, count in collections.Counter(listJoints).items() if count > 1]

	if len(duplicates) > 0:
		pm.warning( 'Found duplicate non-unique joint namings! ' )
		print duplicates
