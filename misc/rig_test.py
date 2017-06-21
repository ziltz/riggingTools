import pymel.core as pmc

# Cartoony eye rig idea by Marco Giordano
# Automated Script by Jerry Lee
# Link - www.vimeo.com/66583205
# Select Upper edge, lower edge eyelid and spherical eye. (MUST BE SPHERICAL)
# Maybe make this into gui in a bit.

"""
Steps
1. Convert edge selection to joints
2. Create joint from middle of Eye to Eyelid
3. Create locators at every eyelid joint and do aimConstraint with Locator above sphere
4.

"""

# Create eyeball locators
def eyeCenterLocator( _eyeMesh, _suffix ):
    _eyeMesh.getPivots(worldSpace=True)[0]
    eyeLoc = pmc.spaceLocator(n = '%s_eye_loc' % _suffix )
    eyeLoc.translate.set(_eyeMesh.getPivots(worldSpace=True)[0])
    return eyeLoc

def eyeAimLocator( _eyeLoc, _suffix ):
    eyeLocAim = pmc.duplicate( _eyeLoc, name='%s_eyeAim_loc' % _suffix )[0]
    eyeLocAim.translateBy((0,5,0), space='object')
    return eyeLocAim

def sortVectorsByLocalX( _list ):
    for i in range(0, len(_list) ):
        for j in range(0, len(_list)):
            if i == j:
                pass
            else:
                if _list[i].x < _list[j].x:
                    _list[i], _list[j] = _list[j], _list[i]
    return _list

# create joints on vertices
def createJointsOnVertices( _vlist, _suffix, _eyeLoc ):
    # create joints
    i=1
    eyeBaseJnt_list = [] # create list of eyelid base joints
    eyelidJnt_list = []
    for v in _vlist:
        pmc.select(cl=True)
        jnt1 = pmc.joint(n='%s_eyelidBase_%d_jnt' % (_suffix, i))
        eyeBaseJnt_list.append(jnt1)
        jnt1.translate.set( _eyeLoc.translate.get() )
        pmc.select(cl=True)
        jnt2 = pmc.joint(n='%s_eyelid_%d_jnt' % (_suffix, i), rad=0.3)
        eyelidJnt_list.append(jnt2)
        pmc.select(v)
        vert = pmc.selected()[0]
        jnt2.translate.set(vert.getPosition())
        pmc.select(cl=True)
        pmc.parent( jnt2, jnt1 )
        pmc.joint( jnt1, e=True, oj='xyz', sao='yup', ch=True, zso=True )
        pmc.joint( jnt2, e=True, oj='none', ch=True, zso=True )
        i+=1

    return eyeBaseJnt_list, eyelidJnt_list

def createJointLocatorsWithAim( _list, _eyeLocAim ):
    # create locators for every eyelid joint and aimconstraint it to base with world up being eyeLocAim
    locList = []
    for jnt in _list:
        loc = pmc.spaceLocator( n=jnt.replace('_jnt', '_loc') )
        pmc.setAttr( loc+'.localScaleX', .3 )
        pmc.setAttr( loc+'.localScaleY', .3 )
        pmc.setAttr( loc+'.localScaleZ', .3 )
        locList.append(loc)
        loc.translate.set( jnt.getTranslation(worldSpace=True) )
        pmc.aimConstraint( loc, jnt.getParent(), mo=True, w=1, aimVector=(1,0,0), upVector=(0,1,0),
                         worldUpType='object', worldUpObject=_eyeLocAim )
    return locList

def createCurveFromJointList( _list, _suffix ):
    posList = []
    # grab the world translation of eyelid child joints
    for jnt in _list:
        posList.append(jnt.getTranslation(worldSpace=True))

    # sort the vectors by x translation
    posList = sortVectorsByLocalX(posList)

    # make a knot list for curve creation
    knotList = []
    for i in range(0, len(posList)):
        knotList.append(i)

    # create the curve
    el_curve = pmc.curve( n='%s_eyelid_highDensity_curve'%_suffix ,d=1, p=posList, k=knotList )
    return el_curve

