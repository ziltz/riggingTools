

__author__ = 'Jerry'


import pymel.core as pm
import maya.cmds as mc


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

