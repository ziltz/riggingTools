__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from make.rig_controls import *
from make.rig_ik import *

from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform
from rutils.rig_chain import *
from rutils.rig_joint import *

'''

numJoints = 39
uv = 1.0/numJoints

for i in range(0,40):
    fol = pm.createNode('transform', n='follicle'+str(i), ss=True)
    folShape = pm.createNode('follicle', n=fol.name()+'Shape', p=fol, ss=True)
    pm.select(cl=True)
    joint = pm.joint(radius=10)
    pm.parent(joint, fol)
    geo = pm.PyNode('nurbsPlane1')
    geo.local >> folShape.inputSurface
    geo.worldMatrix[0] >> folShape.inputWorldMatrix
    folShape.outRotate >> fol.rotate
    folShape.outTranslate >> fol.translate
    fol.inheritsTransform.set(False)
    folShape.parameterU.set(0.5)
    folShape.parameterV.set(uv*i)

expression
tailFKBModify1_GRP.rotateZ = (sin((time*4)+8)*4);
tailFKCModify1_GRP.rotateZ = (sin((time*4)+7)*6);
tailFKDModify1_GRP.rotateZ = (sin((time*4)+6)*8);
tailFKEModify1_GRP.rotateZ = (sin((time*4)+5)*10);
tailFKFModify1_GRP.rotateZ = (sin((time*4)+4)*12);
tailFKGModify1_GRP.rotateZ = (sin((time*4)+3)*14);

tailFKBModify1_GRP.rotateZ = (sin((time*tailDyn_LOC.frequency)+tailDyn_LOC.tailAmp1)*tailDyn_LOC.tailOffset1);
tailFKCModify1_GRP.rotateZ = (sin((time*tailDyn_LOC.frequency)+tailDyn_LOC.tailAmp2)*tailDyn_LOC.tailOffset2);
tailFKDModify1_GRP.rotateZ = (sin((time*tailDyn_LOC.frequency)+tailDyn_LOC.tailAmp3)*tailDyn_LOC.tailOffset3);
tailFKEModify1_GRP.rotateZ = (sin((time*tailDyn_LOC.frequency)+tailDyn_LOC.tailAmp4)*tailDyn_LOC.tailOffset4);
tailFKFModify1_GRP.rotateZ = (sin((time*tailDyn_LOC.frequency)+tailDyn_LOC.tailAmp5)*tailDyn_LOC.tailOffset5);
tailFKGModify1_GRP.rotateZ = (sin((time*tailDyn_LOC.frequency)+tailDyn_LOC.tailAmp6)*tailDyn_LOC.tailOffset6);

swap offset and amp

select "tailSplineIK_CRV";
makeCurvesDynamic 2 { "1", "0", "1", "1", "0"}

# make copy of 8 joints (controls)

ikData = pm.ikHandle(n='dynTail_ikHandle', sj='joint1', ee='joint8',
                                 solver='ikSplineSolver',curve='curve1',ccv=False, ns=8)

hairSystem = pm.ls("|hairSystem?")[0]
nucleus = pm.ls("|nucleus?")[0]
dynCurveGrp = pm.ls("|hairSystem?OutputCurves")[0]
dynCurve = pm.listRelatives(dynCurveGrp, c=True)[0]


setAttr "hairSystemShape1.collide" 0;
setAttr "hairSystemShape1.stretchResistance" 25;
setAttr "hairSystemShape1.bendResistance" .1;
setAttr "hairSystemShape1.stiffness" 1;
setAttr "hairSystemShape1.lengthFlex" 1;
setAttr "hairSystemShape1.damp" .05;
setAttr "hairSystemShape1.stretchDamp" 1;
setAttr "hairSystemShape1.mass" .2;
setAttr "hairSystemShape1.attractionDamp" 1;
setAttr "hairSystemShape1.startCurveAttract" .5;

setAttr "follicleShape1.pointLock" 1;
setAttr "follicleShape1.overrideDynamics" 1;
setAttr "follicleShape1.collide" 0;
setAttr "follicleShape1.damp" .25;
setAttr "follicleShape1.stiffness" 0;
setAttr "follicleShape1.startCurveAttract" .3;

dynTail_ikHandle advanced twist controls same as tail_ikHandle

nucleus.gravity.set(0)


sc = rcon.simpleControls(cmds.ls(sl=True), modify=1, constrainJoints=0, parentCon=1, colour='red' )


// exp
$attrStart = tailFKA_CTRL.startFrame;
$refLocX = tailFKBLagRef_LOC.translateX;
$refLocY = tailFKBLagRef_LOC.translateY;
$refLocZ = tailFKBLagRef_LOC.translateZ;
$lagLocX = tailFKBLag_LOC.translateX;
$lagLocY = tailFKBLag_LOC.translateY;
$lagLocZ = tailFKBLag_LOC.translateZ;
vector $refLoc = <<tailFKBLagRef_LOC.translateX,tailFKBLagRef_LOC.translateY,tailFKBLagRef_LOC.translateZ>>;
vector $ball = <<tailFKBLag_LOC.translateX,tailFKBLag_LOC.translateY,tailFKBLag_LOC.translateZ>>;
$stiffness = 0.9;
$friction = 1.0;
vector $velocity;
vector $oldVelocity;
$distanceVector = ($refLoc - $ball)/1.5;
$force = $distanceVector * $stiffness;
$oldVelocity = $oldVelocity +(($ball+$force)-$ball);

tailFKBLag_LOC.translateX=(tailFKBLag_LOC.translateX+$oldVelocity.x)*$friction;
tailFKBLag_LOC.translateY=(tailFKBLag_LOC.translateY+$oldVelocity.y)*$friction;
tailFKBLag_LOC.translateZ=(tailFKBLag_LOC.translateZ+$oldVelocity.z)*$friction;

if(frame == $attrStart){
$velocity = <<0,0,0>>;
}

if(frame == $attrStart){
tailFKBLag_LOC.translateX = 0;
tailFKBLag_LOC.translateY= 0;
tailFKBLag_LOC.translateZ = 0;
}


rig_tail( 'tail', 'tailHiJA_JNT', 'pelvisJA_JNT', 'spineFullBodyCon_GRP', 1, 12, 12 )


'''

