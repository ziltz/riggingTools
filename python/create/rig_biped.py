


from make.rig_ik import rig_ik
from rutils.rig_chain import *
from make.rig_controls import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform


'''

testing

import rig_biped as rb
reload(rb)
biped = rb.rig_biped()
biped.arm('l')


'''
class rig_biped(object):
	
	def __init__(self, **kwds):

		self.globalCtrl = pm.PyNode('global_CTRL')

		self.clavicleName = 'clavicleJA_JNT'

		self.armName = 'armJA_JNT'
		self.elbowName = 'elbowJA_JNT'
		self.handName = 'handJA_JNT'

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

		self.hip()
		
					
		return
	

	
	def spine(self):
		return
		
	def neck(self):
		return
		
	def head(self):
		return

	def shoulder (self, side ):
		return

	def hip (self):
		return

	def arm (self, side):
		name = side+'_arm'

		module = rig_module(name)
		self.armModule = module
		
		arm = self.armName
		elbow = self.elbowName
		hand = self.handName

		arm = side + '_' + arm
		elbow = side + '_' + elbow
		hand = side + '_' + hand

		chain = [arm, elbow, hand]

		print 'arm '+arm
		print 'elbow '+elbow
		print 'hand '+hand

		# chain result
		armResult = rig_transform(0, name=side + '_armResult', type='joint', target=arm).object
		elbowResult = rig_transform(0, name=side + '_elbowResult', type='joint', target=elbow).object
		handResult = rig_transform(0, name=side + '_handResult', type='joint', target=hand).object
		chainResult = [armResult, elbowResult, handResult]

		chainParent(chainResult)
		chainResult.reverse()
		pm.parent(armResult, module.skeleton)

		# chain FK
		armFK = rig_transform(0, name=side+'_armFK', type='joint', target=arm).object
		elbowFK = rig_transform(0, name=side+'_elbowFK', type='joint', target=elbow).object
		handFK = rig_transform(0, name=side+'_handFK', type='joint', target=hand).object
		chainFK = [ armFK, elbowFK, handFK ]

		chainParent(chainFK)
		chainFK.reverse()
		pm.parent(armFK, module.skeleton)

		# chain IK
		armIK = rig_transform(0, name=side+'_armIK', type='joint', target=arm).object
		elbowIK = rig_transform(0, name=side+'_elbowIK', type='joint', target=elbow).object
		handIK = rig_transform(0, name=side+'_handIK', type='joint', target=hand).object
		chainIK = [ armIK, elbowIK, handIK ]

		chainParent(chainIK)
		chainIK.reverse()
		pm.parent(armIK, module.skeleton)

		# create ik
		ik = rig_ik(name, armIK, handIK, 'ikRPsolver')
		pm.parent(ik.handle, module.parts)

		poleVector = rig_control(side=side, name='armPV', shape='pointer',
		                         modify=1, lockHideAttrs=['rx','ry','rz'],
		                         targetOffset=[arm, hand],
		                         parentOffset=module.controls )

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
		                          parentOffset=module.controls, constrain=
			str(ik.handle))

		pm.orientConstraint(handControl.con, handIK, mo=True )

		# create fk
		print 'fk chain '+ str(chainFK)
		fkCtrls = fkControlChain(chainFK)
		for fk in fkCtrls:
			pm.parent(fk.offset, module.controls)

		# switch
		switchLoc = 'ikFkSwitch_LOC'
		if not pm.objExists(switchLoc):
			switchLoc = rig_transform(0, type='locator', name='ikFkSwitch',
			                    parent=module.parts).object
			pm.addAttr(switchLoc, longName=name, at='float', k=True, min=0,
			           max=1)
		else:
			pm.addAttr(switchLoc, longName=name, at='float', k=True, min=0,
			           max=1)

		# blend joints together
		for i in range(0, len(chainResult)):
			# bldColor for rotation
			bldColor = pm.shadingNode('blendColors', asUtility=True,
			                          name=name+str(i)+'_blendColor')

			"Select ik, fk then bind joints in this order"
			pm.connectAttr(chainIK[i] + '.rotate', bldColor + '.color1',
			                 f=True)  # connect ik jnt to color1
			pm.connectAttr(chainFK[i] + '.rotate', bldColor + '.color2',
			                 f=True)  # connect fk jnt to color2
			pm.connectAttr(bldColor + '.output', chainResult[i] + '.rotate',
			                 f=True)  # connect bldColor output to bind jnt

			pm.connectAttr( switchLoc+'.'+name, bldColor.blender )
			# IK = 0, FK = 10 on switch
			# IK bldColors = 1, FK bldColors = 0
			# driver name, driver attribute, driven name, driven attribute
			# driver first and second values, driven first and second values
			#createSDK(_ikfkName, _switchAttrNme, bldName, 'blender',
			 #         0, 10, 1, 0)


		return module

	def leg (self, side, leg, knee, foot):
		return
		



