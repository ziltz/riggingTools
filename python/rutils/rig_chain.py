

__author__ = 'Jerry'


import pymel.core as pm
import maya.cmds as mc
import string

from rig_object import rig_object

class rig_chain(object):

	def __init__(self, root):

		self.root = pm.PyNode(root)

		rootJoint = self.root
		chainList = [ rootJoint ]
		self.chainChildren = []
		children = 1
		while children == 1:
			joints = pm.listRelatives( rootJoint , c=True, type='joint')
			if len(joints) > 0:
				chainList.append(joints[0])
				rootJoint = joints[0]
				self.chainChildren.append(joints[0])
			elif len(joints) == 0:
				children = 0

		self.chain = chainList

		# super(rig_chain, self).__init__(self.root, **kwds)

def chainParent( list, reverse=0 ):
	chain = list
	if reverse == 0:
		chain.reverse()
	for i in range(0, len(chain)-1 ):
		try:
			mc.parent( chain[i], chain[i+1] )
		except TypeError:
			pm.parent( chain[i], chain[i+1] )



def rig_chainJointName(selection, name):
	ABC = list(string.ascii_uppercase)

	i = 0
	prefixABC = ''
	abcInd = 0
	for jnt in selection:
		if i < 26:
			pm.rename(jnt, name +'J'+ prefixABC+ABC[i] + '_JNT')
		else:
			i = 0
			prefixABC = ABC[abcInd]
			abcInd +=1
			pm.rename(jnt, name + 'J' + prefixABC + ABC[i] + '_JNT')

		i+=1

def rig_chainStraightedJointOrient(selection, axis='X'):

	for jnt in selection:
		pm.setAttr ( jnt+'.jointOrient'+axis, 0 )


