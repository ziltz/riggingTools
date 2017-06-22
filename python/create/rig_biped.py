


from make.rig_ik import rig_ik
from rutils.rig_chain import *
from make.rig_controls import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform
from rutils.rig_nodes import blendColors
from rutils.rig_math import *
from rutils.rig_anim import *

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm
import string

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

		# values : poleVector, hand, fk
		self.armControls = {}
		self.armTop = ''
		self.shoulderControl = None

		# values : poleVector, foot, fk
		self.legControls = {}
		self.legTop = ''
		self.pelvisControl = None

		self.spineConnection = 'spineJF_JNT'
		self.centerConnection = 'spineJA_JNT'
		self.pelvisConnection = 'pelvisJA_JNT'

		self.spineModule = ''
		self.neckModule = ''
		self.headModule = ''

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

		print 'chain[0] '+ str(chains[0])
		print 'chain[1] ' + str(chains[1])
		print 'chain[2] ' + str(chains[2])

		for i in range(0, len(chains[0])):

			blendColors(chains[1][i], chains[2][i], chains[0][i], name=name+str(i),
			            driverAttr=self.switchLoc+'.'+name,
			            attribute='rotate')

		switchAttr = getattr(self.switchLoc, name)
		pm.connectAttr( switchAttr, module.top.ikFkSwitch  )


	def spine(self):
		return
		
	def neck(self):
		return
		
	def head(self):
		return

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

		print 'shoulder ' + shoulder

		ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
		ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

		self.shoulderControl = rig_control( side=side, name='shoulder', shape='pyramid',
		                            targetOffset=shoulder, modify=1,
		                            parentOffset=module.controls,lockHideAttrs=[
				'tx','ty','tz'], constrain=shoulder, scale =ctrlSize, rotateOrder=0 )

		if pm.objExists(self.spineConnection):
			pm.parentConstraint(self.spineConnection, self.shoulderControl.offset, mo=True)


		if pm.objExists('rigModules_GRP'):
			pm.parent(module.top, 'rigModules_GRP')

		return module

	def connectArmShoulder(self, side=''):

		if side != '':
			side = side+'_'

		fkCtrls = self.armControls['fk']
		hand = self.armControls['hand']

		print 'self.shoulderControl '+str(self.shoulderControl.ctrl)
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
				           max=10, defaultValue=5)
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
		pm.move(poleVector.offset, [pvDistance*2, 0, 0], relative=True, objectSpace=True)


		print 'ik handle '+ik.handle
		handControl = rig_control(side=side,name='hand', shape='box', modify=2,
		                          parentOffset=module.controls, scale=ctrlSize,
		                          rotateOrder=2)

		pm.delete(pm.pointConstraint(hand, handControl.offset))
		#pm.parentConstraint( handControl.con, ik.handle, mo=True )

		handControl.gimbal = createCtrlGimbal( handControl )
		handControl.pivot = createCtrlPivot( handControl )

		constrainObject(handControl.offset,
		                [self.spineConnection, self.centerConnection ,
		                 'worldSpace_GRP'],
		                handControl.ctrl, ['spine','main','world'],
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
		pm.parentConstraint( handControl.con, handBallControl.offset, mo=True )
		pm.parentConstraint( handBallControl.con, ik.handle, mo=True )

		pm.connectAttr(module.top.ikFkSwitch, handBallControl.offset + '.visibility')

		pm.rotate(handBallControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)

		constrainObject(handBallControl.modify,
		                [handBallControl.offset, 'worldSpace_GRP'],
		                handBallControl.ctrl, ['hand', 'world'],
		                type='orientConstraint')

		wristBallLoc = rig_transform(0, name=side + '_wristBallAim', type='locator',
		                          parent=module.parts, target=hand).object
		fngBallLoc = rig_transform(0, name=side + '_fngBallAim', type='locator',
		                             parent=module.parts, target=handFng).object

		pm.parentConstraint(  elbowIK,  wristBallLoc, mo=True )
		pm.parentConstraint(  handBallControl.con,  fngBallLoc, mo=True )

		handBallAimTop = mm.eval('rig_makePiston("'+wristBallLoc+'", "'+fngBallLoc+'", "'+side+'_handBallAim");')
		pm.parent( side+'_wristBallAim_LOCUp', side+'_fngBallAim_LOCAimOffset' )

		pm.orientConstraint( side+'_wristBallAim_JNT', handIK, mo=True )

		pm.parent( handBallAimTop, module.parts )

		# auto pole vector
		autoPVOffset = rig_transform(0, name=side+'_autoPVOffset',
		                             parent=module.parts, target = poleVector.con
		).object
		autoPVLoc = rig_transform(0, name=side+'_autoPV' ,type='locator',
		                          parent=autoPVOffset,target=autoPVOffset ).object

		pm.parentConstraint( self.spineConnection, autoPVOffset, mo=True )
		pm.pointConstraint( self.spineConnection, handControl.con,autoPVLoc , mo=True)

		constrainObject(poleVector.offset,
		                [autoPVLoc, self.spineConnection,self.centerConnection,
		                 'worldSpace_GRP'],
		                poleVector.ctrl, ['auto', 'spine', 'main', 'world'],
		                type='parentConstraint')


		fingersControl = rig_control(side=side, name='fingers', shape='pyramid', modify=1,
		                             parentOffset=module.controls, scale=ctrlSizeQuarter,
		                             rotateOrder=2, lockHideAttrs=['tx','ty','tz'])

		pm.delete(pm.parentConstraint(handFng, fingersControl.offset))
		pm.parentConstraint( fingersControl.con, handFngIK, mo=True )
		pm.parentConstraint( handBallControl.con, fingersControl.offset, mo=True )

		pm.connectAttr(module.top.ikFkSwitch, fingersControl.offset + '.visibility')

		constrainObject(fingersControl.modify,
		                [ handControl.con ,fingersControl.offset, 'worldSpace_GRP'],
		                fingersControl.ctrl, ['wrist', 'handBall','world'],
		                type='orientConstraint')

		fingersPos = pm.xform(fingersControl.con, translation=True, query=True, ws=True)
		endPos = pm.xform(side+'_handJEnd_JNT', translation=True, query=True, ws=True)

		fngLength = lengthVector(fingersPos, endPos  )

		if side == 'l':
			pm.move(fingersControl.ctrl.cv, [fngLength, 0, 0], relative=True)
		else:
			pm.move(fingersControl.ctrl.cv, [fngLength*-1, 0, 0], relative=True)


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

			print 'finger is '+fng
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

				simpleControls(childrenFngs,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls,
				               lockHideAttrs=skipAxis)

				pm.parent( fng, module.skeleton )

			else:
				print fng + ' does not exist...Skipping.'




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
		                                   targetOffset=pelvis, modify=1,
		                                   parentOffset=module.controls, lockHideAttrs=[
				'tx', 'ty', 'tz'], constrain=pelvis, scale=ctrlSize, rotateOrder=0)

		if pm.objExists(self.centerConnection):
			pm.parentConstraint(self.centerConnection, self.pelvisControl.offset, mo=True)

		if pm.objExists('rigModules_GRP'):
			pm.parent(module.top, 'rigModules_GRP')

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

		pm.poleVectorConstraint(poleVector.con, ik.handle)  # create pv

		# pm.move(poleVector.offset, [0, -pvDistance*40, 0], relative=True,
		#       objectSpace=True)

		pvDistance = lengthVector(footPos, kneePos)
		pm.move(poleVector.offset, [pvDistance * 2, 0, 0], relative=True, objectSpace=True)

		print 'ik handle ' + ik.handle

		# ## MAKE FOOT CONTROL
		footControl = rig_control(side=side, name='foot', shape='box', modify=2,
		                          parentOffset=module.controls, scale=ctrlSize,
		                          rotateOrder=2)

		pm.delete(pm.pointConstraint(foot, footControl.offset))

		footControl.gimbal = createCtrlGimbal(footControl)
		footControl.pivot = createCtrlPivot(footControl)

		constrainObject(footControl.offset,
		                [self.pelvisConnection, self.centerConnection,
		                 'worldSpace_GRP'],
		                footControl.ctrl, ['pelvis', 'spine', 'world'],
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

		pm.parentConstraint(self.centerConnection, autoPVOffset, mo=True)
		pm.pointConstraint(self.centerConnection, footControl.con, autoPVLoc, mo=True)

		constrainObject(poleVector.offset,
		                [autoPVLoc, self.pelvisConnection, self.centerConnection,
		                 'worldSpace_GRP'],
		                poleVector.ctrl, ['auto', 'pelvis', 'main', 'world'],
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

		pm.parentConstraint(kneeIK, wristBallLoc, mo=True)
		pm.parentConstraint(footBallControl.con, fngBallLoc, mo=True)

		footBallAimTop = mm.eval('rig_makePiston("' + wristBallLoc + '", "' + fngBallLoc + '", "' + side + '_footBallAim");')
		pm.parent(side + '_footBallAim_LOCUp', side + '_toesBallAim_LOCAimOffset')

		pm.orientConstraint(side + '_footBallAim_JNT', footIK, mo=True)

		pm.parent(footBallAimTop, module.parts)

		### MAKE FOOT TOES CONTROL
		footToesControl = rig_control(side=side, name='footToes', shape='cylinder', modify=2,
		                              parentOffset=module.controls, scale=ctrlSizeQuarter,
		                              rotateOrder=2, colour=secColour)

		pm.delete(pm.pointConstraint(toes, footToesControl.offset))
		pm.parentConstraint(footControl.con, footToesControl.offset, mo=True)
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

		pm.delete(pm.ls("?_footRoll*_LOC"))

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

		'''
		if side == 'l':
			pm.move(toesControl.ctrl.cv, [0, 0, toesLength], relative=True)
		else:
			pm.move(toesControl.ctrl.cv, [0, 0, toesLength * -1], relative=True)
		'''

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
						pm.orientConstraint(sideName + 'toesJA_JNT', toeCtrl.modify[0], mo=True, skip='x')

				simpleControls(childrenFngs,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls,
				               lockHideAttrs=skipAxis)

				pm.parent(toe, module.skeleton)

			else:
				print toe + ' does not exist...Skipping.'

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
