


from make.rig_ik import *
from rutils.rig_chain import *
from make.rig_controls import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform
from rutils.rig_nodes import *
from rutils.rig_math import *
from rutils.rig_anim import *

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm
import string

ABC = list(string.ascii_uppercase)

'''

testing

import rig_biped as rb
reload(rb)
biped = rb.rig_biped()
biped.arm('l')


'''
class rig_biped(object):
	
	def __init__(self):

		self.globalCtrl = pm.PyNode('global_CTRL')

		self.switchLoc = 'ikFkSwitch_LOC'

		self.clavicleName = 'clavicleJA_JNT'

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
		self.headModule = ''
		self.neckModule = ''

		self.shoulderModule = ''
		self.armModule = ''
		self.fingersModule = ''

		self.legModule = ''
		self.toesModule = ''
		self.pelvisModule = ''



	def create(self):
		
		self.spine()
		
		self.neck()
		
		self.head()
		
		for s in ['l', 'r']:
			self.arm(s)
			self.leg(s)
			self.shoulder(s)

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
		pm.move(pm.PyNode( spineFullBody.ctrl+'.cv[:]' ), [0, spineDistance, -1*(spineDistance*2)],
		        relative=True,
		        worldSpace=True)
		spineFullBody.gimbal = createCtrlGimbal(spineFullBody)
		spineFullBody.pivot = createCtrlPivot(spineFullBody)


		pm.scale(pm.PyNode(spineFullBody.ctrl+'.cv[:]'), 0.5, 1, 0.5)

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

		# advanced twist spine
		pm.setAttr(ik.handle + '.dTwistControlEnable', 1)
		pm.setAttr(ik.handle + '.dWorldUpType', 2)  # object up start and end
		pm.setAttr(ik.handle + '.dForwardAxis', 2)  # positive y
		pm.setAttr(ik.handle + '.dWorldUpAxis', 6)  # positive x

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
		             min=0, max=1, defaultValue=1, keyable=True)

		connectReverse(input=(spineUpper.ctrl + '.stretch', 0, 0),
		               output=(toggleStretch_ctrl_MD + '.input1X', 0, 0))

		for i in range(0, len(spineChain)-1 ):
			pm.connectAttr(globalCurveStretchyFix_MD + '.outputX', spineChain[i] + '.scaleY',
			               f=True)

		pm.skinCluster(driverJntsList, ik.curve, tsb=True)

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module
		
	def neck(self, ctrlSize=1.0):

		name = 'neck'

		module = rig_module(name)
		self.neckModule = module

		pm.parent('neckJA_JNT', module.skeleton)

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]


		# make neck fk controls
		neckBaseFK = rig_control(name='neckBaseFK', shape='box', modify=1,
		                         lockHideAttrs=['tx', 'ty', 'tz'],scale=ctrlSize,
		                         colour='lightGreen', parentOffset=module.controls, rotateOrder=2)

		pm.delete(pm.parentConstraint( 'neckJA_JNT', neckBaseFK.offset ))
		pm.parentConstraint( self.spineConnection, neckBaseFK.offset )

		neckMidFK = rig_control(name='neckMidFK', shape='box', modify=1,
		                        lockHideAttrs=['tx', 'ty', 'tz'], scale=ctrlSize,
		                        colour='lightGreen', parentOffset=module.controls, rotateOrder=2)

		pm.delete(pm.parentConstraint('neckJB_JNT', neckMidFK.offset))

		pm.parent(neckMidFK.offset, neckBaseFK.con)


		neckBasePos = pm.xform(neckBaseFK.con, translation=True, query=True, ws=True)
		headPos = pm.xform('headJA_JNT', translation=True, query=True, ws=True)
		neckLength = lengthVector(neckBasePos, headPos)

		pm.move(pm.PyNode(neckBaseFK.ctrl + '.cv[:]'), 0, 0, -1*neckLength, r=True,
		        os=True)
		pm.move(pm.PyNode(neckMidFK.ctrl + '.cv[:]'), 0, 0, -1 * neckLength, r=True,
		        os=True)

		pm.scale(pm.PyNode(neckBaseFK.ctrl + '.cv[:]'), 1, 0.5, 1)
		pm.scale(pm.PyNode(neckBaseFK.ctrl + '.cv[:]'), 0.8, 1, 1)
		pm.scale(pm.PyNode(neckMidFK.ctrl + '.cv[:]'), 1, 0.5, 1)
		pm.scale(pm.PyNode(neckMidFK.ctrl + '.cv[:]'), 0.8, 1, 1)

		constrainObject(neckBaseFK.modify,
		                [neckBaseFK.offset, 'worldSpace_GRP'],
		                neckBaseFK.ctrl, ['spineUpper', 'world'],
		                type='orientConstraint')

		constrainObject(neckMidFK.modify,
		                [neckMidFK.offset, 'worldSpace_GRP'],
		                neckMidFK.ctrl, ['neckBase', 'world'],
		                type='orientConstraint')

		# neckBase
		neckBase = rig_control(name='neckBase', shape='circle', modify=1,
		                         targetOffset='neckJA_JNT',
		                         constrainOffset=self.spineConnection, scale=ctrlSize,
		                         colour='lightGreen', parentOffset=module.controlsSec,
		                         rotateOrder=2)

		constrainObject(neckBase.modify,
		                [ neckBaseFK.con , neckBase.offset, 'worldSpace_GRP'],
		                neckBase.ctrl, ['neckBaseFK','spine', 'world'],
		                type='orientConstraint')

		neckBaseDriver = rig_transform(0, name='neckBaseDriver', type='joint',
		                           target='neckJB_JNT', parent=module.parts,
		                           rotateOrder=2).object

		pm.parentConstraint( neckBase.con, neckBaseDriver, mo=True )

		# neckMid
		neckMid = rig_control(name='neckMid', shape='circle', modify=1,
		                       targetOffset='neckJB_JNT', scale=ctrlSize,
		                       colour='lightGreen', parentOffset=module.controlsSec, rotateOrder=2)

		constrainObject(neckMid.modify,
		                [ neckMidFK.con , neckMid.offset, neckBase.con,'worldSpace_GRP'],
		                neckMid.ctrl, [ 'neckMidFK' , 'neckAim' ,'neckBase', 'world'],
		                type='parentConstraint')

		neckMidDriver = rig_transform(0, name='neckMidDriver', type='joint',
		                          target='neckJB_JNT', parent=module.parts,
		                          rotateOrder=2).object

		pm.parentConstraint(neckMid.con, neckMidDriver, mo=True)

		neckTop = rig_control(name='neckTop', shape='circle', modify=1,
		                      targetOffset='headJA_JNT', scale=ctrlSize,
		                      colour='yellow', parentOffset=module.parts, rotateOrder=2)

		neckTopDriver = rig_transform(0, name='headDriver', type='joint',
		                           target='headJA_JNT', parent=module.parts,
		                           rotateOrder=2).object

		pm.parentConstraint(neckTop.con, neckTopDriver, mo=True)
		pm.parentConstraint( neckTop.con, neckBase.con, neckMid.offset, mo=True )

		driverJnts = [neckBaseDriver, neckMidDriver, neckTopDriver]

		neckTopGrp = rig_transform(0, name='neckTop',
		                            target='neckJA_JNT', parent=module.parts).object

		neckSkeletonParts = rig_transform(0, name='neckSkeletonParts',
		                                 parent=neckTopGrp).object
		# chain result
		neckBaseIK = rig_transform(0, name='neckBaseIK', type='joint',
		                          target='neckJA_JNT', parent=neckSkeletonParts,
		                          rotateOrder=2).object
		neckMidIK = rig_transform(0, name='neckMidIK', type='joint',
		                            target='neckJB_JNT', rotateOrder=2).object
		neckTopIK = rig_transform(0, name='neckTopIK', type='joint',
		                           target='headJA_JNT', rotateOrder=2).object

		chainNeckIK = [neckBaseIK, neckMidIK, neckTopIK]

		chainParent(chainNeckIK)
		chainNeckIK.reverse()

		# create spline ik
		ik = rig_ik(name, neckBaseIK, neckTopIK, 'ikSplineSolver', numSpans=2)
		pm.parent(ik.handle, ik.curve, module.parts)
		# // Result: [u'spine2_ik_Handle', u'effector6', u'curve2'] //

		neckAim = rig_transform(0, name='neckAim', type='locator',
		                              parent=module.parts, target='neckJA_JNT').object
		headAim = rig_transform(0, name='headAim', type='locator',
		                              parent=module.parts, target='headJA_JNT').object

		pm.rotate(neckAim, 0, 0, -90, r=True, os=True)
		pm.rotate(headAim, 0, 0, -90, r=True, os=True)

		pm.parentConstraint(neckBase.con, neckAim, mo=True)
		pm.parentConstraint(neckTop.con, headAim, mo=True)

		neckAimTop = mm.eval(
			'rig_makePiston("' + neckAim + '", "' + headAim + '", "neckHeadAim");')

		# advanced twist spine
		pm.setAttr(ik.handle + '.dTwistControlEnable', 1)
		pm.setAttr(ik.handle + '.dWorldUpType', 2)  # object up start and end
		pm.setAttr(ik.handle + '.dForwardAxis', 2)  # positive y
		pm.setAttr(ik.handle + '.dWorldUpAxis', 6)  # positive x

		pm.connectAttr('headAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrixEnd, f=True)
		pm.connectAttr('neckAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrix, f=True)

		pm.parent(neckAimTop, module.parts)

		sc = pm.skinCluster(driverJnts, ik.curve, tsb=True, dr=0.1, maximumInfluences=2)

		pm.skinPercent( sc, ik.curve.cv[2],   tv=[neckMidDriver,1] )
		pm.skinPercent(sc, ik.curve.cv[0], tv=[neckBaseDriver, 1])
		pm.skinPercent(sc, ik.curve.cv[4], tv=[neckTopDriver, 1])

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

		correctAdd_Minus_MD = multiplyDivideNode(name + '_correctAdd_Minus', 'multiply',
		                                         input1=[-1, 0, 0],
		                                         input2=[distanceToStretch_PM + '.output1D', 0, 0],
		                                         output=[])

		toggleStretch_ctrl_MD = multiplyDivideNode(name + '_toggleStretch_ctrl', 'multiply',
		                                           input1=[0, 0, 0],
		                                           input2=[correctAdd_Minus_MD + '.outputX', 0, 0],
		                                           output=[])

		distanceStretchCurve_PM = plusMinusNode(name + '_distanceStretchCurve', 'sum',
		                                        curveInfo, 'arcLength', toggleStretch_ctrl_MD,
		                                        'outputX')

		globalCurveStretchyFix_MD = multiplyDivideNode(name + '_globalCurveStretchyFix', 'divide',
		                                               input1=[ distanceStretchCurve_PM + '.output1D', 0,0],
		                                               input2=[globalCurveInfo + '.arcLength', 1, 1],
		                                               output=[])

		pm.addAttr(neckTop.ctrl, longName='stretch', shortName='ts',
		           attributeType="double",
		           min=0, max=1, defaultValue=1, keyable=True)

		connectReverse(input=(neckTop.ctrl + '.stretch', 0, 0),
		               output=(toggleStretch_ctrl_MD + '.input1X', 0, 0))

		pm.connectAttr(globalCurveStretchyFix_MD + '.outputX',  neckBaseIK+'.scaleY',
		             f=True)
		pm.connectAttr(globalCurveStretchyFix_MD + '.outputX', neckMidIK+'.scaleY',
		              f=True)

		pm.connectAttr( neckBaseIK+'.scaleY', 'neckJA_JNT.scaleY',
		               f=True)
		pm.connectAttr(neckMidIK + '.scaleY', 'neckJB_JNT.scaleY',
		               f=True)

		pm.parentConstraint(neckBaseIK, 'neckJA_JNT',mo=True )
		pm.parentConstraint(neckMidIK, 'neckJB_JNT', mo=True )



		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return

	def head(self, ctrlSize=1.0):

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
		                [ 'neckMidFKCon_GRP' , 'spineJF_JNT', self.spineFullBodyCtrl.con, 'worldSpace_GRP'],
		                headControl.ctrl, ['neckFK', 'spineUpper', 'fullBody', 'world'],
		                type='parentConstraint')

		pm.addAttr(headControl.ctrl, longName='stretch', shortName='ts',
		           attributeType="double",
		           min=0, max=1, defaultValue=0, keyable=True)
		pm.connectAttr(headControl.ctrl + '.stretch', 'neckTop_CTRL.stretch',
		               f=True)

		headPos = pm.xform('headJA_JNT', translation=True, query=True, ws=True)
		headEndPos = pm.xform( 'headJEnd_JNT', translation=True, query=True, ws=True)
		headLength = lengthVector(headPos, headEndPos)
		pm.move(pm.PyNode(headControl.ctrl + '.cv[:]'), 0, headLength/2, 0, r=True,
		        os=True)

		# connect head to neck top
		pm.parentConstraint( headControl.con, 'neckTopOffset_GRP', mo=True )

		pm.pointConstraint( 'neckTopIK_JNT', 'headJA_JNT', mo=True )
		pm.orientConstraint( headControl.con, 'headJA_JNT', mo=True )


	def shoulder (self, side='', ctrlSize=1 ):
		name = side + '_shoulder'
		if side == '':
			name = 'shoulder'

		module = self.armModule

		if self.armModule == '':
			module = rig_module(name)

		self.shoulderModule = module

		shoulder = self.clavicleName

		if side != '':
			shoulder = side+ '_' + shoulder

		pm.parent(shoulder, module.skeleton)

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		self.shoulderControl = rig_control( side=side, name='shoulder', shape='pyramid',
		                            targetOffset=shoulder, modify=1,
		                            parentOffset=module.controls,lockHideAttrs=[
				'tx','ty','tz'], constrain=shoulder, scale =ctrlSize, rotateOrder=0 )

		pm.rotate( pm.PyNode( self.shoulderControl.ctrl+'.cv[:]' ), 0,0,-90, r=True, os=True )

		clavPos = pm.xform(shoulder, translation=True, query=True, ws=True)
		armPos = pm.xform(side+'_'+self.armName, translation=True, query=True, ws=True)
		clavLength = lengthVector( armPos, clavPos )
		if side == 'l':
			pm.move( pm.PyNode( self.shoulderControl.ctrl+'.cv[:]' ), clavLength,0,0, r=True,
			         os=True )
		else:
			pm.move(pm.PyNode(self.shoulderControl.ctrl + '.cv[:]'), -1*clavLength, 0, 0, r=True,
			        os=True)


		if pm.objExists(self.spineConnection):
			pm.parentConstraint(self.spineConnection, self.shoulderControl.offset, mo=True)


		if pm.objExists('rigModules_GRP'):
			pm.parent(module.top, 'rigModules_GRP')

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module

	def connectArmShoulder(self, side=''):

		if side != '':
			side = side+'_'

		fkCtrls = self.armControls['fk']
		hand = self.armControls['hand']

		#print 'self.shoulderControl '+str(self.shoulderControl.ctrl)
		pm.parentConstraint( self.shoulderControl.con , fkCtrls[0].offset,
		                     mo=True )

		pm.parentConstraint( self.shoulderControl.con, self.armTop,
		                     mo=True )

		handAim = rig_transform(0, name=side + 'handAim', type='locator',
		                            parent=self.armModule.parts).object
		shoulderAim = rig_transform(0, name=side + 'shoulderAim', type='locator',
		                        parent=self.armModule.parts).object

		pm.pointConstraint( hand.con, handAim )
		pm.pointConstraint( self.shoulderControl.con, shoulderAim )

		pistonTop = mm.eval('rig_makePiston("'+handAim+'", "'+shoulderAim+'", "'+side+'shoulderAim");')


		pistonChildren = pm.listRelatives( pistonTop, type='transform', c=True)

		pm.parentConstraint(self.spineConnection, pistonTop, mo=True)

		for child in pistonChildren:
			if child.stripNamespace().endswith('shoulderAim_LOCAimOffset'):
				pm.delete(pm.listRelatives(child, type='constraint'))
				pm.parentConstraint(self.spineConnection, child, mo=True )
			if child.stripNamespace().endswith('shoulderAim_LOC'):
				con = pm.parentConstraint( self.shoulderControl.offset, child,
				                           self.shoulderControl.modify,
				                          mo=True)
				pm.setAttr(con.interpType, 0)
				childConAttr = con.getWeightAliasList()[1]
				pm.addAttr(self.shoulderControl.ctrl, longName='followArm',
				           at='float', k=True, min=0,
				           max=10, defaultValue=3)
				pm.setDrivenKeyframe(childConAttr,
				                     cd=self.shoulderControl.ctrl.followArm,
				                     dv=0,
				                     v=0)
				pm.setDrivenKeyframe(childConAttr,
				                     cd=self.shoulderControl.ctrl.followArm,
				                     dv=10,
				                     v=1)
			if child.stripNamespace().endswith('handAim_LOCAimOffset'):
				pm.delete(pm.listRelatives(child, type='constraint'))
				pm.pointConstraint(hand.con, child, mo=True)

		# constrain auto pv
		pm.parentConstraint( side+'handAim_JNT', side+'shoulderAim_JNT',
		                     side+'autoArmPVOffset_GRP', mo=True )

		pm.parent(pistonTop, self.armModule.parts)


	def arm (self, side='', ctrlSize=1.0):
		name = side+'_arm'
		if side == '':
			name = 'arm'


		secColour = 'green'
		if side == 'r':
			secColour = 'magenta'
		elif side == 'l':
			secColour = 'deepskyblue'


		module = rig_module(name)
		self.armModule = module
		
		arm = self.armName
		elbow = self.elbowName
		hand = self.handName
		handFng = self.handFngName

		if side != '':
			arm = side + '_' + arm
			elbow = side + '_' + elbow
			hand = side + '_' + hand
			handFng = side + '_' + handFng

		chain = [arm, elbow, hand, handFng]

		pm.parent(arm, module.skeleton)

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
		ctrlSize = [ctrlSize,ctrlSize,ctrlSize]


		self.armTop = rig_transform(0, name=side + '_armTop',
		              target=arm, parent=module.parts).object

		armSkeletonParts = rig_transform(0, name=side + '_armSkeletonParts',
		                                 parent=self.armTop).object

		# chain result
		armResult = rig_transform(0, name=side + '_armResult', type='joint',
		                          target=arm, parent=armSkeletonParts,
		                          rotateOrder=2).object
		elbowResult = rig_transform(0, name=side + '_elbowResult', type='joint',
		                            target=elbow, rotateOrder=2).object
		handResult = rig_transform(0, name=side + '_handResult', type='joint',
		                           target=hand, rotateOrder=2).object
		handFngResult = rig_transform(0, name=side + '_handFngResult', type='joint',
		                           target=handFng, rotateOrder=2).object

		chainResult = [armResult, elbowResult, handResult,handFngResult]

		chainParent(chainResult)
		chainResult.reverse()

		# chain FK
		armFK = rig_transform(0, name=side+'_armFK', type='joint', target=arm,
		                      parent=armSkeletonParts, rotateOrder=2).object
		elbowFK = rig_transform(0, name=side+'_elbowFK', type='joint',
		                        target=elbow, rotateOrder=2).object
		handFK = rig_transform(0, name=side+'_handFK', type='joint', target=hand, rotateOrder=2
		                       ).object
		handFngFK = rig_transform(0, name=side + '_handFngFK', type='joint', target=handFng, rotateOrder=2
		).object

		chainFK = [ armFK, elbowFK, handFK, handFngFK ]

		chainParent(chainFK)
		chainFK.reverse()

		# chain IK
		armIK = rig_transform(0, name=side+'_armIK', type='joint', target=arm,
		                      parent=armSkeletonParts,rotateOrder=2).object
		elbowIK = rig_transform(0, name=side+'_elbowIK', type='joint',
		                        target=elbow, rotateOrder=2).object
		handIK = rig_transform(0, name=side+'_handIK', type='joint', target=hand, rotateOrder=2
		                       ).object
		handFngIK = rig_transform(0, name=side + '_handFngIK', type='joint', target=handFng, rotateOrder=2
		).object

		chainIK = [ armIK, elbowIK, handIK, handFngIK ]

		chainParent(chainIK)
		chainIK.reverse()

		# create ik
		ik = rig_ik(name, armIK, handIK, 'ikRPsolver')
		pm.parent(ik.handle, module.parts)


		poleVector = rig_control(side=side, name='armPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx','ry','rz'],
		                         targetOffset=[arm, hand],
		                         parentOffset=module.controls, scale=ctrlSizeQuarter )

		if side == 'r':
			pm.rotate(poleVector.ctrl.cv, 90, 0, 0, r=True, os=True)
		else:
			pm.rotate(poleVector.ctrl.cv, -90, 0, 0, r=True, os=True)


		pm.connectAttr(module.top.ikFkSwitch, poleVector.offset+'.visibility' )

		self.armControls['poleVector'] = poleVector

		pm.delete(pm.aimConstraint(elbow, poleVector.offset, mo=False))

		handPos = pm.xform(hand, translation=True, query=True, ws=True)
		elbowPos = pm.xform(elbow, translation=True, query=True, ws=True)
		poleVectorPos = pm.xform(poleVector.con, translation=True, query=True,
		                         ws=True)

		pvDistance = lengthVector(elbowPos, poleVectorPos)

		pm.xform(poleVector.offset, translation=[pvDistance, 0, 0], os=True,
		           r=True)

		pm.poleVectorConstraint(poleVector.con, ik.handle)  # create pv

		#pm.move(poleVector.offset, [0, -pvDistance*40, 0], relative=True,
		 #       objectSpace=True)

		pvDistance = lengthVector(handPos, elbowPos)
		#pm.move(poleVector.offset, [pvDistance*2, 0, 0], relative=True, objectSpace=True)
		pm.move(poleVector.offset, [0, 0, -1*(pvDistance * 2)], relative=True,worldSpace=True)

		pm.rotate(poleVector.ctrl.cv, 0, 0, 90, r=True, os=True)
		if side == 'r':
			pm.rotate(poleVector.ctrl.cv, 0, 30, 0, r=True, os=True)
		else:
			pm.rotate(poleVector.ctrl.cv, 0, -30, 0, r=True, os=True)

		print 'ik handle '+ik.handle
		handControl = rig_control(side=side,name='hand', shape='box', modify=2,
		                          parentOffset=module.controls, scale=ctrlSize,
		                          rotateOrder=2)

		pm.delete(pm.pointConstraint(hand, handControl.offset))
		#pm.parentConstraint( handControl.con, ik.handle, mo=True )

		handControl.gimbal = createCtrlGimbal( handControl )
		handControl.pivot = createCtrlPivot( handControl )

		constrainObject(handControl.offset,
		                [self.spineConnection, self.spineFullBodyCtrl.con ,self.centerConnection ,
		                 'worldSpace_GRP'],
		                handControl.ctrl, ['spine','fullBody ','spineLower','world'],
		                type='parentConstraint')

		pm.addAttr(handControl.ctrl, longName='twist', at='float', k=True)
		pm.connectAttr(handControl.ctrl.twist, ik.handle.twist)

		pm.connectAttr(module.top.ikFkSwitch, handControl.offset + '.visibility')

		self.armControls['hand'] = handControl

		'''
		handIK_loc = rig_transform(0, name= side+'_handIKBuffer', type='locator',
		                           target=handIK, parent = handControl.con).object
		pm.hide(handIK_loc)
		pm.parentConstraint(handIK_loc, handIK, mo=True, skipTranslate=(
		'x','y','z'))
		'''

		handBallControl = rig_control(side=side, name='handBall', shape='cylinder', modify=1,
		                          parentOffset=module.controls, scale=ctrlSizeQuarter,
		                          rotateOrder=2, colour =secColour)

		pm.delete(pm.pointConstraint(handFng, handBallControl.offset))
		handBallControl.gimbal = createCtrlGimbal(handBallControl)
		#pm.parentConstraint( handControl.con, handBallControl.offset, mo=True )
		pm.parent( handBallControl.offset, handControl.con )
		pm.parentConstraint( handBallControl.con, ik.handle, mo=True )

		pm.connectAttr(module.top.ikFkSwitch, handBallControl.offset + '.visibility')

		pm.rotate(handBallControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)

		constrainObject(handBallControl.modify,
		                [handBallControl.offset, self.spineFullBodyCtrl.con,'worldSpace_GRP'],
		                handBallControl.ctrl, ['hand', 'fullBody' ,'world'],
		                type='orientConstraint')

		wristBallLoc = rig_transform(0, name=side + '_wristBallAim', type='locator',
		                          parent=module.parts, target=hand).object
		fngBallLoc = rig_transform(0, name=side + '_fngBallAim', type='locator',
		                             parent=module.parts, target=handFng).object

		for obj in (wristBallLoc, fngBallLoc):
			pm.setAttr(obj + '.rotateX', -90)
			pm.setAttr(obj + '.rotateY', 0)
			pm.setAttr(obj + '.rotateZ', 0)

		pm.parentConstraint(  elbowIK,  wristBallLoc, mo=True )
		pm.parentConstraint(  handBallControl.con,  fngBallLoc, mo=True )

		handBallAimTop = mm.eval('rig_makePiston("'+wristBallLoc+'", "'+fngBallLoc+'", "'+side+'_handBallAim");')
		pm.parent( side+'_wristBallAim_LOCUp', side+'_fngBallAim_LOCAimOffset' )

		pm.orientConstraint( side+'_wristBallAim_JNT', handIK, mo=True )

		pm.delete(pm.listRelatives(side+'_wristBallAim_LOCAimOffset', type='constraint'))
		pm.pointConstraint( handIK, side+'_wristBallAim_LOCAimOffset', mo=True )
		pm.orientConstraint(elbowIK, side + '_wristBallAim_LOCAimOffset', mo=True)

		pm.parent( handBallAimTop, module.parts )

		# auto pole vector
		autoPVOffset = rig_transform(0, name=side+'_autoArmPVOffset',
		                             parent=module.parts, target = poleVector.con
		).object
		autoPVLoc = rig_transform(0, name=side+'_autoArmPV' ,type='locator',
		                          parent=autoPVOffset,target=autoPVOffset ).object

		#pm.parentConstraint( self.spineConnection, autoPVOffset, mo=True )
		#pm.pointConstraint( self.spineConnection, handControl.con,autoPVLoc , mo=True)

		constrainObject(poleVector.offset,
		                [autoPVLoc, self.spineConnection ,self.centerConnection,
		                 self.spineFullBodyCtrl.con,
		                 'worldSpace_GRP'],
		                poleVector.ctrl, ['auto', 'spineUpper', 'spineLower','fullBody', 'world'],
		                type='parentConstraint')


		fingersControl = rig_control(side=side, name='fingers', shape='pyramid', modify=1,
		                             parentOffset=module.controls, scale=ctrlSizeQuarter,
		                             rotateOrder=2, lockHideAttrs=['tx','ty','tz'])

		self.armControls['fingers'] = fingersControl

		pm.delete(pm.parentConstraint(handFng, fingersControl.offset))
		pm.parentConstraint( fingersControl.con, handFngIK, mo=True )
		pm.parentConstraint( handBallControl.con, fingersControl.offset, mo=True )

		pm.connectAttr(module.top.ikFkSwitch, fingersControl.offset + '.visibility')

		pm.addAttr(fingersControl.ctrl, ln='SHAPE', at='enum',
		           enumName='___________',
		           k=True)
		fingersControl.ctrl.SHAPE.setLocked(True)
		pm.addAttr(fingersControl.ctrl, longName='curl', at='float', k=True, min=-10,
		           max=10, dv=0)
		pm.addAttr(fingersControl.ctrl, longName='curlThumb', at='float', k=True, min=-10,
		           max=10, dv=0)
		pm.addAttr(fingersControl.ctrl, longName='splay', at='float', k=True, min=-10,
		           max=10, dv=0)

		constrainObject(fingersControl.modify,
		                [ handControl.con ,fingersControl.offset, self.spineFullBodyCtrl.con,
		                  'worldSpace_GRP'],
		                fingersControl.ctrl, ['wrist', 'handBall','fullBody','world'],
		                type='orientConstraint')

		fingersPos = pm.xform(fingersControl.con, translation=True, query=True, ws=True)
		endPos = pm.xform(side+'_handJEnd_JNT', translation=True, query=True, ws=True)

		fngLength = lengthVector(fingersPos, endPos  )*1.5

		pm.rotate(fingersControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)
		if side == 'l':
			pm.move(fingersControl.ctrl.cv, [fngLength, 0, 0], relative=True, os=True) # os = True
		else:
			pm.move(fingersControl.ctrl.cv, [fngLength*-1, 0, 0], relative=True, os=True)

		# create ik stretchy and soft pop
		endBlendLoc = rig_ikStretchySoftPop(side, name, chainIK, module, handControl,
		                                    ctrlSizeQuarter,
		                            self.armTop )

		pm.pointConstraint( endBlendLoc, handBallControl.offset, mo=True )


		# create fk
		print 'fk chain '+ str(chainFK)
		fkCtrls = fkControlChain(chainFK, scale=ctrlSize)
		for fk in fkCtrls:
			pm.parent(fk.offset, module.controls)
			pm.setDrivenKeyframe( fk.offset+'.visibility' ,
			                     cd=module.top.ikFkSwitch,
			                     dv=1,
			                     v=0)
			pm.setDrivenKeyframe( fk.offset+'.visibility' ,
			                     cd=module.top.ikFkSwitch,
			                     dv=0,
			                     v=1)
		elbowFk = fkCtrls[1]
		rotateAxis = ['rx','ry','rz']
		if self.elbowAxis in rotateAxis: rotateAxis.remove(self.elbowAxis)
		for at in rotateAxis:
			elbowFk.ctrl.attr(at).setKeyable(False)
			elbowFk.ctrl.attr(at).setLocked(True)


		self.armControls['fk'] = fkCtrls


		self.connectIkFkSwitch(chains=[ chainResult, chainIK, chainFK ],
		                       module = module ,name=name  )

		# constrain result to skeleton
		for i in range(0, len(chain)):
			pm.parentConstraint( chainResult[i], chain [i], mo=True)

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module

	def hand(self, side='', axis='rz',ctrlSize=1.0):
		abc = list(string.ascii_lowercase)

		name = side + '_fingers'
		sideName = side + '_'
		if side == '':
			name = 'fingers'
			sideName = ''



		module = rig_module(name)
		self.fingersModule = module

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]



		rotateAxis = ['rx','ry','rz']

		rotateAxis.remove(axis)

		skipAxis = rotateAxis + ['tx', 'ty','tz' ]

		for finger in ( self.fngThumb, self.fngIndex, self.fngMid, self.fngRing,
		                self.fngPinky ):

			fng = finger

			if side != '':
				fng = side + '_' + fng

			#print 'finger is '+fng
			if pm.objExists(fng):

				chainFingers = rig_chain( fng )

				childrenFngs = chainFingers.chainChildren

				childrenFngs.pop(len(childrenFngs)-1)

				sc = simpleControls(fng,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls)

				fngCtrl = sc[fng]
				baseLimit = 0.2
				pm.transformLimits( fngCtrl.ctrl, tx=(-1*baseLimit, baseLimit), etx=(1, 1))
				pm.transformLimits( fngCtrl.ctrl, ty=(-1*baseLimit, baseLimit), ety=(1, 1))
				pm.transformLimits( fngCtrl.ctrl, tz=(-1*baseLimit, baseLimit), etz=(1, 1))

				if 'Thumb' in fng:
					if pm.objExists(sideName+'handJA_JNT'):
						pm.parentConstraint(  sideName+'handJA_JNT', fngCtrl.offset, mo=True)
				else:
					if pm.objExists(sideName + 'handJB_JNT'):
						pm.parentConstraint(sideName + 'handJA_JNT', fngCtrl.offset, mo=True)
						pm.orientConstraint(sideName + 'handJB_JNT', fngCtrl.modify[0], mo=True, skip='x')

				sc = simpleControls(childrenFngs,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls,
				               lockHideAttrs=skipAxis)

				# fk control
				armControl = self.armControls['fingers'].ctrl
				if 'Thumb' in fng:
					if pm.objExists(armControl.curlThumb):
						for key in sc:
							control = sc[key]
							rig_animDrivenKey(armControl.curlThumb, (-10, 0, 10),
							                  control.modify[0] + '.rotateZ', (-90, 0, 90 ))

						rig_animDrivenKey(armControl.curlThumb, (-10, 0, 10),
						                  fngCtrl.modify[1] + '.rotateZ', (-90, 0, 90 ))
				else:
					if pm.objExists(armControl.curl):
						for key in sc:
							control = sc[key]
							rig_animDrivenKey(armControl.curl, (-10, 0, 10),
							                  control.modify[0] + '.rotateZ', (-90, 0, 90 ))

						rig_animDrivenKey(armControl.curl, (-10, 0, 10),
						                  fngCtrl.modify[1] + '.rotateZ', (-90, 0, 90 ))

				pm.parent( fng, module.skeleton )

			else:
				print fng + ' does not exist...Skipping.'

		cmds.dgdirty(allPlugs=True)
		cmds.refresh()

		return module


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

		poleVector = rig_control(side=side, name='legPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx', 'ry', 'rz'],
		                         targetOffset=[leg, foot],
		                         parentOffset=module.controls, scale=ctrlSizeQuarter)

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
		#pm.move(poleVector.offset, [pvDistance * 2, 0, 0], relative=True, objectSpace=True)
		pm.move(poleVector.offset, [0, 0, pvDistance * 2],relative=True, worldSpace=True)

		print 'ik handle ' + ik.handle

		# ## MAKE FOOT CONTROL
		footControl = rig_control(side=side, name='foot', shape='box', modify=2,
		                          parentOffset=module.controls, scale=ctrlSize,
		                          rotateOrder=2)

		pm.delete(pm.pointConstraint(foot, footControl.offset))

		footControl.gimbal = createCtrlGimbal(footControl)
		footControl.pivot = createCtrlPivot(footControl)

		constrainObject(footControl.offset,
		                [self.pelvisConnection, self.centerConnection,self.spineFullBodyCtrl.con,
		                 'worldSpace_GRP'],
		                footControl.ctrl, ['pelvis', 'spineLower', 'fullBody' , 'world'],
		                type='parentConstraint')

		pm.addAttr(footControl.ctrl, ln='MOTION', at='enum',
		           enumName='___________',
		           k=True)
		footControl.ctrl.MOTION.setLocked(True)
		pm.addAttr(footControl.ctrl, longName='twist', at='float', k=True)
		pm.addAttr(footControl.ctrl, longName='footRoll', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.connectAttr(footControl.ctrl.twist, ik.handle.twist)

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
		                              parentOffset=module.controls, scale=ctrlSizeQuarter,
		                              rotateOrder=2, colour=secColour)

		pm.delete(pm.pointConstraint(footB, footBallControl.offset))
		pm.parentConstraint(footBallControl.con, ik.handle, mo=True)

		pm.connectAttr(module.top.ikFkSwitch, footBallControl.offset + '.visibility')

		pm.rotate(footBallControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)
		pm.move(footBallControl.ctrl.cv, [0, 0.5, 0], relative=True)

		constrainObject(footBallControl.modify[0],
		                [footBallControl.offset, 'worldSpace_GRP'],
		                footBallControl.ctrl, ['foot', 'world'],
		                type='orientConstraint')

		wristBallLoc = rig_transform(0, name=side + '_footBallAim', type='locator',
		                             parent=module.parts, target=foot).object
		fngBallLoc = rig_transform(0, name=side + '_toesBallAim', type='locator',
		                           parent=module.parts, target=footB).object

		for obj in (wristBallLoc, fngBallLoc):
			pm.setAttr(obj + '.rotateX', 0)
			pm.setAttr(obj + '.rotateY', 0)
			pm.setAttr(obj + '.rotateZ', -90)

		pm.parentConstraint(kneeIK, wristBallLoc, mo=True)
		pm.parentConstraint(footBallControl.con, fngBallLoc, mo=True)

		footBallAimTop = mm.eval('rig_makePiston("' + wristBallLoc + '", "' + fngBallLoc + '", "' + side + '_footBallAim");')
		pm.parent(side + '_footBallAim_LOCUp', side + '_toesBallAim_LOCAimOffset')

		pm.orientConstraint(side + '_footBallAim_JNT', footIK, mo=True)

		pm.delete(pm.listRelatives(side + '_footBallAim_LOCAimOffset', type='constraint'))
		pm.pointConstraint(footIK, side + '_footBallAim_LOCAimOffset', mo=True)
		pm.orientConstraint(kneeIK, side + '_footBallAim_LOCAimOffset', mo=True)

		pm.parent(footBallAimTop, module.parts)

		### MAKE FOOT TOES CONTROL
		footToesControl = rig_control(side=side, name='footToes', shape='cylinder', modify=2,
		                              parentOffset=module.controls, scale=ctrlSizeQuarter,
		                              rotateOrder=2, colour=secColour)

		pm.delete(pm.pointConstraint(toes, footToesControl.offset))
		#pm.parentConstraint(footControl.con, footToesControl.offset, mo=True)
		pm.parent( footToesControl.offset, footControl.con )
		pm.parentConstraint(footToesControl.con, footBallControl.offset, mo=True)

		pm.connectAttr(module.top.ikFkSwitch, footToesControl.offset + '.visibility')

		pm.rotate(footToesControl.ctrl.cv, [0, 0, 90], relative=True, objectSpace=True)

		constrainObject(footToesControl.modify[0],
		                [footToesControl.offset, 'worldSpace_GRP'],
		                footToesControl.ctrl, ['foot', 'world'],
		                type='orientConstraint')

		footBallLoc = rig_transform(0, name=side + '_footBallBAim', type='locator',
		                             parent=module.parts, target=footB).object
		footToesLoc = rig_transform(0, name=side + 'footToesAim', type='locator',
		                           parent=module.parts, target=toes).object

		for obj in (footBallLoc, footToesLoc):
			pm.setAttr(obj + '.rotateX', 0)
			pm.setAttr(obj + '.rotateY', 0)
			pm.setAttr(obj + '.rotateZ', -90)

		pm.parentConstraint(footIK, footBallLoc, mo=True)
		pm.parentConstraint(footToesControl.con, footToesLoc, mo=True)

		footToesAimTop = mm.eval('rig_makePiston("' + footBallLoc + '", "' + footToesLoc + '", "' + side + '_footToesAim");')
		pm.parent(side + '_footBallBAim_LOCUp', side + '_footToesAim_LOCAimOffset')

		pm.orientConstraint(side + '_footBallBAim_JNT', footBIK, mo=True)

		pm.parent(footToesAimTop, module.parts)

		## MAKE FOOT ROLLS
		pm.addAttr(footControl.ctrl, ln='ROLLS', at='enum',
		           enumName='___________',
		           k=True)
		footControl.ctrl.ROLLS.setLocked(True)
		rollTip = rig_transform(0, name=side + '_footRollTip',
		                            parent=footControl.gimbal.ctrl,
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
		pm.parent( footControl.con, rollOut )

		pm.delete(pm.ls(side+"_footRoll*_LOC"))

		pm.addAttr(footControl.ctrl, longName='rollTip', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.addAttr(footControl.ctrl, longName='rollHeel', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.addAttr(footControl.ctrl, longName='rollIn', at='float', k=True, min=0,
		           max=10, dv=0)
		pm.addAttr(footControl.ctrl, longName='rollOut', at='float', k=True, min=0,
		           max=10, dv=0)

		flipRoll = 1
		if side == 'r':
			flipRoll = -1
		rig_animDrivenKey(footControl.ctrl.rollTip, (0, 10),
		                  rollTip+'.rotateX', (0, 90 ))
		rig_animDrivenKey(footControl.ctrl.rollHeel, (0, 10),
		                  rollHeel+'.rotateX', (0, -90 ))
		rig_animDrivenKey(footControl.ctrl.rollIn, (0, 10),
		                  rollIn+'.rotateZ', (0, 90*flipRoll ))
		rig_animDrivenKey(footControl.ctrl.rollOut, (0, 10),
		                  rollOut + '.rotateZ', (0, -90*flipRoll ))

		## do foot roll with footBall and footToes modify
		rig_animDrivenKey(footControl.ctrl.footRoll, (0,5, 10),
		                  footBallControl.modify[1] + '.rotateX', (0, 20,30 ))
		rig_animDrivenKey(footControl.ctrl.footRoll, (0, 5, 10),
		                  footToesControl.modify[1] + '.rotateX', (0, 0, 40 ))

		# ## MAKE TOES CONTROL
		toesControl = rig_control(side=side, name='toes', shape='pyramid', modify=1,
		                             parentOffset=module.controls, scale=ctrlSizeQuarter,
		                             rotateOrder=2, lockHideAttrs=['tx','ty','tz'])

		self.legControls['toes'] = toesControl

		pm.delete(pm.parentConstraint(toes, toesControl.offset))
		pm.parentConstraint(toesControl.con, toesIK, mo=True)
		pm.parentConstraint(footToesControl.con, toesControl.offset, mo=True)

		pm.connectAttr(module.top.ikFkSwitch, toesControl.offset + '.visibility')

		constrainObject(toesControl.modify,
		                [footControl.con, toesControl.offset, 'worldSpace_GRP'],
		                toesControl.ctrl, ['foot', 'footBall', 'world'],
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

		# make leg foot aim
		footAimLoc = rig_transform(0, name=side + '_footLegAim', type='locator',
		                        parent=module.parts).object
		legAimLoc = rig_transform(0, name=side + '_legFootAim', type='locator',
		                            parent=module.parts).object

		pm.pointConstraint( self.legTop, legAimLoc  )
		pm.pointConstraint( footControl.con, footAimLoc  )
		pm.setAttr( footAimLoc+'.rotateZ', -90 )
		pm.setAttr(legAimLoc+'.rotateZ', -90)

		legAimTop = mm.eval('rig_makePiston("'+legAimLoc+'", "'+footAimLoc+'", "'+side+'_legAim");')

		pm.parentConstraint( side+'_legFootAim_JNT', side+'_footLegAim_JNT', autoPVOffset, mo=True )

		pm.parent( legAimTop, module.parts )



		# create ik stretchy and soft pop
		endBlendLoc = rig_ikStretchySoftPop(side, name, chainIK, module, footControl,
		                                    ctrlSizeQuarter,
		                                    self.legTop)

		pm.pointConstraint(endBlendLoc, footToesControl.offset, mo=True)

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


def rig_bipedPrepare():

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
		cmds.parent( 'neckJA_JNT', w=True)
	except ValueError:
		print 'Skipping neckJA_JNT as it does not exist'



def rig_bipedFinalize():

	# world space hands and feet
	try:
		for s in ['l', 'r']:
			pm.setAttr(s+'_foot_CTRL.space', 3)
			pm.setAttr(s+'_hand_CTRL.space', 1)
	except:
		pass
