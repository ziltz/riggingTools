
__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from make.rig_controls import *
from make.rig_ik import *

from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform

'''

rig_tail( 'tail', 'tailHiJA_JNT', 'pelvisJA_JNT', 'spineFullBodyCon_GRP', 1, 12, 12 )

'''
class rig_tail( object ):

	def __init__(self, name = 'tail' , 
						rootJoint = 'tailHiJA_JNT', 
						parent ='pelvisJA_JNT' ,
						parentName = 'pelvis',
						spine ='spineFullBodyCon_GRP',
						ctrlSize = 1,
						numIKCtrls = 12,
						numFKCtrls = 12 ):

		self.name = name
		self.rootJoint = rootJoint
		self.parent = parent
		self.parentName = parentName
		self.spine = spine
		self.ctrlSize = ctrlSize
		self.numIKCtrls = numIKCtrls
		self.numFKCtrls = numFKCtrls
		self.worldSpace = 'worldSpace_GRP'
		self.dWorldUpAxis = 8 # closest x
		self.splinePosList = []
		self.module = ''


	# make tail
	'''
	tailModule = rig_ikChainSpline('tail', 'tailJA_JNT', ctrlSize=1, parent='pelvisJA_JNT',
	                               numIkControls=4, numFkControls=4)

	chainList = rig_chain('tailJOTip_JNT').chain
	print '====== MAKING TAIL TIP =============='
	fkCtrls = fkControlChain(chainList, modify=1, scale=[1, 1, 1], directCon=1)
	for fk in fkCtrls:
		pm.parent(fk.offset, tailModule.controls)


	string $ctrls[];
	string $reads[];
	string $spline = rig_makeSpline("tail", 4, "cube", 8, 12, "joint", $ctrls, $reads, 0) ;

	makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};


	'''

	def make(self):


		listJoints = cmds.listRelatives(self.rootJoint, type="joint", ad=True)
		listJoints.append(self.rootJoint)
		listJoints.reverse()


		'''
		rig_makeSpline(string $baseName, int $nControls, string $controlType, int $detail,
						int $nRead, string $readType, string $ctrls[], string $reads[], int $bConstrainMid
			)
		'''
		# make cMus tail joints
		mm.eval(
			'string $ctrls[];string $reads[];rig_makeSpline( "'+self.name+'", 4, "cube", 8, '+str(self.numIKCtrls)+', "joint", $ctrls, $reads, 0);')

		# place them every thirds
		if len(self.splinePosList) == 0:
			thirds = len(listJoints)/3
			pm.delete(pm.parentConstraint( self.rootJoint, self.name+'BaseIKOffset_GRP' ))
			pm.delete(pm.parentConstraint( listJoints[thirds], self.name+'MidAIKOffset_GRP' ))
			pm.delete(pm.parentConstraint( listJoints[thirds+thirds], self.name+'MidBIKOffset_GRP' ))
			pm.delete(pm.parentConstraint( listJoints[len(listJoints)-2], self.name+'TipIKOffset_GRP' ))
		elif len(self.splinePosList) > 0:
			pm.delete(pm.parentConstraint( self.splinePosList[0], self.name+'BaseIKOffset_GRP' ))
			pm.delete(pm.parentConstraint( self.splinePosList[1], self.name+'MidAIKOffset_GRP' ))
			pm.delete(pm.parentConstraint( self.splinePosList[2], self.name+'MidBIKOffset_GRP' ))
			pm.delete(pm.parentConstraint( self.splinePosList[3], self.name+'TipIKOffset_GRP' ))

		tailModule = rig_ikChainSpline( self.name , self.rootJoint, ctrlSize=self.ctrlSize, parent=self.parent,
		                               numIkControls=self.numIKCtrls, numFkControls=self.numFKCtrls, dWorldUpAxis= self.dWorldUpAxis)


		# tail upgrade
		tailJnts = pm.listRelatives( self.name+'SplineJoints_GRP', type='joint')
		for i in range (1, len(tailJnts)):
			tailNme = tailJnts[i].stripNamespace()
			tailIK = tailJnts[i]
			tailFK = tailNme.replace('IK', 'FK')
			tailFK = tailFK.replace('_JNT', '')

			constrainObject(tailFK+'Modify2_GRP',
			                [tailFK+'Modify1_GRP',tailIK ],
			                tailFK+'_CTRL', ['parent','IK'], type='parentConstraint')

		pm.parentConstraint( self.name+'FKACon_GRP', self.name+'BaseIKOffset_GRP', mo=True )

		constrainObject(  self.name+'MidAIKOffset_GRP',
		                [self.name+'FKACon_GRP',self.parent, self.worldSpace],
		                 self.name+'MidAIK_CTRL', ['base', self.parentName, 'world'],
		                 type='parentConstraint')

		constrainObject(self.name+'MidBIKOffset_GRP',
		                [self.name+'FKACon_GRP', self.name+'MidAIKCon_GRP' , self.parent, self.worldSpace],
		                self.name+'MidBIK_CTRL', ['base','FK', self.parentName, 'world'],
		                type='parentConstraint')

		constrainObject(self.name+'TipIKOffset_GRP',
		                [self.name+'FKACon_GRP', self.name+'MidBIKCon_GRP', self.parent, self.worldSpace],
		                self.name+'TipIK_CTRL', ['base', 'FK', self.parentName, 'world'],
		                type='parentConstraint')

		ctrlSizeHalf = [self.ctrlSize / 2.0, self.ctrlSize / 2.0, self.ctrlSize / 2.0]
		ctrlSizeQuarter = [self.ctrlSize / 4.0, self.ctrlSize / 4.0, self.ctrlSize / 4.0]
		self.ctrlSize = [self.ctrlSize, self.ctrlSize, self.ctrlSize]

	    # scale ctrls
		for ctrl in (self.name+'MidAIK_CTRL', self.name+'MidBIK_CTRL', self.name+'TipIK_CTRL'):
			c = pm.PyNode( ctrl )
			pm.scale(c.cv, self.ctrlSize[0], self.ctrlSize[0], self.ctrlSize[0] )
			pm.move(c.cv, [0, 2*self.ctrlSize[0], 0], relative=True, worldSpace=True)

		tailPointer = rig_control(name=self.name+'Pointer', shape='pyramid', lockHideAttrs=['rx', 'ry', 'rz'],
		                            colour='white', parentOffset=tailModule.controls, rotateOrder=2, scale=self.ctrlSize)
		pm.delete(pm.parentConstraint( listJoints[len(listJoints)-2], tailPointer.offset ))
		constrainObject(tailPointer.offset,
		                [self.parent, self.spine, self.worldSpace],
		                tailPointer.ctrl, [self.parentName, 'fullBody', 'world'], type='parentConstraint')

		tailPointerBase = rig_transform(0, name=self.name+'PointerBase', type='locator',
		                        parent=tailModule.parts, target=self.name+'FKA_CTRL').object
		tailPointerTip = rig_transform(0, name=self.name+'PointerTip', type='locator',
		                        parent=tailModule.parts, target=tailPointer.con).object

		pm.rotate(tailPointerBase, 0, 0, -90, r=True, os=True)
		pm.rotate(tailPointerTip, 0, 0, -90, r=True, os=True)

		pm.parentConstraint(self.parent, tailPointerBase, mo=True)
		pm.parentConstraint(tailPointer.con, tailPointerTip, mo=True)

		tailPointerTop = mm.eval(
			'rig_makePiston("' + tailPointerBase + '", "' + tailPointerTip + '", "'+self.name+'PointerAim");')

		pm.orientConstraint( tailPointerBase.replace('LOC','JNT'), self.name+'FKAModify2_GRP', mo=True )

		pm.parent(self.name+'MidAIKOffset_GRP', self.name+'MidBIKOffset_GRP',self.name+'TipIKOffset_GRP',
		          tailModule.controls)
		pm.parent(tailJnts, tailModule.skeleton)
		pm.parent(self.name+'_cMUS',self.name+'BaseIKOffset_GRP',tailPointerTop, tailModule.parts)
		pm.parent(self.name+'SplineSetup_GRP',self.name+'BaseIKOffset_GRP',tailPointerTop, tailModule.parts)

		pm.setAttr( tailModule.skeleton+'.inheritsTransform', 0 )


		self.module = tailModule
