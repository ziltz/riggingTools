

__author__ = 'Jerry'


import pymel.core as pm
import maya.cmds as mc


from rig_object import rig_object

class rig_chain(rig_object):

	def __init__(self, root, **kwds):

		self.root = root

		super(rig_chain, self).__init__(root, **kwds)

		rootJoint = self.root
		chainList = [ rootJoint ]
		children = 1
		while children == 1:
			joints = pm.listRelatives( rootJoint , c=True, type='joint')
			if len(joints) > 0:
				chainList.append(joints[0])
				rootJoint = joints[0]
			elif len(joints) == 0:
				children = 0

		self.chain = chainList


def chainParent( list, reverse=0 ):
	chain = list
	if reverse == 0:
		chain.reverse()
	for i in range(0, len(chain)-1 ):
		print (chain[i])
		print (chain[i+1])
		try:
			mc.parent( chain[i], chain[i+1] )
		except TypeError:
			pm.parent( chain[i], chain[i+1] )