def connectLocToCurveU( _locList, _curve ):
    for loc in _locList:
        pos = loc.getTranslation(worldSpace=True)
        u = _curve.getParamAtPoint(pos)
        nme = loc.replace('_loc', '_poi')
        poi = pmc.createNode( 'pointOnCurveInfo', n=nme )
        pmc.connectAttr( _curve+'.worldSpace', poi + '.inputCurve', )
        pmc.setAttr( poi +'.parameter', u )
        pmc.connectAttr( poi+'.position', loc+'.t')

def eyeCartoonyRig( _eyeMesh, _edgeList, _suffix ):
    # create locator at eyeball center and locator above for aim constraint
    eyeLoc = eyeCenterLocator( _eyeMesh, _suffix )
    eyeLocAim = eyeAimLocator( eyeLoc, _suffix )
    # convert edge to vertices
    vertexSel = pmc.polyListComponentConversion( _edgeList, fe=True, toVertex=True )
    vertexSel = pmc.filterExpand(vertexSel, ex=True, sm=31) # get all vertices selection
    jnt_list = createJointsOnVertices( vertexSel, _suffix, eyeLoc ) # create joints on eyelid
    # separate lists into proper names
    eyeBaseJnt_list = jnt_list[0]
    eyelidJnt_list = jnt_list[1]

    eyeloc_list = createJointLocatorsWithAim( eyelidJnt_list, eyeLocAim ) # create locators on eyelid joints with aim constraint

    eyelidCurve = createCurveFromJointList( eyelidJnt_list, _suffix ) # create high density curve
    connectLocToCurveU( eyeloc_list, eyelidCurve ) # connect locators to high density curve

    lowDensityName = eyelidCurve.replace( 'high', 'low' ) # name for low density curve
    lowDensity_eyelidCurve = pmc.duplicate( eyelidCurve, name=lowDensityName )[0] # create low density curve

    #wire -gw false -en 1.000000 -ce 0.000000 -li 0.000000 -w r_upper_eyelid_lowDensity_curve -dds 0 10.000000 r_upper_eyelid_highDensity_curve;
    pmc.rebuildCurve( lowDensity_eyelidCurve, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0,
                        s=4, d=3, tol=0 )

    pmc.select(cl=True)

    wireCurveName = eyelidCurve.replace( 'highDensity', 'wire' )
    wireCurve = pmc.wire( eyelidCurve, gw=False, en=1, ce=0, li=0, w=lowDensity_eyelidCurve, dds=[(0),(10.0)], name=wireCurveName )
    curveBaseWire = pmc.listConnections(wireCurve[0]+'.baseWire', s=True)
    #print wireCurve[0].getParent()
    # group nodes appropriately
    pmc.select(cl=True)
    pmc.group( eyeloc_list, name=_suffix+'_eyelid_loc_grp' )
    pmc.group( eyeBaseJnt_list, name=_suffix+'_eyelid_jnt_grp' )
    extraGrp = pmc.group( eyeLoc, eyeLocAim, eyelidCurve, lowDensity_eyelidCurve, curveBaseWire, name=_suffix+'_eyelid_extras_grp' )
    pmc.setAttr( extraGrp+'.visibility', 0 )


eyeCartoonyRig( eyeMesh, edgeSel, 'r_jupper' )

upperEdgeSel = pmc.ls(sl=True)
lowerEdgeSel = pmc.ls(sl=True)

eyeMesh = pmc.ls(sl=True)[0]
edgeSel = pmc.ls(sl=True)



#######################################################
# tests below !


testList = pmc.ls(sl=True)

curveNme = pmc.ls(sl=True)[0]
pmc.getAttr( curveNme+'.cv[0]', ws=True )
dir(curveNme)
type(curveNme)
c = curveNme.getTranslation(worldSpace=True)

