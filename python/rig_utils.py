__author__ = 'Jerry'

import glob, os, platform

import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm


def rig_utilsOpenMayaPort():
	#mc.commandPort( name=":7002", close=True )
	mc.commandPort(name=":7002", sourceType="mel")




def rig_sourceMelFiles(dir='C:/dev/riggingTools/mel/', ext='*.mel'):
	if platform.system() == 'Darwin':
		dir = '/Users/Jerry/Documents/dev/riggingTools/mel/'
	os.chdir(dir)
	for file in glob.glob(ext):
		print("Sourcing "+file+" ....")
		mm.eval('source "'+dir+file+'";')


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


def rig_geometryGroupHierarchy(group=None):
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
	geos = rig_geometryGroupHierarchy(group)
	for g in geos:
		try:
			skinCluster = pm.PyNode(mm.eval('findRelatedSkinCluster "' + g + '";'))
			if skinCluster.exists:
				pm.setAttr(g + '.inheritsTransform', 0)

		except pm.MayaNodeError:
			print 'No skinCluster on '+ g