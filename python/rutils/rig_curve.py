
import pymel.core as pm

from rutils.rig_sort import rig_sortListByVectorAxis




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