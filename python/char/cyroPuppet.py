__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *
from create.rig_facial import *
from create.rig_quadruped import *

from make.rig_tail import *
from make.rig_controls import *
from make.rig_flex import *

from rutils.rig_nodes import *

import string

'''

# puppet build
import char.cyroPuppet as charPuppet
reload(charPuppet)
charPuppet.build()

charPuppet.buildScene()

'''

def buildScene():
    puppet( character='cyro',buildInScene=1 )

def build():
    puppet( character='cyro' )
    #puppet( character='cyro', rigBound = 'C:/Users/Jerry/Documents/maya/projects/cyro/scenes/rigBound/cyro_new_leg8.ma' )


def cyroPrepareRig():
    print 'Prepare cyro'

    rig_transform(0, name='headJAWorld', target='headJALocal_GRP')
    rig_transform(0, name='headShapeWorld', target='headJALocal_GRP')

    rig_quadPrepare()


def cyroRigModules():
    print 'Create cyro rig modules'

    biped = rig_biped()
    quad = rig_quadruped()

    quad.spine(ctrlSize=50)

    quad.pelvis(ctrlSize=35)

    neckMod = quad.neck(ctrlSize=15, splinePosList=[ 'neckStart_LOC', 'neckMidA_LOC', 'neckMidB_LOC', 'neckEnd_LOC'  ])

    headMod = quad.head(ctrlSize=35)

    # jaw control
    jawControl = rig_control(name='jaw', shape='circle', scale=(25,25,25),
                             lockHideAttrs=['rx'],
                             parentOffset=headMod.controls, colour='white')

    pm.rotate(jawControl.ctrl.cv, -90, 0, 0, r=True, os=True)
    pm.move(jawControl.ctrl.cv, 2, 0, 0, r=True, os=True)

    pm.delete(pm.parentConstraint( 'jawJA_JNT' ,jawControl.offset))
    pm.parentConstraint('headJA_JNT', jawControl.offset, mo=True)
    pm.parentConstraint(jawControl.con, 'jawJA_JNT', mo=True)
    jawPos = pm.xform('jawJA_JNT', translation=True, query=True, ws=True)
    jawEndPos = pm.xform( 'jawJEnd_JNT', translation=True, query=True, ws=True)
    jawLength = lengthVector(jawPos, jawEndPos)
    pm.move(pm.PyNode(jawControl.ctrl + '.cv[:]'), jawLength/2,0, 0, r=True, os=True)

    
    biped.spineFullBodyCtrl = quad.spineFullBodyCtrl
    biped.spineUpperCtrl = quad.spineUpperCtrl
    biped.spineLowerCtrl = quad.spineLowerCtrl

    biped.pelvisControl = quad.pelvisControl

    biped.elbowAxis = 'ry'
    
    for side in ['l', 'r']:
        armModule = biped.arm(side, ctrlSize=12)

        fingersModule = biped.hand(side, ctrlSize=4, baseLimit=1)

        shoulderModule = biped.shoulder(side, ctrlSize=10)

        biped.connectArmShoulder(side)

        cyroShoulderUpgrade(side=side, ctrlSize=10)

        if side == 'l':
            quad.switchLoc = biped.switchLoc
        
        # make quadruped leg 
        legModule = quad.leg(side, ctrlSize = 30)

        toesModule = quad.foot(side, ctrlSize=7, baseLimit=1)

        quad.connectLegPelvis()

    tail = rig_tail( rootJoint = 'tailJA_JNT',
                        numIKCtrls = 8, 
                        numFKCtrls = 8,  
                        ctrlSize = 15,
                        makeDynamic = 1 )
    tail.make()
    pm.parent('tailDynJA_JNT', 'pelvisJA_JNT')

    pubisControl = rig_control(name='pubis', shape='box', scale=(25,25,25),
                             parentOffset='spineControls_GRP', colour='white')
    pm.delete(pm.parentConstraint( 'pubisJA_JNT' ,pubisControl.offset))
    pm.parentConstraint('pelvisJA_JNT', pubisControl.offset, mo=True)
    pm.parentConstraint(pubisControl.con, 'pubisJA_JNT', mo=True)

    pm.move(pubisControl.ctrl.cv, 36, 0, 0, r=True, os=True)
    pm.scale(pubisControl.ctrl.cv, 1, 0.5 ,1 )

    tongueModule = rig_ikChainSpline( 'tongue' , 'tongueJA_JNT', ctrlSize=5, parent='jawJA_JNT',
                                       numIkControls=3, numFkControls=3)

    cmds.setAttr("tongueFKA_CTRL.stretch", 1)
    pm.rotate( pm.PyNode('tongueFKC_CTRL').cv, 70, 0, 0,r=True,os=True )
    pm.scale( pm.PyNode('tongueFKC_CTRL').cv, 0.4, 0.4, 0.4,r=True,os=True )
    pm.rotate( pm.PyNode('tongueFKB_CTRL').cv, 65, 0, 0,r=True,os=True )
    pm.move( pm.PyNode('tongueFKB_CTRL').cv, 0, 10, 0,r=True,os=True )

    cryoBuildFacial()

    cyroFlexControls()

    spineCtrl = quad.spineUpperCtrl.ctrl
    pm.addAttr(spineCtrl, ln='SHAPES', at='enum',
                       enumName='___________',
                       k=True)
    spineCtrl.SHAPES.setLocked(True)
    pm.addAttr(spineCtrl, longName='breathe',
               attributeType="double",
               min=-10, max=10, defaultValue=0, keyable=True)
    rig_animDrivenKey(spineCtrl.breathe, (0,10), 'flexShapes_LOC.breathOut', (0,1))
    rig_animDrivenKey(spineCtrl.breathe, (0,-10), 'flexShapes_LOC.breathIn', (0,1))

