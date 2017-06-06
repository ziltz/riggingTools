__author__ = 'Jerry'



from rutils.rig_object import rig_object
from rutils.rig_utils import *
from make.rig_controls import *
from rutils.rig_transform import rig_transform


import pymel.core as pm
import maya.cmds as cmds
import glob, os

class puppet(object):
	
	def __init__(self,  **kwds):

		self.character = defaultReturn('jerry', 'character', param=kwds)
		self.rigBound = defaultReturn(None, 'rigBound', param=kwds)

		pm.newFile(f=True)

		print "START: rigPuppet build "+self.character
		pm.timer(s=True)
		pm.undoInfo(state=False)
		pm.evaluationManager(mode='serial')

		try:
			self.charModule = importlib.import_module('char.' + self.character+'Puppet')
			print self.charModule

			pm.workspace(update=True)
			projectRoot = pm.workspace(q=True, rd=True) +'scenes/release/rigBound/'
			print ' project root '+projectRoot+' found'

			if self.rigBound is None:
				#projectRoot = pm.workspace(q=True, rd=True) + 'scenes/release/rigBound/'
				fileList = []
				os.chdir(projectRoot)
				for f in glob.glob("*.ma"):
					fileList.append(f)

				fileList.sort()
				latestFile = fileList[-1:][0]
				self.rigBound = projectRoot + latestFile
			#else:
			#	self.rigBound = projectRoot + self.rigBound + '.ma'

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
			except Exception as e:
				self.rigGrp = rig_transform(0, name='rig',
				                            parent=self.globalCtrl.gimbal).object
				pm.addAttr(self.rigGrp, longName='worldScale', at='float',
				           k=True, min=0, defaultValue=1)
				self.rigGrp.worldScale.set(cb=True)



			try:
				self.rigModule = pm.parent('rigModules_GRP',
				                           self.globalCtrl.gimbal)[0]
			except Exception as e:
				self.rigModule = rig_transform(0, name='rigModules',
				                               parent=self.globalCtrl.gimbal).object

			try:
				self.model = pm.parent('model_GRP', self.topNode)[0]
			except Exception as e:
				self.model = rig_transform(0, name='model', parent=self.topNode).object

			try:
				self.rigModel = pm.parent('rigModel_GRP', self.model)[0]
			except Exception as e:
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
			self.bbox = self.model.boundingBox()
			width = self.bbox.width() * 0.3
			cvsGlobal = pm.PyNode(self.globalCtrl.ctrl + '.cv[:]')
			cvsGimbal = pm.PyNode(self.globalCtrl.gimbal + '.cv[:]')
			pm.scale(cvsGlobal, width, width, width )
			pm.scale(cvsGimbal, width/1.5, width/1.5, width/1.5)

			# make display toggle
			self.displayTransform = pm.circle(name='displayModulesToggleControl',
			                             sw=360, nr=(0, 1, 0), ch=0)[0]
			pm.delete(self.displayTransform.getShape())

			displayCurves = pm.PyNode(
				pm.textCurves(f="Quartz|wt:50|sz:28|sl:n|st:100", t="Display", ch=0,
				              fzn=True)[0])
			pm.setAttr(displayCurves.translateX, -1.7)
			pm.move(0, 0, 0, displayCurves.rotatePivot, p=True, ws=True)
			pm.move(0, 0, 0, displayCurves.scalePivot, p=True, ws=True)

			pm.move( 0,(self.bbox.height()+(self.bbox.height()*0.1)),0,
			         displayCurves, r=True )
			displayScale = self.bbox[1][0]/4
			pm.scale( displayCurves, displayScale,displayScale,displayScale  )

			allCurves = pm.listRelatives(displayCurves, ad=True, c=True,
			                             type="nurbsCurve")
			parentCurves = []
			for crv in allCurves:
				parentTransform = pm.listRelatives(crv, p=True)[0]
				pm.parent(parentTransform, w=True)
				pm.makeIdentity(parentTransform, apply=True, t=1, r=1, s=1)
				pm.parent(crv, self.displayTransform, shape=True, add=True)
				parentCurves.append(parentTransform)

			pm.dgdirty(allPlugs=True)
			pm.refresh()
			pm.delete(parentCurves, s=False)
			pm.delete( displayCurves )
			pm.parent( self.displayTransform, self.globalCtrl.ctrl )
			for at in ['translateX','translateY','translateZ',
			             'rotateX', 'rotateY', 'rotateZ',
			             'scaleX', 'scaleY', 'scaleZ', 'visibility']:
				#getattr(self.displayTransform, at).set(k=False)
				self.displayTransform.attr(at).set(k=False)
				self.displayTransform.attr(at).setLocked(True)

			try:
				pm.delete( "|*RigBoundTop_GRP" )
			except pm.MayaNodeError:
				print 'RigBound top node does not exist'

			pm.connectAttr(self.globalCtrl.ctrl+'.scaleX', self.rigGrp.worldScale)
			pm.hide(self.rigGrp, self.rigModel)

			pm.addAttr(self.globalCtrl.ctrl, ln='rigAuthor', at='enum',
			           enumName='Jerry:Lee', k=False, dv=0)

			self.prepareRig()

			self.createRigModules()

			self.finishRig()

			pm.select(cl=True)

			#self.sup = super(puppet, self)
			#self.sup.__init__(self.topNode, **kwds)

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
			print "END: rigPuppet built in %g seconds" % mayaTimer
			print ''


	def prepareRig(self):
		print 'Prepare core rig'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()


		getattr(self.charModule, self.character+'PrepareRig')()

	def createRigModules(self):
		print 'Creating core rig modules'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()


		getattr(self.charModule, self.character + 'RigModules')()

	def finishRig(self):
		print 'Finishing core rig'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		# add controls to set and display toggle
		pm.select(cl=True)
		controlSet = pm.sets( n=self.character+'RigPuppetControlSet' )
		moduleAttrs = pm.listAttr(self.rigModule, ud=True, st='*Module')
		allControls = []
		for at in moduleAttrs:
			sectionName = at.replace( 'Module', '' )
			moduleName = at+'_GRP'
			module = pm.PyNode( moduleName )
			modGroups = pm.listRelatives( module, c=True )
			for grp in modGroups:
				if 'Controls' in grp.stripNamespace():
					allCurves = pm.listRelatives(grp, ad=True,c=True, type="nurbsCurve")
					for ctrl in allCurves:
						allControls.append( pm.listRelatives(ctrl, p=True)[0] )

					pm.addAttr(self.displayTransform, ln=sectionName, at='enum',
					           enumName='None:Primary', k=False, dv=1)
					self.displayTransform.attr(sectionName).set(cb=True)
					pm.connectAttr( self.displayTransform.attr(sectionName),
					                grp.lodVisibility )

		pm.select(cl=True)
		controlSet.addMembers(allControls)

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

		getattr(self.charModule, self.character + 'Finish')()


# make default human puppet
def defaultRigPuppet(self, rig_puppet):

	defaultRig = rig_puppet()