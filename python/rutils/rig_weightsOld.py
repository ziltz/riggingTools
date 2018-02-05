import xml.etree.ElementTree
import time
import maya.cmds as cmds
import maya.mel as mel
import os

'''

taken from chrisevans3d
http://www.chrisevans3d.com/pub_blog/saveload-skinweights-125x-faster/

sw = rig_skinWeights()
sw.saveWeightInfo('e:\\gadget\\', cmds.ls(sl=1))
>>>Exported skinWeights for 214 meshes in 2.433 seconds.


'''

class rig_skinWeights(object):
	def __init__(self, path=None):
		self.path = path
		self.shapes = {}
		self.fileName = None

		if self.path:
			self.parseFile(self.path)

	class skinnedShape(object):
		def __init__(self, joints=None, shape=None, skin=None, verts=None):
			self.joints = joints
			self.shape = shape
			self.skin = skin
			self.verts = verts

	def applyWeightInfo(self):
		for shape in self.shapes:
			#make a skincluster using the joints
			if cmds.objExists(shape):
				sc = mel.eval('findRelatedSkinCluster ' + shape)
				if cmds.objExists(sc):
					cmds.delete(sc)

				ss = self.shapes[shape]
				skinList = ss.joints
				skinList.append(shape)
				cmds.select(cl=1)
				cmds.select(skinList)
				cluster = cmds.skinCluster(name=ss.skin, tsb=1)
				fname = self.path.split('\\')[-1]
				dir = self.path.replace(fname,'')
				cmds.deformerWeights(fname , path = dir, deformer=ss.skin, im=1)

	def saveWeightInfo(self, fpath, meshes, all=True):
		t1 = time.time()

		#get skin clusters
		meshDict = {}
		for mesh in meshes:
			sc = mel.eval('findRelatedSkinCluster '+mesh)
			#not using shape atm, mesh instead
			msh =  cmds.listRelatives(mesh, shapes=1)
			if sc != '':
				meshDict[sc] = mesh
			else:
				cmds.warning('>>>saveWeightInfo: ' + mesh + ' is not connected to a skinCluster!')

		#fname = fpath.split('//')[-1]
		#dir = fpath.replace(fname,'')
		print fpath

		for skin in meshDict:
			cmds.deformerWeights(meshDict[skin] + '.skinWeights', path=fpath, ex=1, deformer=skin)

		elapsed = time.time()-t1
		print 'Exported skinWeights for', len(meshes), 'meshes in', elapsed, 'seconds.'


	def parseFile(self, path):
		root = xml.etree.ElementTree.parse(path).getroot()

		#set the header info
		for atype in root.findall('headerInfo'):
			self.fileName = atype.get('fileName')

		for atype in root.findall('weights'):
			jnt = atype.get('source')
			shape = atype.get('shape')
			clusterName = atype.get('deformer')

			if shape not in self.shapes.keys():
				self.shapes[shape] = self.skinnedShape(shape=shape, skin=clusterName, joints=[jnt])
			else:
				s = self.shapes[shape]
				s.joints.append(jnt)


def loadWeightInfo(path):
	if path:
		t1 = time.time()
		files = 0
		for file in os.listdir(path):
			if file.endswith(".skinWeights"):
				fpath = path + file
				sdw = rig_skinWeights(path=fpath)
				sdw.applyWeightInfo()
				files += 1

		elapsed = time.time() - t1
		print 'Loaded skinWeights for', files, 'meshes in', elapsed, 'seconds.'