def cyroFinish():
    print 'Finishing cyro'

    rig_quadFinalize()

    pm.setAttr("neckFocus_CTRL.focusNeck", 0.75)

    pm.setAttr("spineUpperPivot_CTRL.translateY", -17.164)
    pm.setAttr("spineUpperPivot_CTRL.translateZ", 1.81)
    pm.setAttr("spineUpper_CTRL.stretch", 0.2)

    pm.move( 'tailUpperAim_LOCUp', 0, 1000, 0,r=True,os=True )
    pm.move('tailLowerAim_LOCUp', 0, 1000, 0, r=True, os=True)

    pm.move(pm.PyNode( 'neckTipIK_CTRL.cv[:]'), 0 , 0, -5, r=True, os=True)
    pm.move(pm.PyNode( 'neckMidBIK_CTRL.cv[:]'), 0 ,-8.5, -13, r=True, os=True)
    pm.move(pm.PyNode( 'neckMidAIK_CTRL.cv[:]'), 0 , -1 , -23, r=True, os=True)
    
    controlSet = pm.PyNode('cyroRigPuppetControlSet')
    for s in ('l', 'r'):
        pm.setAttr("displayModulesToggleControl."+s+"_fingers", 0)
        pm.setAttr("displayModulesToggleControl."+s+"_toes", 0)

        pm.setAttr(s+"_armPV_CTRL.space", 1)
        #pm.setAttr(s+"_shoulder_CTRL.followArm", 1)

        pm.rotate(pm.PyNode(s+'_handBall_CTRL').cv, 0, 90, 0, r=True, os=True)
        pm.scale(pm.PyNode(s+'_handBall_CTRL').cv, 2, 2, 2)

        pm.parentConstraint( s+'_anklePos_JNT', s+'_toeThumbModify1_GRP' ,mo=True )

        controlSet.removeMembers([ s+'_shoulder_CTRL' ])

    hiDeltaMush = mm.eval('rig_returnDeformers("skin_C_body_GV", "deltaMush")')
    if len(hiDeltaMush) > 0:
        cNode = conditionNode( 'hiDeltaMush', 'equal', ('',0), ('', 2), ('', 1), ('', 0) )
        pm.connectAttr( "global_CTRL.lodDisplay", cNode+'.secondTerm')
        pm.connectAttr( cNode+'.outColorR', hiDeltaMush[0]+'.envelope')
        
    # mid LOD
    #cmds.setAttr("global_CTRL.lodDisplay", 1)


