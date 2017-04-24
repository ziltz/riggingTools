


from make.rig_ik import rig_ik
from rutils.rig_chain import *
from make.rig_controls import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform
from rutils.rig_nodes import blendColors

import pymel.core as pm
import maya.mel as mm

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

		self.armJoints = []

		# values : poleVector, hand, fk
		self.armControls = {}
		self.armTop = ''
		self.shoulderControl = None

		self.spineConnection = 'spineJF_JNT'
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
				'tx','ty','tz'], constrain=shoulder, scale =ctrlSize )

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
		
		for child in pistonChildren:
			if 'shoulderAim_LOCAimOffset' in repr(child):
				pm.delete(pm.listRelatives(child, type='constraint'))
				pm.parentConstraint(self.spineConnection, child, mo=True )
			if 'shoulderAim_LOC' in repr(child):
				con = pm.parentConstraint([self.shoulderControl.offset, child], self.shoulderControl.modify,
				                          mo=True)
				childConAttr = con.getWeightAliasList()[1]
				pm.addAttr(self.shoulderControl.ctrl, longName='aim', at='float', k=True, min=0,
				           max=10, defaultValue=5)
				pm.setDrivenKeyframe(childConAttr,
				                     cd=self.shoulderControl.ctrl.aim,
				                     dv=0,
				                     v=0)
				pm.setDrivenKeyframe(childConAttr,
				                     cd=self.shoulderControl.ctrl.aim,
				                     dv=10,
				                     v=1)
				
				
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
		                          target=arm, parent=armSkeletonParts).object
		elbowResult = rig_transform(0, name=side + '_elbowResult', type='joint', target=elbow).object
		handResult = rig_transform(0, name=side + '_handResult', type='joint', target=hand).object
		chainResult = [armResult, elbowResult, handResult]

		chainParent(chainResult)
		chainResult.reverse()

		# chain FK
		armFK = rig_transform(0, name=side+'_armFK', type='joint', target=arm, parent=armSkeletonParts).object
		elbowFK = rig_transform(0, name=side+'_elbowFK', type='joint', target=elbow).object
		handFK = rig_transform(0, name=side+'_handFK', type='joint', target=hand).object
		chainFK = [ armFK, elbowFK, handFK ]

		chainParent(chainFK)
		chainFK.reverse()

		# chain IK
		armIK = rig_transform(0, name=side+'_armIK', type='joint', target=arm,parent=armSkeletonParts).object
		elbowIK = rig_transform(0, name=side+'_elbowIK', type='joint', target=elbow).object
		handIK = rig_transform(0, name=side+'_handIK', type='joint', target=hand).object
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

		pm.connectAttr(module.top.ikFkSwitch, poleVector.offset+'.visibility' )

		self.armControls['poleVector'] = poleVector

		pm.delete(pm.aimConstraint(elbow, poleVector.offset, mo=False))

		elbowPos = pm.xform(elbow, translation=True, query=True, ws=True)
		poleVectorPos = pm.xform(poleVector.con, translation=True, query=True,
		                         ws=True)

		pvDistance = lengthVector(elbowPos, poleVectorPos)

		pm.xform(poleVector.offset, translation=[pvDistance, 0, 0], os=True,
		           r=True)

		pm.poleVectorConstraint(poleVector.con, ik.handle)  # create pv

		print 'ik handle '+ik.handle
		handControl = rig_control(side=side,name='hand', shape='box', modify=2,
		                          targetOffset=hand,
		                          parentOffset=module.controls, constrain= str(
				ik.handle), scale=ctrlSize)

		handControl.gimbal = createCtrlGimbal( handControl )
		handControl.pivot = createCtrlPivot( handControl )

		pm.connectAttr(module.top.ikFkSwitch, handControl.offset+'.visibility' )

		self.armControls['hand'] = handControl

		pm.orientConstraint(handControl.con, handIK, mo=True )



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
		for at in ['ry','rz']:
			elbowFk.ctrl.attr(at).setKeyable(False)
			elbowFk.ctrl.attr(at).setLocked(True)

		self.armControls['fk'] = fkCtrls


		self.connectIkFkSwitch(chains=[ chainResult, chainIK, chainFK ],
		                       module = module ,name=name  )

		# constrain result to skeleton
		for i in range(0, len(chain)):
			pm.parentConstraint( chainResult[i], chain [i], mo=True)



		return module

	def pelvis (self):
		return

	def leg (self, side):
		return
		