for i in range(0,7):
    if (i == 1) or (i == 5):
        pass
    else:
        pmc.select(cl=True)
        #pmc.select(curveNme+'.cv[0]')
        pmc.select('%s.cv[%d]' % (curveNme, i) )
        curveCV = pmc.selected()[0]
        cvPos = curveCV.getPosition(space='world')
        pmc.select(cl=True)
        jnt = pmc.joint( n='_control_%d_jnt' % i)
        jnt.translate.set( cvPos )
        print i


c = pmc.listConnections( testList[0]+'.baseWire', s=True )
pmc.select(c)

curveTest = testList[0]
posList = []
for p in testList:
    posList.append(p.getTranslation(worldSpace=True))

uList = []
for p in posList:
    uList.append(curveTest.getParamAtPoint( p ))

for loc in testList:
    pos = loc.getTranslation(worldSpace=True)
    u = curveTest.getParamAtPoint(pos)
    nme = loc.replace('_loc', '_poi')
    poi = pmc.createNode( 'pointOnCurveInfo', n=nme )
    pmc.connectAttr( curveTest+'.worldSpace', poi + '.inputCurve', )
    pmc.setAttr( poi +'.parameter', u )
    pmc.connectAttr( poi+'.position', loc+'.t')

posList = []
for jnt in testList:
    posList.append(jnt.getTranslation(worldSpace=True))

def testSwapList( _list, _localAxis ):
    for i in range(0, len(_list) ):
        for j in range(0, len(_list)):
            if i == j:
                pass
            else:
                if _list[i]._localAxis < _list[j]._localAxis:
                    _list[i], _list[j] = _list[j], _list[i]
def localAxis(x):
    print x

testSwapList(posList, posList.x)

knotList = []
for i in range(0, len(posList)):
    knotList.append(i)

pmc.curve( d=1, p=posList, k=knotList )

# To create a new context that will create curves of degree 5:
pmc.curveCVCtx( "curveCVContext", degree=15 )
# Result: u'curveCVContext' #
pmc.setToolTo("curveCVContext")

testList = pmc.ls(sl=True)
loc = testList[0]
jnt = testList[1]
pmc.aimConstraint( loc, jnt, mo=True, w=1, aimVector=(1,0,0), upVector=(0,1,0),
                     worldUpType='object', worldUpObject='eyeLocAim' )

myName = 'Jerry_loc'
myName.replace('_loc', '_yo')
print myName

vertexSel = pmc.polyListComponentConversion( edgeSelection, toVertex=True )
for v in vertexSel:
    pmc.select(v)
    vert = pmc.selected()[0]
    pmc.select(cl=True)
    jnt = pmc.joint()
    jnt.translate.set(vert.getPosition())
    pmc.select(cl=True)

help(vertexSel[0].getPosition)
vertexSel.vtx
pmc.select(vertexSel[0])
v = pmc.selected()[0]
v.getPosition()

t = pmc.MeshVertex(getPosition())

for v in vertexSel:
    pmc.select(cl=True)
    jnt = pmc.joint()
    jnt.translate.set(v.translate.get())
    pmc.select(cl=True)

jntSel = pmc.ls(sl=True)
dir(jntSel[0])

pmc.select(cl=True)
#pmc.select('head_jnt', r=True)
for jnt in jntSel:
    c = pmc.listRelatives(jnt, c=True, type='joint')[0]
    pmc.select( c, add=True)


for jnt in pmc.ls(sl=True):
    ctrlName = jnt.replace("_jnt", "_ctrl")
    ctrl = pmc.circle( nr=(1, 0, 0), r=1,  n=ctrlName)[0]
    group = pmc.group(ctrl, n=ctrl + "_sdk")
    offset = pmc.group(group, n=ctrl + "_offset")
    print type(offset)
    print dir(offset)
    pmc.delete(pmc.parentConstraint(jnt, offset, mo=False))