def cyroShoulderUpgrade(side='', ctrlSize=1):
    name = side+'_quadShoulder'

    module = rig_module(name)

    ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
    ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

    shoulderControl = rig_control( side=side, name='quadShoulder', shape='pyramid',
                                    targetOffset=side+'_clavicleJA_JNT', modify=1,
                                    parentOffset=module.controls,lockHideAttrs=[
                'rx','ry','rz'], scale =ctrlSize, rotateOrder=0 )

    clavPos = pm.xform(side+'_clavicleJA_JNT', translation=True, query=True, ws=True)
    armPos = pm.xform(side+'_scapulaJA_JNT', translation=True, query=True, ws=True)
    clavLength = lengthVector( armPos, clavPos )
    if side == 'l':
        pm.move( pm.PyNode( shoulderControl.offset ), clavLength,0,0, r=True,
                 os=True )
    else:
        pm.move(pm.PyNode(shoulderControl.offset), -1*clavLength, 0, 0, r=True,
                os=True)
    pm.rotate( pm.PyNode( shoulderControl.offset ), 0,0,-90, r=True, os=True )
    

    pm.parentConstraint( 'spineJF_JNT', shoulderControl.offset, mo=True )

    clavicleAim = rig_transform(0, name=side + '_clavicleAim', type='locator',
                                    parent=module.parts, target=side+'_clavicleJA_JNT').object
    armAim = rig_transform(0, name=side + '_quadShoulderAim', type='locator',
                            parent=module.parts).object


    pm.pointConstraint( 'spineJF_JNT', clavicleAim,mo=True )
    pm.pointConstraint( shoulderControl.con, armAim )

    quadShoulderAimTop = mm.eval('rig_makePiston("'+clavicleAim+'", "'+armAim+'", "'+side+'_quadShoulderAim");')


    #pm.orientConstraint( clavicleAim, side+'_shoulder_CTRL', mo=True )
    
    pm.delete(pm.listRelatives(side+'_shoulderOffset_GRP', type='constraint'))
    pm.parentConstraint( clavicleAim, side+'_shoulderOffset_GRP', mo=True )

    pm.addAttr(shoulderControl.ctrl, longName='followArm',
                           at='float', k=True, min=0,
                           max=10, defaultValue=1)

    pm.connectAttr( shoulderControl.ctrl.followArm, side+'_shoulder_CTRL.followArm'  )

    baseLimit = 15
    pm.transformLimits(shoulderControl.ctrl, tx=(-1 * baseLimit, baseLimit), etx=(1, 1))
    pm.transformLimits(shoulderControl.ctrl, ty=(-1 * baseLimit, baseLimit), ety=(1, 1))
    pm.transformLimits(shoulderControl.ctrl, tz=(-1 * baseLimit, baseLimit), etz=(1, 1))

    scapulaControl = rig_control( side=side, name='quadScapula', shape='box',
                                    targetOffset=side+'_scapulaJEnd_JNT', modify=1,
                                    parentOffset=module.controls,lockHideAttrs=[
                'rx','ry','rz'], scale =ctrlSize, rotateOrder=0 )

    pm.delete( pm.orientConstraint( side+'_scapulaJA_JNT', scapulaControl.offset ) )


    scapulaAim = rig_transform(0, name=side + '_quadScapulaAim', type='locator',
                                    parent=module.parts).object
    scapulaEndAim = rig_transform(0, name=side + '_quadScapulaEndAim', type='locator',
                            parent=module.parts).object

    pm.delete( pm.parentConstraint(side+'_scapulaJA_JNT', scapulaAim ) )
    pm.pointConstraint( side+'_clavicleJA_JNT', scapulaAim,mo=True )
    pm.pointConstraint( scapulaControl.con, scapulaEndAim )
    pm.delete( pm.orientConstraint( side+'_scapulaJA_JNT', scapulaEndAim ) )

    quadScapulaAimTop = mm.eval('rig_makePiston("'+scapulaAim+'", "'+scapulaEndAim+'", "'+side+'_quadScapulaAim");')

    #pm.parentConstraint( side+'_clavicleJA_JNT', 'spineJE_JNT', scapulaControl.offset, mo=True )

    constrainObject(  scapulaControl.offset,
                [side+'_clavicleJA_JNT','spineJE_JNT'], '', [],
                 type='parentConstraint', doSpace=0, setVal=(0.5,1))

    baseLimit = 5
    pm.transformLimits(scapulaControl.ctrl, tx=(-1 * baseLimit, baseLimit), etx=(1, 1))
    pm.transformLimits(scapulaControl.ctrl, ty=(-1 * baseLimit, baseLimit), ety=(1, 1))
    pm.transformLimits(scapulaControl.ctrl, tz=(-1 * baseLimit, baseLimit), etz=(1, 1))


    pm.orientConstraint( scapulaAim, side+'_scapulaJA_JNT', mo=True )

    pm.hide(side+'_shoulderOffset_GRP')

    pm.parent( quadShoulderAimTop, quadScapulaAimTop, module.parts )


