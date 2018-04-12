__author__ = 'Jerry'

import maya.cmds as cmds
import pymel.core as pm

from rutils.rig_name import *
from rutils.rig_chain import *
from rutils.rig_transform import *

#mc.makeIdentity( 'r_clavicleJA_JNT', a=1, r=1 )

'''
0 - center
1 - left
2 - right
3 - none

'''
def rig_jointAssignLabel(list=[]):
	for jnt in list:
		side = rig_nameGetSide(jnt)
		if side == 'l':
			cmds.setAttr(jnt+'.side', 1)
			cmds.setAttr(jnt+'.otherType', jnt.replace(side+'_','label_'), type='string' )

		elif side == 'r':
			cmds.setAttr(jnt+'.side', 2)
			cmds.setAttr(jnt+'.otherType', jnt.replace(side+'_','label_'), type='string' )
		elif side == '':
			cmds.setAttr(jnt+'.side', 0)
			cmds.setAttr(jnt+'.otherType', 'label_'+jnt, type='string' )



'''
make duplicate joint chain and rename
find replace name

'''
def rig_jointCopyChain(rootJoint, replaceName=('','') ):
	jointChain = rig_chain( rootJoint ).chain

	#print 'rootJoint = '+rootJoint
	parent = pm.listRelatives(rootJoint, p=True)
	#print 'parent = '+parent
	if len(parent) == 0:
		parent = ''
		print 'No parent found'
	else:
		parent = parent[0]
	i=0
	firstJoint = ''
	for joint in jointChain:
		newJnt = rig_transform(0, name=joint.replace(replaceName[0], replaceName[1]), type='joint',
			                          target=joint, parent=parent).object
		parent = newJnt
		if i == 0:
			firstJoint = newJnt
		i += 1


	return rig_chain( firstJoint ).chain

