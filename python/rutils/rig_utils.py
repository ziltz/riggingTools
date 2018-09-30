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



def connectAttrToVisObj(ctrl, attrName, obj, defaultValue=0):
    pm.addAttr(ctrl, longName=attrName, at='long', k=False, min=0, max=1, dv=defaultValue)
    #ctrl.attrName.set(cb=True)
    pm.setAttr(ctrl+'.'+attrName, cb=True)
    pm.connectAttr(ctrl+'.'+attrName, obj+'.v')

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


def findClosestVertexToObj(mesh, obj):
    import maya.OpenMaya as OpenMaya
     
    geo = pm.PyNode(mesh)
    loc = pm.PyNode(obj)
    pos = loc.getRotatePivot(space='world')
     
    nodeDagPath = OpenMaya.MObject()
    try:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(geo.name())
        nodeDagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, nodeDagPath)
    except:
        raise RuntimeError('OpenMaya.MDagPath() failed on %s' % geo.name())
     
    mfnMesh = OpenMaya.MFnMesh(nodeDagPath)
     
    pointA = OpenMaya.MPoint(pos.x, pos.y, pos.z)
    pointB = OpenMaya.MPoint()
    space = OpenMaya.MSpace.kWorld
     
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()
     
    mfnMesh.getClosestPoint(pointA, pointB, space, idPointer)  
    idx = OpenMaya.MScriptUtil(idPointer).asInt()
     
    faceVerts = [geo.vtx[i] for i in geo.f[idx].getVertices()]
    closestVert = None
    minLength = None
    for v in faceVerts:
        thisLength = (pos - v.getPosition(space='world')).length()
        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v
    pm.select(closestVert)

    return closestVert

def constrainObjsToClosestVertex(mesh, selection):
    import maya.app.general.pointOnPolyConstraint

    objDict = {}
    for sel in selection:
        vert = findClosestVertexToObj(mesh, sel)
        cmds.select(sel, add=True)
        cmdString = "string $constraint[]=`pointOnPolyConstraint -weight 1`;"
        assembled = maya.app.general.pointOnPolyConstraint.assembleCmd()
        print str(cmdString)
        print str(assembled)
        con = mel.eval(cmdString)
        mel.eval(assembled)
        objDict[sel] = con

    return objDict