##############################################################################################################################
'''

facial

import char.cyroPuppet as charPuppet
reload(charPuppet)

charPuppet.cyroFacialShapeDriver()
charPuppet.cyroConnectShapesToShapeBS('hi_shapesBS')
charPuppet.cyroConnectShapesToShapeBS('mid_shapesBS')

'''

def cyroShapeDriverList():
    shapes = []

    sideShapes = []
    for s in ('l','r'):
        sideShapes.extend( [
            s+'_nostrilClose',
            s+'_nostrilOpen',
            s+'_eyeClosed'
        ] )

    shapes.extend(sideShapes)

    return shapes

def cyroConnectShapesToShapeBS(shapeBS):

    shapeDriver = 'facialShapeDriver_LOC'

    shapes = cyroShapeDriverList()

    for shape in shapes:
        if cmds.objExists(shapeBS+'.'+shape):
            pm.connectAttr(shapeDriver+'.'+shape, shapeBS+'.'+shape, f=True )

def cyroFacialShapeDriver():

    shapeDriver = 'facialShapeDriver_LOC'
    if not cmds.objExists(shapeDriver):
        shapeDriver = rig_transform(0, name='facialShapeDriver',
                                    type='locator',
                                    parent='rig_GRP').object

    shapeDriver = pm.PyNode(shapeDriver)

    shapes = cyroShapeDriverList()

    pm.addAttr(shapeDriver, ln='SHAPE', at='enum',
               enumName='___________',
               k=True)
    shapeDriver.SHAPE.setLocked(True)

    for shape in shapes:
        print shape
        pm.addAttr(shapeDriver, longName=shape, at='float', k=True, min=0,
                   max=1, dv=0)



