__author__ = 'Jerry'



from rutils.rig_object import rig_object
from rutils.rig_utils import *
from make.rig_controls import *
from rutils.rig_transform import rig_transform


import pymel.core as pm
import maya.cmds as cmds



'''

Create rig skeleton from root joint and given name

rigSkeleton = skeleton( 'test', 'mainJA_JNT' )

'''

class skeleton(rig_object):
	
	def __init__(self, character, root, **kwds):
		
		self.character = character
		self.root = root
		
		
		try:
			
			pm.select(cl=True)
			
			self.globalCtrl = rig_control(name='global', colour='white', shape='arrows',
			                              con=0, showAttrs=['sx', 'sy','sz'])
		
			self.topNode = rig_transform(0, name=self.character + 'RigSkeletonTop', child=self.globalCtrl.offset).object
			
			self.skeleton = rig_transform(0, name='skeleton', child=self.root, parent=self.globalCtrl.ctrl).object
			
			connectAttrToVisObj(self.globalCtrl.ctrl, 'skeletonVis', self.skeleton,
			                    defaultValue=1)
			
			pm.select(cl=True)
			
			self.sup = super(skeleton, self)
			self.sup.__init__(self.topNode, **kwds)
		
		except Exception as e:
			raise

		
		
		
'''

pose names
- tPose
- bindPose

savePose('spineJA_JNT', 'tPose')
savePose('spineJA_JNT', 'projPose')

loadPose('spineJA_JNT', 'tPose')
loadPose('spineJA_JNT', 'projPose')

removePose('spineJA_JNT', 'tPose')
removePose('spineJA_JNT', 'projPose')

'''

def savePose(root='spineJA_JNT', pose='tPose'):

	listJoints = listSkeletonHierarchy(root)

	for joint in listJoints:
		joint = pm.PyNode(joint)
		poseExist = pm.objExists(joint+'.'+pose)
		if poseExist:
			setCurrentPose(joint, pose)
		else:
			pm.addAttr(joint, longName=pose, attributeType='matrix')
			setCurrentPose(joint, pose)

	print 'Done saving '+pose+' on '+root

def setCurrentPose(joint='spineJA_JNT', pose='tPose'):
	joint = pm.PyNode(joint)
	poses = getCurrentPose(joint)

	poseAttr = getattr(joint, pose)
	matrix = poseAttr.get()

	matrix.a00 = poses['translate'][0]
	matrix.a01 = poses['translate'][1]
	matrix.a02 = poses['translate'][2]

	matrix.a10 = poses['rotate'][0]
	matrix.a11 = poses['rotate'][1]
	matrix.a12 = poses['rotate'][2]

	matrix.a20 = poses['scale'][0]
	matrix.a21 = poses['scale'][1]
	matrix.a22 = poses['scale'][2]

	matrix.a30 = poses['jointOrient'][0]
	matrix.a31 = poses['jointOrient'][1]
	matrix.a32 = poses['jointOrient'][2]

	poseAttr.set( matrix )


def getCurrentPose(joint):
	joint = pm.PyNode(joint)
	poseDict = {}

	translate = pm.getAttr(joint.translate)
	rotate = pm.getAttr(joint.rotate)
	scale = pm.getAttr(joint.scale)
	jointOrient = pm.getAttr(joint.jointOrient)

	poseDict['translate'] = translate
	poseDict['rotate'] = rotate
	poseDict['scale'] = scale
	poseDict['jointOrient'] = jointOrient

	return poseDict



def loadPose(root='spineJA_JNT', pose='tPose'):

	listJoints = listSkeletonHierarchy(root)

	for joint in listJoints:
		jnt = pm.PyNode(joint)
		poseExist = pm.objExists(joint + '.' + pose)
		if poseExist:
			poseAttr = getattr(jnt, pose)
			matrix = poseAttr.get()

			pm.setAttr( jnt.translateX, matrix.a00)
			pm.setAttr( jnt.translateY, matrix.a01)
			pm.setAttr( jnt.translateZ, matrix.a02)

			pm.setAttr(jnt.rotateX, matrix.a10)
			pm.setAttr(jnt.rotateY, matrix.a11)
			pm.setAttr(jnt.rotateZ, matrix.a12)

			pm.setAttr(jnt.scaleX, matrix.a20)
			pm.setAttr(jnt.scaleY, matrix.a21)
			pm.setAttr(jnt.scaleZ, matrix.a22)

			pm.setAttr(jnt.jointOrientX, matrix.a30)
			pm.setAttr(jnt.jointOrientY, matrix.a31)
			pm.setAttr(jnt.jointOrientZ, matrix.a32)

	print 'Done loading ' + pose + ' on ' + root


def removePose(root='spineJA_JNT', pose='tPose'):
	listJoints = listSkeletonHierarchy(root)
	for joint in listJoints:
		pm.deleteAttr(joint, at=pose)


def listSkeletonHierarchy(root):

	listJoints = cmds.listRelatives(root, type="joint", ad=True)

	skeleton = []
	if listJoints:
		listJoints.insert(0, root)

		for jnt in listJoints:
			if 'JEnd_JNT' not in jnt:
				skeleton.append(jnt)
	else:
		skeleton.append(root)

	return skeleton











