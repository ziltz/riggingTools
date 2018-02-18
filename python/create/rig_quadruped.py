__author__ = 'Jerry'


from make.rig_ik import *
from make.rig_controls import *

from rutils.rig_chain import *
from rutils.rig_nodes import *
from rutils.rig_math import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm
import string

ABC = list(string.ascii_uppercase)



class rig_quadruped(object):

	def __init__(self, **kwds):

		self.globalCtrl = pm.PyNode('global_CTRL')

		self.switchLoc = 'ikFkSwitch_LOC'

		self.clavicleName = 'clavicleJA_JNT'
		self.scapula = 'scapulaJA_JNT'

		self.armName = 'armJA_JNT'
		self.elbowName = 'elbowJA_JNT'
		self.handName = 'handJA_JNT'
		self.handFngName = 'handJB_JNT'

		self.fngThumb = 'fngThumbJA_JNT'
		self.fngIndex = 'fngIndJA_JNT'
		self.fngMid = 'fngMidJA_JNT'
		self.fngRing = 'fngRingJA_JNT'
		self.fngPinky = 'fngPnkyJA_JNT'

		self.legName = 'legJA_JNT'
		self.kneeName = 'kneeJA_JNT'
		self.footName = 'footJA_JNT'
		self.footBName = 'footJB_JNT'
		self.toesName = 'toesJA_JNT'

		self.toeThumb = 'toeThumbJA_JNT'
		self.toeIndex = 'toeIndJA_JNT'
		self.toeMid = 'toeMidJA_JNT'
		self.toeRing = 'toeRingJA_JNT'
		self.toePinky = 'toePnkyJA_JNT'

		self.elbowAxis = 'rx'
		self.kneeAxis = 'rz'

		self.armJoints = []
		self.legJoints = []

		# values : poleVector, hand, fk, fingers
		self.armControls = {}
		self.armTop = ''
		self.shoulderControl = None

		# values : poleVector, foot, fk, toes
		self.legControls = {}
		self.legTop = ''
		self.pelvisControl = None

		self.spineFullBodyCtrl = None
		self.spineUpperCtrl = None
		self.spineLowerCtrl = None

		self.spineConnection = 'spineJF_JNT'
		self.centerConnection = 'spineJA_JNT'
		self.pelvisConnection = 'pelvisJA_JNT'

		self.spineModule = ''
		self.neckModule = ''
		self.headModule = ''
		
		self.shoulderModule = ''
		self.armModule = ''
		self.legModule = ''


	def create(self):

		self.spine()

		self.neck()

		self.head()

		for s in ['l', 'r']:
			self.shoulder(s)
			self.arm(s)
			self.leg(s)

		self.pelvis()


		return


	'''
	chains[0] = result
	chains[1] = ik
	chains[2] = fk
	'''
	def connectIkFkSwitch(self, chains, module, name='rigSwitch' ):
		# switch

		switchParent = module.parts
		if pm.objExists('rig_GRP'):
			switchParent = 'rig_GRP'

		if not pm.objExists(self.switchLoc):
			self.switchLoc = pm.PyNode(rig_transform(0, type='locator',
			                                     name='ikFkSwitch',
			                               parent=switchParent).object)

		pm.addAttr(self.switchLoc, longName=name, at='float', k=True, min=0,
		           max=1)

		# blend joints together

		for i in range(0, len(chains[0])):

			con = pm.orientConstraint( chains[1][i], chains[2][i], chains[0][i] )
			targetsOrient = con.getWeightAliasList()
			pm.setAttr(con.interpType, 2)

			con = pm.pointConstraint(chains[1][i], chains[2][i], chains[0][i])
			targetsPoint = con.getWeightAliasList()

			pm.connectAttr( self.switchLoc+'.'+name, targetsOrient[0] )
			pm.connectAttr(self.switchLoc + '.' + name, targetsPoint[0])
			connectReverse(input=(self.switchLoc+'.'+name, self.switchLoc+'.'+name, 0),
			               output=(targetsOrient[1], targetsPoint[1], 0))

			'''
			blendColors(chains[1][i], chains[2][i], chains[0][i], name=name+str(i),
			            driverAttr=self.switchLoc+'.'+name,
			            attribute='rotate')

			blendColors(chains[1][i], chains[2][i], chains[0][i], name=name + str(i),
			            driverAttr=self.switchLoc + '.' + name,
			            attribute='translate')
			'''

		switchAttr = getattr(self.switchLoc, name)
		pm.connectAttr( switchAttr, module.top.ikFkSwitch  )



	def spine(self,  ctrlSize=1 ):
		name = 'spine'

		module = rig_module(name)
		self.spineModule = module

		pm.parent(self.centerConnection, module.skeleton)

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		'''
		string $spline = cMS_makeSpline($baseName, $nControls, $controlType, $detail, $nRead, $readType, $ctrls, $reads, $bConstrainMid) ;
	string $spline = cMS_makeSpline($baseName, $nControls, $controlType, 8, 0, "null", $ctrls, $reads, 1) ;

		'''

		# full body control
		spineFullBody = rig_control(name='spineFullBody', shape='box', modify=1,
		                            scale=ctrlSize,
		                         colour='yellow', parentOffset=module.controls, rotateOrder=2)
		pm.delete(pm.pointConstraint( 'spineJA_JNT', spineFullBody.offset ))
		self.spineFullBodyCtrl = spineFullBody
		spineTop = pm.xform('spineJF_JNT', translation=True, query=True, ws=True)
		spineBot = pm.xform('spineJA_JNT', translation=True, query=True, ws=True)
		spineDistance = lengthVector(spineBot, spineTop)
		pm.scale(pm.PyNode(spineFullBody.ctrl+'.cv[:]'), 0.5, 1, 0.5)
		pm.rotate( pm.PyNode(spineFullBody.ctrl+'.cv[:]') , 90, 0,0,r=True,os=True )

		pm.move(pm.PyNode( spineFullBody.ctrl+'.cv[:]' ), [0, spineDistance/1.5, 0],
		        relative=True,
		        worldSpace=True)
		spineFullBody.gimbal = createCtrlGimbal(spineFullBody)
		spineFullBody.pivot = createCtrlPivot(spineFullBody)


		

		# spine lower
		spineLower = rig_control(name='spineLower', shape='box', modify=1,
		                         targetOffset='spineJB_JNT',
		                         constrainOffset=spineFullBody.con, scale=ctrlSize,
		                         colour='yellow', parentOffset=module.controls, rotateOrder=2)
		spineLower.gimbal = createCtrlGimbal(spineLower)
		spineLower.pivot = createCtrlPivot(spineLower)

		self.spineLowerCtrl = spineLower

		constrainObject(spineLower.modify,
		                [spineLower.offset, 'worldSpace_GRP'],
		                spineLower.ctrl, ['fullBody', 'world'],
		                type='parentConstraint')

		pm.parentConstraint( spineLower.con, self.centerConnection, mo=True )

		pm.move(pm.PyNode(spineLower.ctrl + '.cv[:]'),
		        [0, 0, 0.5],
		        relative=True,
		        worldSpace=True)
		pm.scale(pm.PyNode(spineLower.ctrl + '.cv[:]'), 1, 0.7, 1)

		# spine upper
		spineUpper = rig_control(name='spineUpper', shape='box', modify=1,scale=ctrlSize,
		                         colour='yellow', parentOffset=module.controls, rotateOrder=2)
		spineUpper.gimbal = createCtrlGimbal(spineUpper)
		spineUpper.pivot = createCtrlPivot(spineUpper)

		self.spineUpperCtrl = spineUpper

		pm.delete(pm.parentConstraint( 'spineJE_JNT', spineUpper.offset ))
		pm.parentConstraint( spineFullBody.con, spineUpper.offset, mo=True )

		pm.move(pm.PyNode(spineUpper.ctrl + '.cv[:]'),
		        [0, 0, 1.5],
		        relative=True,
		        worldSpace=True)

		constrainObject(spineUpper.modify,
		                [spineUpper.offset, 'worldSpace_GRP'],
		                spineUpper.ctrl, ['fullBody', 'world'],
		                type='parentConstraint')

		pm.addAttr(spineUpper.ctrl, ln='MOTION', at='enum',
		           enumName='___________',
		           k=True)
		spineUpper.ctrl.MOTION.setLocked(True)

		spineChain = rig_chain(self.centerConnection).chainChildren

		driverJntsList = []
		driverCtrlList = {}
		for i in range (0, len(spineChain)):
			driverJnt = rig_transform(0, name='spineDriverJ'+ABC[i+1], type='joint',
			                          target=spineChain[i], parent=module.parts,
			                          rotateOrder=2).object
			driverJntsList.append(driverJnt)

			driverCtrl = rig_control(name='spineDriver'+ABC[i+1], shape='circle', modify=1,
			                        targetOffset=spineChain[i], scale=ctrlSizeHalf,
			                        colour='green', parentOffset=module.controlsSec, rotateOrder=2)
			driverCtrlList[ 'spine'+ABC[i+1] ] = driverCtrl

			pm.parentConstraint( driverCtrl.con, driverJnt, mo=True )

		# constrain control drivers
		pm.parentConstraint( spineUpper.con, driverCtrlList['spineE'].offset, mo=True )
		pm.parentConstraint( spineUpper.con, driverCtrlList['spineF'].offset, mo=True )

		pm.parentConstraint(spineLower.con, driverCtrlList['spineB'].offset, mo=True)
		pm.parentConstraint(spineLower.con, driverCtrlList['spineC'].offset, mo=True)
		pm.parentConstraint(spineUpper.con,spineLower.con, driverCtrlList['spineD'].offset, mo=True)

		# create spline ik
		ik = rig_ik(name, 'spineJB_JNT', 'spineJF_JNT', 'ikSplineSolver', numSpans=5)
		pm.parent(ik.handle, ik.curve, module.parts)
		#// Result: [u'spine2_ik_Handle', u'effector6', u'curve2'] //

		spineLowerAim = rig_transform(0, name='spineLowerAim', type='locator',
		                        parent=module.parts, target='spineJB_JNT' ).object
		spineUpperAim = rig_transform(0, name= 'spineUpperAim', type='locator',
		                            parent=module.parts, target='spineJE_JNT').object

		#pm.setAttr(spineLowerAim + '.rotateZ', -90)
		#pm.setAttr(spineUpperAim + '.rotateZ', -90)
		pm.rotate( spineLowerAim, 0,0,-90, r=True , os=True)
		pm.rotate(spineUpperAim, 0, 0, -90, r=True, os=True)

		pm.parentConstraint(spineLower.con, spineLowerAim, mo=True)
		pm.parentConstraint(spineUpper.con, spineUpperAim, mo=True)

		spineAimTop = mm.eval(
			'rig_makePiston("' + spineLowerAim + '", "' + spineUpperAim + '", "spineAim");')

		pm.setAttr("spineUpperAim_LOCUp.translateY", 100)
		pm.setAttr( "spineLowerAim_LOCUp.translateY", 100)

		# advanced twist spine
		pm.setAttr(ik.handle + '.dTwistControlEnable', 1)
		pm.setAttr(ik.handle + '.dWorldUpType', 2)  # object up start and end
		pm.setAttr(ik.handle + '.dForwardAxis', 2)  # positive y
		pm.setAttr(ik.handle + '.dWorldUpAxis', 8)  # closest x

		pm.connectAttr('spineUpperAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrixEnd, f=True)
		pm.connectAttr('spineLowerAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrix, f=True)

		pm.parent(spineAimTop, module.parts)

		axis = '.ry'
		# create new attributes
		pm.addAttr(spineUpper.ctrl, ln="autoTwist", at="double", dv=0, min=0, max=1, k=False)
		pm.addAttr(spineUpper.ctrl, ln="twistOffset", at="double", dv=0, k=True)

		# create nodes for autoTwist and twistOffset
		autoTwist1 = pm.createNode("multiplyDivide", n="md_" + spineUpper.ctrl + "_autoTwist1")
		autoTwist2 = pm.createNode("multiplyDivide", n="md_" + spineUpper.ctrl + "_autoTwist2")
		twistOffset1 = pm.createNode("plusMinusAverage", n="pma_" + spineUpper.ctrl + "_twistOffset1")
		twistOffset2 = pm.createNode("plusMinusAverage", n="pma_" + spineUpper.ctrl + "_twistOffset2")

		# connect the end control
		pm.connectAttr(spineUpper.ctrl + axis, autoTwist1 + ".input1X")
		pm.connectAttr(spineUpper.ctrl + ".autoTwist", autoTwist1 + ".input2X")

		pm.connectAttr(autoTwist1 + ".outputX", twistOffset1 + ".input1D[0]")
		pm.connectAttr(spineUpper.ctrl + ".twistOffset", twistOffset1 + ".input1D[1]")

		# connect the start control
		pm.connectAttr(spineLower.ctrl + axis, autoTwist2 + ".input1X")
		pm.connectAttr(spineUpper.ctrl + ".autoTwist", autoTwist2 + ".input2X")

		pm.connectAttr(twistOffset1 + ".output1D", twistOffset2 + ".input1D[0]")
		pm.connectAttr(autoTwist2 + ".outputX", twistOffset2 + ".input1D[1]")

		pm.setAttr(twistOffset2 + ".operation", 2)  # subtract

		# connect to the ikHandle
		#pm.connectAttr(spineLower.ctrl + axis, ik.handle + ".roll")
		pm.connectAttr(twistOffset2 + ".output1D", ik.handle + ".twist")

		pm.select(ik.curve)
		curveShape = pm.pickWalk(direction='down')
		curveInfoNode = pm.arclen(curveShape[0], ch=True)
		curveInfo = pm.rename(curveInfoNode, name + '_splineIk_curveInfo')
		globalCurve = pm.duplicate(ik.curve)
		globalCurve = pm.rename(globalCurve, name + 'global_splineIk_curve')
		pm.select(globalCurve)
		globalCurveShape = pm.pickWalk(direction='down')
		globalCurveInfoNode = pm.arclen(globalCurveShape[0], ch=True)
		globalCurveInfo = pm.rename(globalCurveInfoNode, name + 'global_splineIk_curveInfo')
		pm.parent(globalCurve, module.parts)
		pm.setAttr(globalCurve + '.inheritsTransform', 1)

		distanceToStretch_PM = plusMinusNode(name + '_distanceToStretch', 'subtract',
		                                     curveInfo, 'arcLength', globalCurveInfo, 'arcLength')


		correctAdd_Minus_MD = multiplyDivideNode(name+'_correctAdd_Minus', 'multiply',
		                                         input1=[-1, 0, 0],
		                                         input2=[distanceToStretch_PM+'.output1D', 0, 0],
		                                         output=[])

		toggleStretch_ctrl_MD = multiplyDivideNode(name + '_toggleStretch_ctrl', 'multiply',
		                                         input1=[0, 0, 0],
		                                         input2=[correctAdd_Minus_MD + '.outputX', 0, 0],
		                                         output=[])

		distanceStretchCurve_PM = plusMinusNode(name + '_distanceStretchCurve', 'sum',
		                                        curveInfo, 'arcLength', toggleStretch_ctrl_MD,
		                                        'outputX')

		globalCurveStretchyFix_MD = multiplyDivideNode(name + '_globalCurveStretchyFix', 'divide',
		                                         input1=[distanceStretchCurve_PM+'.output1D', 0, 0],
		                                         input2=[globalCurveInfo + '.arcLength', 1, 1],
		                                         output=[])

		pm.addAttr(spineUpper.ctrl, longName='stretch', shortName='ts',
		             attributeType="double",
		             min=0, max=1, defaultValue=0.5, keyable=True)

		connectReverse(input=(spineUpper.ctrl + '.stretch', 0, 0),
		               output=(toggleStretch_ctrl_MD + '.input1X', 0, 0))

		for i in range(0, len(spineChain)-1 ):
			pm.connectAttr(globalCurveStretchyFix_MD + '.outputX', spineChain[i] + '.scaleY',
			               f=True)

		pm.skinCluster(driverJntsList, ik.curve, tsb=True)

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module

	def neck (self):
		return

	def head (self, ctrlSize=1.0):
		name = 'head'

		module = rig_module(name)
		self.headModule = module

		pm.parent('headJA_JNT', module.skeleton)

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		headControl = rig_control(name='head', shape='box', modify=1,
		                          targetOffset='headJA_JNT', scale=ctrlSize,
		                          colour='yellow', parentOffset=module.controls, rotateOrder=2)
		headControl.gimbal = createCtrlGimbal(headControl)
		headControl.pivot = createCtrlPivot(headControl)

		constrainObject(headControl.offset,
		                [ 'neckJEnd_JNT' , 'spineJF_JNT', self.spineFullBodyCtrl.con, 'worldSpace_GRP'],
		                headControl.ctrl, ['neck', 'spineUpper', 'fullBody', 'world'],
		                type='parentConstraint', spaceAttr='space')
		constrainObject(headControl.modify,
		                [ 'neckJEnd_JNT' , 'spineJF_JNT', 'worldSpace_GRP'],
		                headControl.ctrl, ['neck', 'spineUpper', 'world'],
		                type='orientConstraint',spaceAttr='orientSpace')

		headPos = pm.xform('headJA_JNT', translation=True, query=True, ws=True)
		headEndPos = pm.xform( 'headJEnd_JNT', translation=True, query=True, ws=True)
		headLength = lengthVector(headPos, headEndPos)
		pm.move(pm.PyNode(headControl.ctrl + '.cv[:]'), 0, headLength/2, 0, r=True,
		        os=True)

		#pm.pointConstraint( 'neckJEnd_JNT', 'headJA_JNT', mo=True )
		#pm.orientConstraint( headControl.con, 'headJA_JNT', mo=True )

		pm.parentConstraint( headControl.con, 'headJA_JNT', mo=True )

		return module

	def shoulder (self, side):
		return

	def arm (self, side, ctrlSize = 1):
		return

	def pelvis (self, ctrlSize=1):
		name = 'pelvis'

		module = self.spineModule

		if self.spineModule == '':
			module = rig_module(name)

		self.pelvisModule = module

		pelvis = self.pelvisConnection

		pm.parent(pelvis, module.skeleton)

		print 'pelvis ' + pelvis

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		self.pelvisControl = rig_control(side='', name='pelvis', shape='box',
		                                   targetOffset=pelvis, modify=1, colour='green',
		                                   parentOffset=module.controls, lockHideAttrs=[
				'tx', 'ty', 'tz'], constrain=pelvis, scale=ctrlSize, rotateOrder=0)

		if pm.objExists(self.centerConnection):
			pm.parentConstraint(self.centerConnection, self.pelvisControl.offset, mo=True)

		if pm.objExists('rigModules_GRP'):
			pm.parent(module.top, 'rigModules_GRP')

		pm.scale(pm.PyNode(self.pelvisControl.ctrl + '.cv[:]'), 1, 0.3, 1)

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module

	def connectLegPelvis(self):

			fkCtrls = self.legControls['fk']
			#foot = self.legControls['foot']

			print 'self.pelvisControl ' + str(self.pelvisControl.ctrl)
			pm.parentConstraint(self.pelvisControl.con, fkCtrls[0].offset,
			                    mo=True)
			pm.parentConstraint(self.pelvisControl.con, self.legTop,
			                    mo=True)

			'''
			hipControl = rig_control(side=side, name='hip', shape='sphere', modify=1,
			                         parentOffset=module.controls, scale=ctrlSizeHalf,
			                         rotateOrder=2, lockHideAttrs=['rx', 'ry', 'rz'])

			constrainObject(hipControl.offset,
			                [self.pelvisConnection, self.centerConnection,
			                 'worldSpace_GRP'],
			                poleVector.ctrl, ['pelvis', 'main', 'world'],
			                type='parentConstraint')
			'''

	def leg (self, side='', ctrlSize=1.0):
		name = side + '_leg'
		if side == '':
			name = 'leg'

		secColour = 'green'
		if side == 'r':
			secColour = 'magenta'
		elif side == 'l':
			secColour = 'deepskyblue'

		module = rig_module(name)
		self.legModule = module

		leg = self.legName
		knee = self.kneeName
		foot = self.footName
		footB = self.footBName
		toes = self.toesName

		if side != '':
			leg = side + '_' + leg
			knee = side + '_' + knee
			foot = side + '_' + foot
			footB = side + '_' + footB
			toes = side + '_' + toes

		chain = [leg, knee, foot, footB, toes]

		pm.parent(leg, module.skeleton)

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
		ctrlSizeEight = [ctrlSize / 8.0, ctrlSize / 8.0, ctrlSize / 8.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		self.legTop = rig_transform(0, name=side + '_legTop',
		                            target=leg, parent=module.parts).object

		legSkeletonParts = rig_transform(0, name=side + '_legSkeletonParts',
		                                 parent=self.legTop).object

		# chain result
		legResult = rig_transform(0, name=side + '_legResult', type='joint',
		                          target=leg, parent=legSkeletonParts,
		                          rotateOrder=2).object
		kneeResult = rig_transform(0, name=side + '_kneeResult', type='joint',
		                            target=knee, rotateOrder=2).object
		footResult = rig_transform(0, name=side + '_footResult', type='joint',
		                           target=foot, rotateOrder=2).object
		footBResult = rig_transform(0, name=side + '_footBResult', type='joint',
		                              target=footB, rotateOrder=2).object
		toesResult = rig_transform(0, name=side + '_toesResult', type='joint',
		                            target=toes, rotateOrder=2).object

		chainResult = [legResult, kneeResult, footResult, footBResult, toesResult]

		chainParent(chainResult)
		chainResult.reverse()

		# chain FK
		legFK = rig_transform(0, name=side + '_legFK', type='joint', target=leg,
		                      parent=legSkeletonParts, rotateOrder=2).object
		kneeFK = rig_transform(0, name=side + '_kneeFK', type='joint',
		                        target=knee, rotateOrder=2).object
		footFK = rig_transform(0, name=side + '_footFK', type='joint', target=foot, rotateOrder=2
		).object
		footBFK = rig_transform(0, name=side + '_footBFK', type='joint', target=footB, rotateOrder=2
		).object
		toesFK = rig_transform(0, name=side + '_toesFK', type='joint', target=toes, rotateOrder=2
		).object

		chainFK = [legFK, kneeFK, footFK, footBFK, toesFK]

		chainParent(chainFK)
		chainFK.reverse()

		# chain IK
		legIK = rig_transform(0, name=side + '_legIK', type='joint', target=leg,
		                      parent=legSkeletonParts, rotateOrder=2).object
		kneeIK = rig_transform(0, name=side + '_kneeIK', type='joint',
		                        target=knee, rotateOrder=2).object
		footIK = rig_transform(0, name=side + '_footIK', type='joint', target=foot, rotateOrder=2
		).object
		footBIK = rig_transform(0, name=side + '_footBIK', type='joint', target=footB, rotateOrder=2
		).object
		toesIK = rig_transform(0, name=side + '_toesIK', type='joint', target=toes, rotateOrder=2
		).object

		chainIK = [legIK, kneeIK, footIK, footBIK,toesIK]

		chainParent(chainIK)
		chainIK.reverse()

		# create ik
		ik = rig_ik(name, legIK, footIK, 'ikRPsolver')
		pm.parent(ik.handle, module.parts)
		pm.hide(ik.handle)

		poleVector = rig_control(side=side, name='legPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx', 'ry', 'rz'],
		                         targetOffset=[leg, foot],
		                         parentOffset=module.controls, scale=ctrlSizeEight)

		if side == 'r':
			pm.rotate(poleVector.ctrl.cv, 90, 0, 0, r=True, os=True)
		else:
			pm.rotate(poleVector.ctrl.cv, -90, 0, 0, r=True, os=True)

		pm.connectAttr(module.top.ikFkSwitch, poleVector.offset + '.visibility')

		self.legControls['poleVector'] = poleVector

		pm.delete(pm.aimConstraint(knee, poleVector.offset, mo=False))

		footPos = pm.xform(foot, translation=True, query=True, ws=True)
		kneePos = pm.xform(knee, translation=True, query=True, ws=True)
		poleVectorPos = pm.xform(poleVector.con, translation=True, query=True,
		                         ws=True)

		pvDistance = lengthVector(kneePos, poleVectorPos)

		pm.xform(poleVector.offset, translation=[pvDistance, 0, 0], os=True,
		         r=True)

		pm.rotate(poleVector.ctrl.cv, 0, 0, 90, r=True, os=True)

		pm.poleVectorConstraint(poleVector.con, ik.handle)  # create pv

		# pm.move(poleVector.offset, [0, -pvDistance*40, 0], relative=True,
		#       objectSpace=True)

		pvDistance = lengthVector(footPos, kneePos)
		pm.move(poleVector.offset, [pvDistance * 2, 0, 0], relative=True, objectSpace=True)
		#pm.move(poleVector.offset, [0, 0, pvDistance * 2],relative=True, worldSpace=True)

		print 'ik handle ' + ik.handle

		# ## MAKE FOOT CONTROL
		footControl = rig_control(side=side, name='foot', shape='box', modify=2,
		                          parentOffset=module.controls, lockHideAttrs=['rx', 'ry', 'rz'], scale=ctrlSizeHalf,
		                          rotateOrder=2)

		pm.delete(pm.pointConstraint(foot, footControl.offset))

		footControl.gimbal = createCtrlGimbal(footControl)
		footControl.pivot = createCtrlPivot(footControl)

		'''
		constrainObject(footControl.offset,
		                [self.pelvisConnection, self.centerConnection,self.spineFullBodyCtrl.con,
		                 'worldSpace_GRP'],
		                footControl.ctrl, ['pelvis', 'spineLower', 'fullBody' , 'world'],
		                type='parentConstraint')
		'''

		pm.connectAttr(module.top.ikFkSwitch, footControl.offset + '.visibility')

		self.legControls['foot'] = footControl

		# auto pole vector LOCATOR
		autoPVOffset = rig_transform(0, name=side + '_autoLegPVOffset',
		                             parent=module.parts, target=poleVector.con
		).object
		autoPVLoc = rig_transform(0, name=side + '_autoLegPV', type='locator',
		                          parent=autoPVOffset, target=autoPVOffset).object

		#pm.parentConstraint(self.centerConnection, autoPVOffset, mo=True)
		#pm.pointConstraint(self.centerConnection, footControl.con, autoPVLoc, mo=True)

		constrainObject(poleVector.offset,
		                [autoPVLoc, self.pelvisConnection, self.centerConnection,
		                 'worldSpace_GRP'],
		                poleVector.ctrl, ['auto', 'pelvis', 'spineLower', 'world'],
		                type='parentConstraint')



		# ## MAKE FOOT BALL CONTROL
		footBallControl = rig_control(side=side, name='footBall', shape='cylinder', modify=2,
		                              parentOffset=module.controls, scale=ctrlSizeHalf,
		                              rotateOrder=2, colour=secColour)

		footBallControl.gimbal = createCtrlGimbal(footBallControl)
		footBallControl.pivot = createCtrlPivot(footBallControl)

		pm.delete(pm.pointConstraint(footB, footBallControl.offset))
		#pm.parentConstraint(footBallControl.con, ik.handle, mo=True)

		pm.connectAttr(module.top.ikFkSwitch, footBallControl.offset + '.visibility')

		pm.rotate(footBallControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)
		pm.move(footBallControl.ctrl.cv, [0, 0.5, 0], relative=True)

		pm.addAttr(footBallControl.ctrl, ln='MOTION', at='enum',
		           enumName='___________',
		           k=True)
		footBallControl.ctrl.MOTION.setLocked(True)
		pm.addAttr(footBallControl.ctrl, longName='twist', at='float', k=True)
		pm.addAttr(footBallControl.ctrl, longName='footRoll', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.connectAttr(footBallControl.ctrl.twist, ik.handle.twist)

		'''
		constrainObject(footBallControl.modify[0],
		                [footBallControl.offset, 'worldSpace_GRP'],
		                footBallControl.ctrl, ['foot', 'world'],
		                type='orientConstraint')
		'''


		### MAKE FOOT TOES CONTROL
		footToesControl = rig_control(side=side, name='footToes', shape='cylinder', modify=2,
		                              parentOffset=module.controls, scale=ctrlSizeQuarter,
		                              rotateOrder=2, colour=secColour)

		pm.delete(pm.pointConstraint(toes, footToesControl.offset))
		pm.parent( footToesControl.offset, footBallControl.con )
		pm.parent(  ik.handle, footToesControl.con )

		pm.connectAttr(module.top.ikFkSwitch, footToesControl.offset + '.visibility')

		pm.rotate(footToesControl.ctrl.cv, [0, 0, 90], relative=True, objectSpace=True)

		'''
		constrainObject(footToesControl.modify[0],
		                [footToesControl.offset, 'worldSpace_GRP'],
		                footToesControl.ctrl, ['foot', 'world'],
		                type='orientConstraint')
		'''

		pm.parentConstraint( footToesControl.con, footControl.offset , mo=True)

		pm.parent( footControl.offset, footBallControl.con )
		
		## MAKE FOOT ROLLS
		pm.addAttr(footBallControl.ctrl, ln='ROLLS', at='enum',
		           enumName='___________',
		           k=True)
		footBallControl.ctrl.ROLLS.setLocked(True)
		rollTip = rig_transform(0, name=side + '_footRollTip',
		                            parent=footBallControl.gimbal.ctrl,
		                            target=side+'_footRollTip_LOC').object
		rollHeel = rig_transform(0, name=side + '_footRollHeel',
		                    parent=rollTip,
		                    target=side + '_footRollHeel_LOC').object
		rollIn = rig_transform(0, name=side + '_footRollIn',
		                     parent=rollHeel,
		                     target=side + '_footRollIn_LOC').object
		rollOut = rig_transform(0, name=side + '_footRollOut',
		                       parent=rollIn,
		                       target=side + '_footRollOut_LOC').object
		pm.parent( footBallControl.con, rollOut )

		pm.delete(pm.ls(side+"_footRoll*_LOC"))

		pm.addAttr(footBallControl.ctrl, longName='rollTip', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.addAttr(footBallControl.ctrl, longName='rollHeel', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.addAttr(footBallControl.ctrl, longName='rollIn', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.addAttr(footBallControl.ctrl, longName='rollOut', at='float', k=True, min=0,
		           max=10, dv=0)

		flipRoll = 1
		if side == 'r':
			flipRoll = -1
		rig_animDrivenKey(footBallControl.ctrl.rollTip, (0, 10),
		                  rollTip+'.rotateX', (0, 90 ))
		rig_animDrivenKey(footBallControl.ctrl.rollHeel, (0, 10),
		                  rollHeel+'.rotateX', (0, -90 ))
		rig_animDrivenKey(footBallControl.ctrl.rollIn, (0, 10),
		                  rollIn+'.rotateZ', (0, 90*flipRoll ))
		rig_animDrivenKey(footBallControl.ctrl.rollOut, (0, 10),
		                  rollOut + '.rotateZ', (0, -90*flipRoll ))

		## do foot roll with footBall and footToes modify
		rig_animDrivenKey(footBallControl.ctrl.footRoll, (0,5, 10),
		                  footToesControl.modify[1] + '.rotateX', (0, 20,30 ))
		#rig_animDrivenKey(footBallControl.ctrl.footRoll, (0, 5, 10),
		#                  footToesControl.modify[1] + '.rotateX', (0, 0, 40 ))
		
		

		# ## MAKE TOES CONTROL
		toesControl = rig_control(side=side, name='toes', shape='pyramid', modify=1,
		                             parentOffset=module.controls, scale=ctrlSizeQuarter,
		                             rotateOrder=2, lockHideAttrs=['tx','ty','tz'])

		self.legControls['toes'] = toesControl

		pm.delete(pm.parentConstraint(toes, toesControl.offset))
		pm.orientConstraint(toesControl.con, toesIK, mo=True)
		pm.parentConstraint(footToesControl.con, toesControl.offset, mo=True)

		pm.connectAttr(module.top.ikFkSwitch, toesControl.offset + '.visibility')

		
		constrainObject(toesControl.modify,
		                [footBallControl.con, toesControl.offset, 'worldSpace_GRP'],
		                toesControl.ctrl, ['footBall', 'footToes', 'world'],
		                type='orientConstraint')
		

		toesPos = pm.xform(toesControl.con, translation=True, query=True, ws=True)
		endPos = pm.xform(side + '_toesJEnd_JNT', translation=True, query=True, ws=True)

		toesLength = lengthVector(toesPos, endPos)

		pm.move(toesControl.ctrl.cv, [0, 0, toesLength], relative=True)

		pm.addAttr(toesControl.ctrl, ln='SHAPE', at='enum',
		           enumName='___________',
		           k=True)
		toesControl.ctrl.SHAPE.setLocked(True)
		pm.addAttr(toesControl.ctrl, longName='curl', at='float', k=True, min=-10,
		           max=10, dv=0)
		pm.addAttr(toesControl.ctrl, longName='curlThumb', at='float', k=True, min=-10,
		           max=10, dv=0)
		pm.addAttr(toesControl.ctrl, longName='splay', at='float', k=True, min=-10,
		           max=10, dv=0)


		'''
		if side == 'l':
			pm.move(toesControl.ctrl.cv, [0, 0, toesLength], relative=True)
		else:
			pm.move(toesControl.ctrl.cv, [0, 0, toesLength * -1], relative=True)
		'''

		# make reverse ankle ik setup
		pm.parent( footBIK, legSkeletonParts  )
		footBReverseJnt = rig_transform(0, name=side + '_footBReverse', type='joint',
		                        parent=legSkeletonParts, target=footBIK).object
		ankleReverseJnt = rig_transform(0, name=side + '_ankleReverse', type='joint',
		                        parent=legSkeletonParts, target = footIK).object
		pm.parent( ankleReverseJnt, footBReverseJnt )
		ankleIK = rig_ik( side+'_ankle' ,footBReverseJnt, ankleReverseJnt, 'ikRPsolver' )
		#pm.parent(ankleIK.handle, module.parts)
		pm.hide(ankleIK.handle)
		pm.parent(ankleIK.handle, footToesControl.con)
		anklePV = rig_transform(0, name=side + '_anklePV', type='locator',
		                        parent=module.parts, target=footBallControl.con).object
		pm.move(anklePV, [50, 0, 0],relative=True, objectSpace=True)
		pm.parentConstraint( footToesControl.con, anklePV, mo=True )
		pm.poleVectorConstraint(anklePV, ankleIK.handle)
		pm.pointConstraint( footControl.con, ankleIK.handle, mo=True )
		pm.parentConstraint( footToesControl.con,footBReverseJnt,mo=True )

		pm.pointConstraint(ankleReverseJnt, ik.handle, mo=True)
		pm.orientConstraint( ankleReverseJnt, footIK, mo=True )

		# make leg aim
		legAimLoc = rig_transform(0, name=side + '_legFootAim', type='locator',
		                            parent=module.parts).object
		footAimLoc = rig_transform(0, name=side + '_footLegAim', type='locator',
		                        parent=module.parts).object

		pm.pointConstraint( self.legTop, legAimLoc  )
		pm.delete(pm.pointConstraint( footBallControl.con, footAimLoc ))
		pm.pointConstraint( footToesControl.con, footAimLoc,mo=True  )
		pm.setAttr( footAimLoc+'.rotateZ', -90 )
		pm.setAttr(legAimLoc+'.rotateZ', -90)

		legAimTop = mm.eval('rig_makePiston("'+legAimLoc+'", "'+footAimLoc+'", "'+side+'_legAim");')

		#legAimMod = rig_transform(0, name=side + '_legFootAimModify', type='group',
		 #                           parent=side+'_footLegAim_LOC', target=side+'_footLegAim_LOC').object

		#pm.parent( side+'_footLegAim_JNT', legAimMod )

		pm.parent( legAimTop, module.parts )

		# make foot ankle aim
		ankleAimLoc = rig_transform(0, name=side + '_ankleLegAim', type='locator',
		                        parent=module.parts).object
		footBAimLoc = rig_transform(0, name=side + '_footBAim', type='locator',
		                            parent=module.parts).object

		pm.parentConstraint( footIK, ankleAimLoc  )
		pm.delete(pm.orientConstraint( footIK, footBAimLoc ))
		pm.pointConstraint( footBReverseJnt, footBAimLoc )
		#pm.setAttr( footAimLoc+'.rotateZ', -90 )
		#pm.setAttr(legAimLoc+'.rotateZ', -90)

		ankleAimTop = mm.eval('rig_makePiston("'+ankleAimLoc+'", "'+footBAimLoc+'", "'+side+'_ankleAim");')

		pm.parent( ankleAimTop, module.parts )
		pm.parentConstraint( side+'_ankleLegAim_JNT', footBIK, skipRotate=('x','y','z'), mo=True )
		pm.parentConstraint( footToesControl.con, footBIK, skipTranslate=('x','y','z'), mo=True )

		# make ankle bend
		startMeasure = rig_transform(0, name=name+'FullStart', type='locator',
		                          parent=module.parts, target=leg).object
		endMeasure = rig_transform(0, name=name+'FullEnd', type='locator',
		                          parent=module.parts, target=footToesControl.con).object
		totalLegDist = rig_measure(name=name+'FullLength', start=startMeasure, end=endMeasure,
	                        parent=module.parts)

		legDistGlobal_MD = multiDivideNode( name+'_distanceRotationGlobal', 'multiply',
                        'rig_GRP', 'worldScale', '', totalLegDist.distanceVal )
		legDist_MD = multiDivideNode( name+'_distanceRotation', 'divide',
                        totalLegDist.distance, 'distance', legDistGlobal_MD, 'outputX' )

		pm.pointConstraint( footBallControl.con, endMeasure, mo=True )
		pm.pointConstraint( self.pelvisConnection, startMeasure, mo=True )

		'''

		expression -e -s "float $outputX = multiplyDivide8.outputX; \n\nfloat $degrees = 0;\n\n$degrees = -1*atand(1.0-$outputX);\n\nl_footAim_JNT.rotateZ = $degrees*1.5;"  -o "" -ae 1 -uc all  l_legRotate_EXP;

		
		'''
		mm.eval('expression -o ("'+side+'_footLegAim_JNT") -s ("float $outputX = '+legDist_MD+'.outputX; float $degrees = 0;$degrees = -1*atand(1.0-$outputX);ry = $degrees*1.5;") -n ("'+side+'_legRotate_EXP") -ae 1 -uc all ;')

		footOrientLoc = rig_transform(0, name=side+'_footOrient', type='locator',
		                          parent=side+'_footLegAim_JNT', target=footControl.con).object
		pm.setAttr( footOrientLoc+'.tx', 0)
		pm.setAttr( footOrientLoc+'.ty', 0)
		pm.setAttr( footOrientLoc+'.tz', 0)
		con = pm.parentConstraint( footControl.offset, footOrientLoc, footControl.modify[0], mo=True )
		pm.parentConstraint( side+'_legFootAim_JNT', side+'_footLegAim_JNT', autoPVOffset, mo=True )

		
		# create ik stretchy and soft pop
		endBlendLoc = rig_ikStretchySoftPop(side, name, chainIK, module, footControl,
		                                    ctrlSizeQuarter,
		                                    self.legTop)

		#pm.pointConstraint(endBlendLoc, footToesControl.offset, mo=True)

		pm.addAttr(footBallControl.ctrl, ln='ikSettings', at='enum',
	             enumName='___________',
	             k=True)
		footBallControl.ctrl.ikSettings.setLocked(True)

		pm.addAttr( footBallControl.ctrl, longName='ikStretch', shortName='iks',attributeType="double",
		                        min=0, max=1, defaultValue=0, keyable=True )
		pm.addAttr( footBallControl.ctrl, longName='midSlide', shortName='es',attributeType="double",
		                            min=-1, max=1, defaultValue=0, keyable=True )
		pm.addAttr( footBallControl.ctrl, longName='ankleStiffness', shortName='aksti',attributeType="double",
		                            min=0, max=1, defaultValue=0.5, keyable=True )

		targets = con.getWeightAliasList()
		pm.connectAttr( footBallControl.ctrl.ankleStiffness, targets[0] )
		connectReverse( name=side+'_ankleOrient_reverseNode#', input=(targets[0],0,0), output=(targets[1],0,0) )

		pm.connectAttr( footBallControl.ctrl.ikStretch, footControl.ctrl.ikStretch)
		pm.connectAttr( footBallControl.ctrl.midSlide, footControl.ctrl.midSlide)
		pm.setAttr( footControl.ctrl.ikSettings, k=False, cb=False )
		pm.setAttr( footControl.ctrl.ikStretch, k=False, cb=False )
		pm.setAttr( footControl.ctrl.ikSoftBlend, k=False, cb=False )
		pm.setAttr( footControl.ctrl.midSlide, k=False, cb=False )

		# create fk
		print 'fk chain ' + str(chainFK)
		fkCtrls = fkControlChain(chainFK, scale=ctrlSize)
		for fk in fkCtrls:
			pm.parent(fk.offset, module.controls)
			pm.setDrivenKeyframe(fk.offset + '.visibility',
			                     cd=module.top.ikFkSwitch,
			                     dv=1,
			                     v=0)
			pm.setDrivenKeyframe(fk.offset + '.visibility',
			                     cd=module.top.ikFkSwitch,
			                     dv=0,
			                     v=1)
		kneeFk = fkCtrls[1]
		rotateAxis = ['rx', 'ry', 'rz']
		if self.elbowAxis in rotateAxis: rotateAxis.remove(self.kneeAxis)
		for at in rotateAxis:
			kneeFk.ctrl.attr(at).setKeyable(False)
			kneeFk.ctrl.attr(at).setLocked(True)

		self.legControls['fk'] = fkCtrls

		self.connectIkFkSwitch(chains=[chainResult, chainIK, chainFK],
		                       module=module, name=name)

		# constrain result to skeleton
		for i in range(0, len(chain)):
			pm.parentConstraint(chainResult[i], chain[i], mo=True)

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module

	def foot(self, side = '', axis = 'ry', ctrlSize = 1.0):
		abc = list(string.ascii_lowercase)

		name = side + '_toes'
		sideName = side + '_'
		if side == '':
			name = 'toes'
			sideName = ''

		module = rig_module(name)
		self.fingersModule = module

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		rotateAxis = ['rx', 'ry', 'rz']

		rotateAxis.remove(axis)

		skipAxis = rotateAxis + ['tx', 'ty', 'tz']

		for toes in ( self.toeThumb, self.toeIndex, self.toeMid, self.toeRing,
		                self.toePinky ):

			toe = toes

			if side != '':
				toe = side + '_' + toe

			print 'finger is ' + toe
			if pm.objExists(toe):

				chainFingers = rig_chain(toe)

				childrenFngs = chainFingers.chainChildren

				childrenFngs.pop(len(childrenFngs) - 1)

				sc = simpleControls(toe,
				                    modify=2, scale=ctrlSize,
				                    parentOffset=module.controls)

				toeCtrl = sc[toe]
				baseLimit = 0.2
				pm.transformLimits(toeCtrl.ctrl, tx=(-1 * baseLimit, baseLimit), etx=(1, 1))
				pm.transformLimits(toeCtrl.ctrl, ty=(-1 * baseLimit, baseLimit), ety=(1, 1))
				pm.transformLimits(toeCtrl.ctrl, tz=(-1 * baseLimit, baseLimit), etz=(1, 1))

				pm.move(toeCtrl.ctrl.cv, [0, 0, 0.3], relative=True)

				if 'Thumb' in toe:
					if pm.objExists(sideName + 'footJA_JNT'):
						pm.parentConstraint(sideName + 'footJA_JNT', toeCtrl.offset, mo=True)
				else:
					if pm.objExists(sideName + 'footJB_JNT'):
						pm.parentConstraint(sideName + 'footJB_JNT', toeCtrl.offset, mo=True)
						if pm.objExists(sideName+'footToesOrient_LOC'):
							pm.orientConstraint(sideName+'footToesOrient_LOC', toeCtrl.modify[0], mo=True,
							                    skip='x')

						else:
							orientLoc = rig_transform( 0, name=sideName+'footToesOrient',
							                           type='locator',
							               target=side+'_toesJA_JNT',
							               parent=side+'_toesJA_JNT').object
							pm.delete(pm.orientConstraint( toeCtrl.modify[0], orientLoc ))
							pm.orientConstraint(orientLoc, toeCtrl.modify[0],
							                    mo=True,
							                    skip='x')

				pm.setAttr( toeCtrl.modify[0]+".rotateOrder", 2 )

				sc = simpleControls(childrenFngs,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls,
				               lockHideAttrs=skipAxis)

				# fk control
				toesControl = self.legControls['toes'].ctrl
				if 'Thumb' in toe:
					if pm.objExists(toesControl.curlThumb):
						for key in sc:
							control = sc[key]
							rig_animDrivenKey(toesControl.curlThumb, (-10, 0, 10),
							                  control.modify[0] + '.rotateY', (-90, 0, 90 ))

						rig_animDrivenKey(toesControl.curlThumb, (-10, 0, 10),
						                  toeCtrl.modify[1] + '.rotateY', (-90, 0, 90 ))
				else:
					if pm.objExists( toesControl.curl ):
						for key in sc:
							control = sc[key]
							rig_animDrivenKey(toesControl.curl, (-10, 0, 10),
							                  control.modify[0] + '.rotateY', (-90, 0, 90 ))

						rig_animDrivenKey(toesControl.curl, (-10, 0, 10),
						                  toeCtrl.modify[1] + '.rotateY', (-90, 0, 90 ))

				pm.parent(toe, module.skeleton)

			else:
				print toe + ' does not exist...Skipping.'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module


def rig_quadPrepare():

	fngJoints = cmds.ls('*fng*JA_JNT')
	for digit in fngJoints:
		try:
			cmds.parent( digit, w=True)
		except ValueError:
			print 'Skipping ' + digit + ' as it does not exist'

	toesJoints = cmds.ls('*toe*JA_JNT')
	if 'l_toesJA_JNT' in toesJoints: toesJoints.remove('l_toesJA_JNT')
	if 'r_toesJA_JNT' in toesJoints: toesJoints.remove('r_toesJA_JNT')
	for digit in toesJoints:
		try:
			cmds.parent(digit, w=True)
		except ValueError:
			print 'Skipping ' + digit + ' as it does not exist'



	sideJointList = [ 'clavicleJA_JNT', 'armJA_JNT', 'legJA_JNT' ]
	for jnt in sideJointList:
		for side in ('l_', 'r_'):
			try:
				cmds.parent(side + jnt, w=True)
			except ValueError:
				print 'Skipping '+side+jnt+' as it does not exist'

	try:
		cmds.parent( 'headJA_JNT', w=True)
	except ValueError:
		print 'Skipping neckJA_JNT as it does not exist'

	try:
		cmds.parent( 'neckJA_JNT', w=True)
		neckEndJnt = rig_transform(0, name='neckJEnd', type='joint',
    	                          target='headJA_JNT', parent='neckJF_JNT',
    	                          rotateOrder=2).object
	except ValueError:
		print 'Skipping neckJA_JNT as it does not exist'

def rig_quadFinalize():

	try:
		# world space hands and feet
		for s in ['l', 'r']:
			pm.setAttr(s+'_foot_CTRL.space', 3)
			pm.setAttr(s+'_hand_CTRL.space', 1)
	except:
		pass