def cryoBuildFacial():
    # build facial
    print 'Cyro Facial'

    facialModule = rig_module('facial')
    pm.parent(facialModule.top, 'rigModules_GRP')

    # build shape locators

    for side in ['l', 'r']:
        nostrilCtrl = twoWayShapeControl(side + '_nostrilShape_LOC', (side + '_nostrilClose', side + '_nostrilOpen'),
                            'headShapeWorld_GRP', mult=1.5, ctrlSize=10, negPos=1)

        pm.rotate(nostrilCtrl.ctrl.cv, -90, 0, 0,r=True, os=True)

        pm.addAttr(nostrilCtrl.ctrl, longName='sinusBreathe',
               attributeType="double",
               min=0, max=1, defaultValue=1, keyable=True)

        nostrilMD = multiplyDivideNode( side+'nostril', 'multiply', input1=[nostrilCtrl.ctrl.sinusBreathe,0,0], 
                                        input2=[nostrilCtrl.ctrl.translateY,1,1],
                                        output=['facialShapeDriver_LOC.'+side+'_sinusBreathe'])


        eyeCtrl = oneWayShapeControl(side + '_eyeShape_LOC', side+'_eyeClosed',
                           'headShapeWorld_GRP', mult=1.5, ctrlSize=10, negPos=1)

        pm.rotate(eyeCtrl.ctrl.cv, 0, -90, 0,r=True, os=True)
        if side == 'r':
            pm.rotate(eyeCtrl.ctrl.cv, 180, 0, 0,r=True, os=True)



    pm.parent('headShapeWorld_GRP', facialModule.controls)
    pm.parentConstraint('headJA_JNT', 'headShapeWorld_GRP')

    # build simple controllers
    facialLocalWorldControllers(facialModule, 'headJAWorld_GRP', ctrlSize=1)

    pm.parentConstraint( 'headJA_JNT', 'headJAWorld_GRP' )

    pm.parent( 'headJAWorld_GRP', facialModule.controlsSec )

    pm.setAttr( 'facial_GRP.inheritsTransform', 0)
    pm.setAttr( facialModule.parts+'.inheritsTransform', 0)

    pm.delete('shapeLocs_GRP')

    lipTwkers = pm.ls("*LipTwker*_CTRL")
    for c in lipTwkers:
        pm.scale(c.cv, 1.5, 1.5, 1.5, r=True)

    lipTwkers = pm.ls("l_*Lip*Twk_CTRL")
    for c in lipTwkers:
        pm.move(c.cv, 2.6, 0, 0, r=True)
    lipTwkers = pm.ls("r_*Lip*Twk_CTRL")
    for c in lipTwkers:
        pm.move(c.cv, -2.6, 0, 0, r=True)

    pm.move(pm.PyNode('lowerLipTwk_CTRL').cv, 0, 0, 3.7, r=True)
    pm.move(pm.PyNode('upperLipTwk_CTRL').cv, 0, 0, 3.7, r=True)

    pm.move( pm.PyNode('nostrilMoverTwk_CTRL').cv, 0, 0, 10,r=True,os=True )

    pm.move( pm.PyNode('l_masseterTwk_CTRL').cv, 0, 0, 0.3,r=True,os=True )
    pm.move( pm.PyNode('r_masseterTwk_CTRL').cv, 0, 0, -0.3,r=True,os=True )

    print 'Finished Cyro Facial'
    
def setFlex(name, driver, shapes, parents, colour='red'):
    print 'setFlex start'
    ctrl = rig_flexControl(name, driver, shapes=shapes, colour=colour)
    if isinstance('', str):
        pm.parentConstraint( parents, ctrl.offset, mo=True)
    else:
        pm.pointConstraint(parents[0], parents[1], ctrl.offset, mo=True )
        con = pm.orientConstraint(parents[0], parents[1], ctrl.offset, mo=True )
        pm.setAttr(con.interpType, 2)
    print 'setFlex end'
    return ctrl

def cyroFlexControls():
    print 'cyroFlexControls start'
    flexModule = rig_module('flex')

    hyoidCtrl = setFlex('hyoid', 'hyoidShapeDriver_LOC', shapes=['hyoidIn_neck','hyoidOut_neck'],
                parents=('jawJEnd_JNT', 'neckJA_JNT') )
    neckTense = setFlex('neckTense', 'neckTenseShapeDriver_LOC', shapes=['tenseOut_neck','tenseIn_neck'],
                parents=('jawJEnd_JNT', 'neckJA_JNT'), colour='orange' )
    neckSwallow = setFlex('neckSwallow', 'neckSwallowShapeDriver_LOC', shapes=['swallowDown_neck','swallowUp_neck'],
                parents='neckJC_JNT' )
    neckBulge = setFlex('neckBulge', 'neckBulgeShapeDriver_LOC', shapes=['bulgeOut_neck','bulgeIn_neck'],
                parents='neckJB_JNT', colour='orange' )

    pm.parent(hyoidCtrl.offset, neckTense.offset, neckSwallow.offset, neckBulge.offset, flexModule.controls )

    print 'cyroFlexControls end'