class rig_tail( object ):

    def __init__(self, name = 'tail' , 
                        rootJoint = 'tailHiJA_JNT', 
                        parent ='pelvisJA_JNT' ,
                        parentName = 'pelvis',
                        spine ='spineFullBodyCon_GRP',
                        ctrlSize = 1,
                        numIKCtrls = 12,
                        numFKCtrls = 12,
                        makeLag = 1, 
                        makeDynamic = 0 ):

        self.name = name
        self.rootJoint = rootJoint
        self.parent = parent
        self.parentName = parentName
        self.spine = spine
        self.ctrlSize = ctrlSize
        self.numIKCtrls = numIKCtrls
        self.numFKCtrls = numFKCtrls
        self.worldSpace = 'worldSpace_GRP'
        self.dWorldUpAxis = 8 # closest x
        self.splinePosList = []
        self.module = ''
        self.makeLag = makeLag # adds a lag expression on the fk control layer
        self.makeDynamic = makeDynamic # adds a post dynamic control layer ( red controls )
    # make tail
    '''
    tailModule = rig_ikChainSpline('tail', 'tailJA_JNT', ctrlSize=1, parent='pelvisJA_JNT',
                                   numIkControls=4, numFkControls=4)

    chainList = rig_chain('tailJOTip_JNT').chain
    print '====== MAKING TAIL TIP =============='
    fkCtrls = fkControlChain(chainList, modify=1, scale=[1, 1, 1], directCon=1)
    for fk in fkCtrls:
        pm.parent(fk.offset, tailModule.controls)


    string $ctrls[];
    string $reads[];
    string $spline = rig_makeSpline("tail", 4, "cube", 8, 12, "joint", $ctrls, $reads, 0) ;


    '''

    def make(self):


        listOrigJoints = mc.listRelatives(self.rootJoint, type="joint", ad=True)
        listOrigJoints.append(self.rootJoint)
        listOrigJoints.reverse()

        listJoints = []
        if self.makeDynamic:
            listJoints = rig_jointCopyChain(self.rootJoint, replaceName=(self.name,self.name+'ChainSpline') )
            self.origRootJoint = str(self.rootJoint)
            self.rootJoint = listJoints[0]
        else:
            listJoints = listOrigJoints

        '''
        rig_makeSpline(string $baseName, int $nControls, string $controlType, int $detail,
                        int $nRead, string $readType, string $ctrls[], string $reads[], int $bConstrainMid
            )
        '''
        # make cMus tail joints
        mm.eval(
            'string $ctrls[];string $reads[];rig_makeSpline( "'+self.name+'", 4, "cube", 8, '+str(self.numIKCtrls)+', "joint", $ctrls, $reads, 0);')

        # place them every thirds
        if len(self.splinePosList) == 0:
            thirds = len(listJoints)/3
            pm.delete(pm.parentConstraint( self.rootJoint, self.name+'BaseIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( listJoints[thirds], self.name+'MidAIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( listJoints[thirds+thirds], self.name+'MidBIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( listJoints[len(listJoints)-2], self.name+'TipIKOffset_GRP' ))
        elif len(self.splinePosList) > 0:
            pm.delete(pm.parentConstraint( self.splinePosList[0], self.name+'BaseIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( self.splinePosList[1], self.name+'MidAIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( self.splinePosList[2], self.name+'MidBIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( self.splinePosList[3], self.name+'TipIKOffset_GRP' ))

        tailModule = rig_ikChainSpline( self.name , self.rootJoint, ctrlSize=self.ctrlSize, parent=self.parent,
                                       numIkControls=self.numIKCtrls, numFkControls=self.numFKCtrls, dWorldUpAxis= self.dWorldUpAxis)


        fkBaseCtrl = pm.PyNode(self.name+'FKA_CTRL')
        fkBaseName = self.name+'FKA_CTRL'
        if self.makeLag:
            pm.addAttr( fkBaseCtrl, longName='startFrame',attributeType="long",
                                 defaultValue=1, keyable=True )
            pm.addAttr(fkBaseCtrl, ln='lagExpr', at='enum',
                       enumName='___________',
                       k=True)
            fkBaseCtrl.lagExpr.setLocked(True)
            pm.addAttr( fkBaseCtrl, longName='lagBlend',attributeType="double",
                                min=0, max=10, defaultValue=10, keyable=True )
            pm.addAttr( fkBaseCtrl, longName='lagStiffness',attributeType="double",
                                min=0, max=10, defaultValue=0, keyable=True )
            pm.addAttr( fkBaseCtrl, longName='lagStiffnessBlend',attributeType="double",
                                min=0, max=1, defaultValue=0, keyable=False )
            rig_animDrivenKey(fkBaseCtrl.lagStiffness, (0, 10),
                                              fkBaseCtrl.lagStiffnessBlend, (0, 1 ))
            pm.addAttr( fkBaseCtrl, longName='upDownMult',attributeType="long",
                                min=0, max=1, defaultValue=1, keyable=True )
            pm.addAttr( fkBaseCtrl, longName='leftRightMult',attributeType="long",
                                min=0, max=1, defaultValue=1, keyable=True )

        # tail upgrade
        prevCtrl = fkBaseName
        tailLagGrp = rig_transform(0, name=self.name+'Lag',
                                    parent=tailModule.parts).object

        tailJnts = pm.listRelatives( self.name+'SplineJoints_GRP', type='joint')

        dynJnts = []
        if self.makeDynamic:
            for i in range (0, len(tailJnts)):
                tailNme = tailJnts[i].stripNamespace()
                tailDyn = tailNme.replace('IK', 'Dyn')
                tailDyn = tailDyn.replace('_JNT', '')
                tailDyn = rig_transform(0, name=tailDyn, type='joint',target=tailJnts[i] ).object
                dynJnts.append(tailDyn)
                pm.addAttr(fkBaseCtrl, ln='Dynamics', at='enum',
                       enumName='___________',
                       k=True)
                pm.addAttr( fkBaseCtrl, longName='dynamicBlend',attributeType="double",
                                min=0, max=10, defaultValue=0, keyable=True )
                pm.addAttr( fkBaseCtrl, longName='stiffness',attributeType="double",
                                min=0, max=10, defaultValue=5, keyable=True )

        for i in range (1, len(tailJnts)):
            tailNme = tailJnts[i].stripNamespace()
            tailIK = tailJnts[i]
            tailFK = tailNme.replace('IK', 'FK')
            tailFK = tailFK.replace('_JNT', '')
            

            constrainObject(tailFK+'Modify2_GRP',
                            [tailFK+'Modify1_GRP',tailIK ],
                            tailFK+'_CTRL', ['parent','IK'], type='parentConstraint')

            # make lag reference locators
            if self.makeLag:
                lagOffset = rig_transform(0, name=tailFK+'LagOffset',
                                    parent=tailLagGrp, target=tailFK+'_CTRL').object
                lagExpLoc = rig_transform(0, name=tailFK+'Lag', type='locator',
                                    parent=lagOffset, target=tailFK+'_CTRL').object
                lagExpRefLoc = rig_transform(0, name=tailFK+'LagRef', type='locator',
                                    parent=lagOffset, target=tailFK+'_CTRL').object
                lagExpDriveLoc = rig_transform(0, name=tailFK+'LagDrive', type='locator',
                                    parent=lagExpRefLoc, target=tailFK+'_CTRL').object

                pm.parentConstraint(self.spine, lagOffset, mo=True)
                pm.parentConstraint( prevCtrl,  lagExpRefLoc, mo=True)
                con = pm.parentConstraint(lagExpRefLoc,lagExpLoc, lagExpDriveLoc, mo=True, sr=('x','y','z'))
                targets = con.getWeightAliasList()
                rig_animDrivenKey(fkBaseCtrl.lagBlend, (0, 10),
                                          targets[0], (1, 0 ))
                rig_animDrivenKey(fkBaseCtrl.lagBlend, (0, 10),
                                          targets[1], (0, 1 ))

                mm.eval('expression -o ("'+lagExpLoc+'") -n ("'+tailFK+'Lag_EXP") -s ("$attrStart = '+fkBaseName+'.startFrame;vector $refLoc = <<'+lagExpRefLoc+'.translateX,'+lagExpRefLoc+'.translateY,'+lagExpRefLoc+'.translateZ>>;vector $ball = <<'+lagExpLoc+'.translateX,'+lagExpLoc+'.translateY,'+lagExpLoc+'.translateZ>>;$stiffness = 0.9+(0.1*'+fkBaseName+'.lagStiffnessBlend);$friction = 1.0;vector $velocity;vector $oldVelocity;$distanceVector = ($refLoc - $ball)/2.0;$force = $distanceVector * $stiffness;$oldVelocity = $oldVelocity +(($ball+$force)-$ball);'+lagExpLoc+'.translateX=(('+lagExpLoc+'.translateX+$oldVelocity.x)*$friction)*'+fkBaseName+'.leftRightMult;'+lagExpLoc+'.translateY=(('+lagExpLoc+'.translateY+$oldVelocity.y)*$friction)*'+fkBaseName+'.upDownMult;'+lagExpLoc+'.translateZ=(('+lagExpLoc+'.translateZ+$oldVelocity.z)*$friction)*'+fkBaseName+'.upDownMult;if(frame == $attrStart){$velocity = <<0,0,0>>;}if(frame == $attrStart){'+lagExpLoc+'.translateX = 0;'+lagExpLoc+'.translateY= 0;'+lagExpLoc+'.translateZ = 0;}") -ae 1 -uc all ;')

                for at in ('tx','ty','tz'):
                    pm.connectAttr( lagExpDriveLoc+'.'+at, tailFK+'Modify1_GRP.'+at, f=True  )

                prevCtrl = tailFK+'_CTRL'
                

        pm.parentConstraint( self.name+'FKACon_GRP', self.name+'BaseIKOffset_GRP', mo=True )

        constrainObject(  self.name+'MidAIKOffset_GRP',
                        [self.name+'FKACon_GRP',self.parent, self.worldSpace],
                         self.name+'MidAIK_CTRL', ['base', self.parentName, 'world'],
                         type='parentConstraint')

        constrainObject(self.name+'MidBIKOffset_GRP',
                        [self.name+'FKACon_GRP', self.name+'MidAIKCon_GRP' , self.parent, self.worldSpace],
                        self.name+'MidBIK_CTRL', ['base','FK', self.parentName, 'world'],
                        type='parentConstraint')

        constrainObject(self.name+'TipIKOffset_GRP',
                        [self.name+'FKACon_GRP', self.name+'MidBIKCon_GRP', self.parent, self.worldSpace],
                        self.name+'TipIK_CTRL', ['base', 'FK', self.parentName, 'world'],
                        type='parentConstraint')

        ctrlSizeHalf = [self.ctrlSize / 2.0, self.ctrlSize / 2.0, self.ctrlSize / 2.0]
        ctrlSizeQuarter = [self.ctrlSize / 4.0, self.ctrlSize / 4.0, self.ctrlSize / 4.0]
        self.ctrlSize = [self.ctrlSize, self.ctrlSize, self.ctrlSize]

        # scale ctrls
        for ctrl in (self.name+'MidAIK_CTRL', self.name+'MidBIK_CTRL', self.name+'TipIK_CTRL'):
            c = pm.PyNode( ctrl )
            pm.scale(c.cv, self.ctrlSize[0], self.ctrlSize[0], self.ctrlSize[0] )
            pm.move(c.cv, [0, 2*self.ctrlSize[0], 0], relative=True, worldSpace=True)

        tailPointer = rig_control(name=self.name+'Pointer', shape='pyramid', lockHideAttrs=['rx', 'ry', 'rz'],
                                    colour='white', parentOffset=tailModule.controls, rotateOrder=2, scale=self.ctrlSize)
        pm.delete(pm.parentConstraint( listJoints[len(listJoints)-2], tailPointer.offset ))
        constrainObject(tailPointer.offset,
                        [self.parent, self.spine, self.worldSpace],
                        tailPointer.ctrl, [self.parentName, 'fullBody', 'world'], type='parentConstraint')

        tailPointerBase = rig_transform(0, name=self.name+'PointerBase', type='locator',
                                parent=tailModule.parts, target=self.name+'FKA_CTRL').object
        tailPointerTip = rig_transform(0, name=self.name+'PointerTip', type='locator',
                                parent=tailModule.parts, target=tailPointer.con).object

        pm.rotate(tailPointerBase, 0, 0, -90, r=True, os=True)
        pm.rotate(tailPointerTip, 0, 0, -90, r=True, os=True)

        pm.parentConstraint(self.parent, tailPointerBase, mo=True)
        pm.parentConstraint(tailPointer.con, tailPointerTip, mo=True)

        tailPointerTop = mm.eval(
            'rig_makePiston("' + tailPointerBase + '", "' + tailPointerTip + '", "'+self.name+'PointerAim");')

        pm.orientConstraint( tailPointerBase.replace('LOC','JNT'), self.name+'FKAModify2_GRP', mo=True )

        pm.parent(self.name+'MidAIKOffset_GRP', self.name+'MidBIKOffset_GRP',self.name+'TipIKOffset_GRP',
                  tailModule.controls)
        pm.parent(tailJnts, tailModule.skeleton)
        pm.parent(self.name+'_cMUS',self.name+'BaseIKOffset_GRP',tailPointerTop, tailModule.parts)
        pm.parent(self.name+'SplineSetup_GRP',self.name+'BaseIKOffset_GRP',tailPointerTop, tailModule.parts)

        pm.setAttr( tailModule.skeleton+'.inheritsTransform', 0 )

        if self.makeDynamic:
            chainParent( dynJnts, reverse=0 )
            dynJnts.reverse()
            finalChain = rig_jointCopyChain(dynJnts[0], replaceName=('Dyn','Final') )
            for d in dynJnts:
                print 'dynJnt = '+d
            print str(dynJnts)
            print str(finalChain)

            mc.select(self.name+"SplineIK_CRV")
            mm.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')

            hairSystem = pm.ls("|hairSystem?")[0]
            nucleus = pm.ls("|nucleus?")[0]
            dynCurveGrp = pm.ls("|hairSystem?OutputCurves")[0]
            dynCurve = pm.listRelatives(dynCurveGrp, c=True)[0]
            dynCurve = pm.rename(dynCurve, self.name+'Dyn_CRV')

            nmeUpper = self.name.capitalize()
            #ikData = pm.ikHandle(n='dyn'+nmeUpper, sj=dynJnts[0], ee=dynJnts[-1],
            #                                 solver='ikSplineSolver',curve=dynCurve,ccv=False, ns=self.numFKCtrls)

            ikData = rig_ik('dyn'+nmeUpper, dynJnts[0], dynJnts[-1], 
                            'ikSplineSolver', numSpans=self.numFKCtrls, curve=dynCurve, createCurve=False)

            # advanced twist
            pm.setAttr(ikData.handle + '.dTwistControlEnable', 1)
            pm.setAttr(ikData.handle + '.dWorldUpType', 2)  # object up start and end
            pm.setAttr(ikData.handle + '.dForwardAxis', 2)  # positive y
            pm.setAttr(ikData.handle + '.dWorldUpAxis', self.dWorldUpAxis)  # positive x

            pm.connectAttr(self.name+'UpperAim_LOCUp.worldMatrix[0]', ikData.handle.dWorldUpMatrixEnd, f=True)
            pm.connectAttr(self.name+'LowerAim_LOCUp.worldMatrix[0]', ikData.handle.dWorldUpMatrix, f=True)

            mc.setAttr(hairSystem+".collide", 0)
            mc.setAttr(hairSystem+".stretchResistance" ,25)
            mc.setAttr(hairSystem+".bendResistance" ,.1)
            mc.setAttr(hairSystem+".stiffness", 1)
            mc.setAttr(hairSystem+".lengthFlex", 1)
            mc.setAttr(hairSystem+".damp" ,.05)
            mc.setAttr(hairSystem+".stretchDamp", 1)
            mc.setAttr(hairSystem+".mass" ,.2)
            mc.setAttr(hairSystem+".attractionDamp", 1)
            mc.setAttr(hairSystem+".startCurveAttract" , .5)

            mc.setAttr( "follicleShape1.pointLock", 1)
            mc.setAttr( "follicleShape1.overrideDynamics", 1)
            mc.setAttr( "follicleShape1.collide", 0)
            mc.setAttr( "follicleShape1.damp" ,.25)
            mc.setAttr( "follicleShape1.stiffness", 0)
            #mc.setAttr( "follicleShape1.startCurveAttract" ,.3) # 0.3 default dyn stiffness at 0, 1 = 10
            rig_animDrivenKey(fkBaseCtrl.stiffness, (0, 10),
                                              "follicleShape1.startCurveAttract" , (0.3, 1 ))
            pm.connectAttr(fkBaseCtrl.startFrame, 'nucleus1.startFrame', f=True)

            # create tail dyn controls with joints parentd underneath
            # creat another ikSPline 'tailDriven_CRV' and 'tailDriven_ikHandle' and drive final geo, with tail dyn jonints skinned to the ikPlane tail driven crv.

            sc = simpleControls(dynJnts, modify=1, constrainJoints=0, parentCon=1, colour='red' )
            pm.parent ( sc[dynJnts[0]].offset, tailModule.controlsSec )

            i = 0
            for jnt in sc:
                pm.parent( finalChain[i], sc[jnt].con )
                i += 1

            chainList = rig_chain(self.origRootJoint).chain
            ik = rig_ik(self.name+'Driven', self.origRootJoint, chainList[-1], 'ikSplineSolver', numSpans=self.numIKCtrls)
            pm.parent(ik.handle, ik.curve, tailModule.parts)

            # advanced twist
            pm.setAttr(ik.handle + '.dTwistControlEnable', 1)
            pm.setAttr(ik.handle + '.dWorldUpType', 2)  # object up start and end
            pm.setAttr(ik.handle + '.dForwardAxis', 2)  # positive y
            pm.setAttr(ik.handle + '.dWorldUpAxis', self.dWorldUpAxis)  # positive x

            pm.connectAttr(self.name+'UpperAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrixEnd, f=True)
            pm.connectAttr(self.name+'LowerAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrix, f=True)

            pm.skinCluster(finalChain, ik.curve, tsb=True)

            pm.parent( dynJnts[0], 'nucleus1', hairSystem, ikData.handle, ikData.curve ,tailModule.parts)
            pm.delete('hairSystem1OutputCurves')

        self.module = tailModule
