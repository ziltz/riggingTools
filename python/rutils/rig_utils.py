__author__ = 'Jerry'

import glob, os, platform, math, importlib

import maya.cmds as cmds
import maya.mel as mm
import pymel.core as pm






def defaultReturn(defaultVar, userVar, param):
	if param.get(userVar) == None:
		return defaultVar
	else:
		return param.get(userVar)

def defaultAppendReturn(defaultVar, userVar, param):
	if param.get(userVar) == None:
		return defaultVar
	else:
		var = param.get(userVar)
		if type(var) == str:
			var = [var]
		list = defaultVar + var
		return list


def rig_geoUnderGroupHierarchy(group=None):
	if group is None:
		group = pm.ls(sl=True)[0]
	geos = pm.listRelatives(group, ad=True, typ="mesh", ni=True)
	parents = []
	for g in geos:
		parents.append(pm.listRelatives(g, p=True)[0])

	pm.select(parents)
	return parents

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


def connectAttrToVisObj(ctrl, attrName, obj, defaultValue=0):
	pm.addAttr(ctrl, longName=attrName, at='long', k=False, min=0, max=1, dv=defaultValue)
	#ctrl.attrName.set(cb=True)
	pm.setAttr(ctrl+'.'+attrName, cb=True)
	pm.connectAttr(ctrl+'.'+attrName, obj.visibility)

'''



'''
def importLatestAsset(assetType=None, projectRoot=None, type='model'):
	
	if projectRoot is None:
		pm.workspace(update=True)
		projectRoot = pm.workspace(q=True, rd=True) + 'scenes/release/'
		print ' project root ' + projectRoot + ' found'
	
	
	genericPath = projectRoot + type+'/'
	if assetType is None:
		fileList = []
		os.chdir(genericPath)
		for f in glob.glob("*.ma"):
			fileList.append(f)
		
		fileList.sort()
		latestFile = fileList[-1:][0]
		assetType = genericPath + latestFile
	else:
		assetType = genericPath + assetType + '.ma'
	
	print type+' file path = ' + assetType
	# import type file
	try:
		cmds.file(assetType, i=True, ignoreVersion=True,
		                     ra=False, mergeNamespacesOnClash=False,
		                     typ="mayaAscii", loadReferenceDepth='none')
	except RuntimeError:
		print assetType + ' file not found'












