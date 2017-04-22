__author__ = 'Jerry'

import glob, os, platform, math, importlib

import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm



def rig_utilsOpenMayaPort():
	#mc.commandPort( name=":7002", close=True )
	mc.commandPort(name=":7002", sourceType="mel")




def rig_sourceMelFiles(dir='C:/dev/riggingTools/mel/', ext='*.mel'):
	print("Sourcing all mel files")
	if platform.system() == 'Darwin':
		dir = '/Users/Jerry/Documents/dev/riggingTools/mel/'
	os.chdir(dir)
	for file in glob.glob(ext):
		print("- "+file+" ....")
		mm.eval('source "'+dir+file+'";')
		
		
def rig_sourcePythonFiles(dir='C:/dev/riggingTools/python/', ext='*.py'):
	print("Sourcing all python files")
	if platform.system() == 'Darwin':
		dir = '/Users/Jerry/Documents/dev/riggingTools/python/'

	print 'Using directory = '+ dir
	for root, dirs, files in os.walk(dir):
		currentDir = root.replace(dir, '')
		if dirs is not 'other':
			for file in files:
				if file.endswith(".py"):
					path = 'python.' +currentDir + '.' + file[:-3]
					if not currentDir:
						path = file[:-3]
					if file[:-3] not in '__init__':
						mod = importlib.import_module(path, package='riggingTools')
						print path
						reload(mod)


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
				print 'Found skinCluster on '+ g
				pm.setAttr(g + '.inheritsTransform', 0)

		except pm.MayaNodeError:
			pass

	print 'Done turning off inherit transforms on skinned geos'


def lengthVector( posA, posB):
	dx = posA[0] - posB[0]
	dy = posA[1] - posB[1]
	dz = posA[2] - posB[2]
	return math.sqrt( dx*dx + dy*dy + dz*dz )


def connectAttrToVisObj(ctrl, attrName, obj, defaultValue=0):
	pm.addAttr(ctrl, longName=attrName, at='long', k=True, min=0, max=1, dv=defaultValue)
	#ctrl.attrName.set(cb=True)
	pm.connectAttr(ctrl+'.'+attrName, obj.visibility)

















