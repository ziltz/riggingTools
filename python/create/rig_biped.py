


from make.rig_ik import rig_ik
from rutils.rig_chain import *
from make.rig_controls import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform
from rutils.rig_nodes import blendColors
from rutils.rig_math import *

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

		self.elbowAxis = 'rx'

		self.fngThumb = 'fngThumbJA_JNT'
		self.fngIndex = 'fngIndJA_JNT'
		self.fngMid = 'fngMidJA_JNT'
		self.fngRing = 'fngRingJA_JNT'
		self.fngPinky = 'fngPnkyJA_JNT'

		self.armJoints = []

		# values : poleVector, hand, fk
		self.armControls = {}
		self.armTop = ''
		self.shoulderControl = None

		self.spineConnection = 'spineJF_JNT'
		self.centerConnection = 'spineJA_JNT'
		self.pelvisConnection = 'pelvisJA_JNT'

		self.spineModule = ''
		self.neckModule = ''
		self.headModule = ''
		self.shoulderModule = ''
		self.armModule = ''
		self.legModule = ''
		self.fingersModule = ''


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
		
		return

	def arm (self, side='', ctrlSize=1.0):
		name = side+'_arm'
		if side == '':
			name = 'arm'

		module = rig_module(name)
		self.armModule = module
		
		arm = self.armName
		elbow = self.elbowName
		hand = self.handName

		if side != '':
			arm = side + '_' + arm
			elbow = side + '_' + elbow
			hand = side + '_' + hand

		chain = [arm, elbow, hand]

		pm.parent(arm, module.skeleton)

		print 'arm '+arm
		print 'elbow '+elbow
		print 'hand '+hand

		ctrlSizeHalf = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
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
		chainResult = [armResult, elbowResult, handResult]

		chainParent(chainResult)
		chainResult.reverse()

		# chain FK
		armFK = rig_transform(0, name=side+'_armFK', type='joint', target=arm,
		                      parent=armSkeletonParts, rotateOrder=2).object
		elbowFK = rig_transform(0, name=side+'_elbowFK', type='joint',
		                        target=elbow, rotateOrder=2).object
		handFK = rig_transform(0, name=side+'_handFK', type='joint', target=hand, rotateOrder=2
		                       ).object
		chainFK = [ armFK, elbowFK, handFK ]

		chainParent(chainFK)
		chainFK.reverse()

		# chain IK
		armIK = rig_transform(0, name=side+'_armIK', type='joint', target=arm,
		                      parent=armSkeletonParts,rotateOrder=2).object
		elbowIK = rig_transform(0, name=side+'_elbowIK', type='joint',
		                        target=elbow, rotateOrder=2).object
		handIK = rig_transform(0, name=side+'_handIK', type='joint', target=hand, rotateOrder=2
		                       ).object
		chainIK = [ armIK, elbowIK, handIK ]

		chainParent(chainIK)
		chainIK.reverse()

		# create ik
		ik = rig_ik(name, armIK, handIK, 'ikRPsolver')
		pm.parent(ik.handle, module.parts)


		poleVector = rig_control(side=side, name='armPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx','ry','rz'],
		                         targetOffset=[arm, hand],
		                         parentOffset=module.controls, scale=ctrlSizeHalf )

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
		pm.parentConstraint( handControl.con, ik.handle, mo=True )

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

		handIK_loc = rig_transform(0, name= side+'_handIKBuffer', type='locator',
		                           target=handIK, parent = handControl.con).object
		pm.hide(handIK_loc)
		pm.parentConstraint(handIK_loc, handIK, mo=True, skipTranslate=(
		'x','y','z'))


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
		if side == '':
			name = 'fingers'

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

				simpleControls(fng,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls,
				               lockHideAttrs=['tx','ty','tz'])

				simpleControls(childrenFngs,
				               modify=2, scale=ctrlSize,
				               parentOffset=module.controls,
				               lockHideAttrs=skipAxis)

			else:
				print fng + ' does not exist...Skipping.'





		return


	def pelvis (self):
		return

	def leg (self, side):
		return
		


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
