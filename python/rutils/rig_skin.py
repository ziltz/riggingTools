


import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm

import re

from rutils.rig_utils import *

'''

make skincluster local to global transform rig_GRP

 rig_skinLocalRig( ('body_GEO', 'midRes_body_GEO') )

'''

def rig_skinLocalRig(geos, top='rig_GRP'):

	for g in geos:
		print g
		skin = mm.eval(
			'findRelatedSkinCluster "'+g+'";')

		infs = pm.skinCluster(skin, q=True, inf=True)

		for jnt in infs:
			skinMat = ''
			try:
				skinMat = pm.listConnections(jnt.worldMatrix[0], p=True, d=True, scn=True,
				                             s=False)[0]
			except IndexError:
				print jnt+' not connected to '+skin

			print 'skinMat = '+skinMat

			multMatrix = pm.createNode('multMatrix')
			pm.connectAttr(jnt.worldMatrix, multMatrix.matrixIn[0], f=True)
			pm.connectAttr(top + '.worldInverseMatrix', multMatrix.matrixIn[1],f=True)

			indexSearch = re.search(r"\[([A-Za-z0-9_]+)\]", skinMat.stripNamespace())
			skinIndex = indexSearch.group(1)

			print 'Connecting '+jnt+ ' to '+skin+'.matrix['+skinIndex+']'
			pm.connectAttr(multMatrix.matrixSum, skin+'.matrix['+skinIndex+']', f=True)


# turn off inherit transforms on skincluster geometry under hierarchy
def rig_skinClusterTransforms(group=None):
	geos = rig_geoUnderGroupHierarchy(group)
	for g in geos:
		try:
			skinCluster = pm.PyNode(mm.eval('findRelatedSkinCluster "' + g + '";'))
			if skinCluster.exists:
				print 'Found skinCluster on '+ g
				pm.setAttr(g + '.inheritsTransform', 0)

		except pm.MayaNodeError:
			pass

	print 'Done turning off inherit transforms on skinned geos'



def rig_skinClusterFindMirrorMissing(sc=''):
	rList = []
	infs = cmds.skinCluster(sc, q=True, inf=True)

	for i in infs:
		if i.startswith('l_'):
			right = i.replace('l_', 'r_')
			skin = cmds.listConnections(right+'.worldMatrix[0]')
			try:
				if len(skin) > 0 and skin[0].startswith('skinCluster'):
					print 'left'
			except:
				print right
				rList.append(right)

	cmds.select(rList)

















