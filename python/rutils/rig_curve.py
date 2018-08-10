
import pymel.core as pm

from rutils.rig_sort import rig_sortListByVectorAxis
from other.webcolors import name_to_rgb
from rutils.rig_transform import rig_transform



def rig_curveFromJoints( _list, name = 'crvJoints', axis='x', degree=3 ):
    posList = []
    # grab the world translation of eyelid child joints
    for jnt in _list:
        posList.append(jnt.getTranslation(worldSpace=True))

    # sort the vectors by x translation
    posList = rig_sortListByVectorAxis(posList, axis)

    # make a knot list for curve creation
    knotList = []
    numKnots = (len(posList)+degree-1)
    numHalf = numKnots / 2
    if numKnots % 2 != 0:
        numHalf = (numKnots-1) / 2
    knotVector = 0
    for i in range(0, numKnots):
        if i == numHalf:
            knotVector = 1
        if i > numHalf:
            knotVector = 2
        knotList.append(knotVector)

    # create the curve
    curve = pm.curve( n=name+'_CRV' ,d=degree, p=posList, k=knotList )

    return curve

'''
_locList = pm.ls(sl=True)
_curve = crv


for loc in _locList:
    pos = loc.getTranslation(worldSpace=True)
    closestPoint = _curve.closestPoint(pos)
    u = _curve.getParamAtPoint( closestPoint )
    print u
    nme = loc.replace('_JNT', '_POI')
    poi = pm.createNode( 'pointOnCurveInfo', n=nme )
    pm.connectAttr( _curve+'.worldSpace', poi + '.inputCurve', )
    pm.setAttr( poi +'.parameter', u )
    pm.connectAttr( poi+'.position', loc+'.t')

crv = pm.PyNode('crvJoints_CRV1')

cvs =  crv.getCVs()

count = 0
for c in cvs:
    pm.select(cl=True)
    jnt = pm.joint(name='spine'+str(count)+'_JNT')
    jnt.setTranslation(c)
    count += 1
'''


'''
rig_curveBetweenTwoPoints(poleVector.con, elbow, name=name+'PV')
'''
def rig_curveBetweenTwoPoints(start,end, name='curveBetween' , degree=1, colour='white', parent='allModel_GRP'):

    startPos = pm.xform( start, translation=True, query=True, ws=True)
    endPos = pm.xform( end, translation=True, query=True, ws=True)

    pm.select(cl=True)
    startJnt = pm.joint(name=name+'Start_JNT')
    pm.pointConstraint( start, startJnt )
    pm.select(cl=True)
    endJnt = pm.joint(name=name+'End_JNT')
    pm.pointConstraint( end, endJnt )

    curve = pm.curve( n=name+'_CRV', d=degree, p=(startPos, endPos), k=(0,1) )

    sc = pm.skinCluster( (startJnt, endJnt),curve , tsb=True, dr=1)

    pm.skinPercent( sc, curve.cv[0],tv=(startJnt, 1)  )
    pm.skinPercent( sc, curve.cv[1],tv=(endJnt, 1)  )

    col = name_to_rgb(colour)
    curve.overrideColorRGB.set(col[0], col[1], col[2])

    topGrp = 'puppetLinearCurves_GRP'
    if not pm.objExists(topGrp):
        topGrp = rig_transform(0, name='puppetLinearCurves', type='group',
                                    parent=parent).object

    pm.parent(curve,startJnt,endJnt, topGrp)
    pm.setAttr(curve+".inheritsTransform", 0)
    pm.setAttr(curve+".template", 1)

    pm.hide( startJnt, endJnt )

    return curve
