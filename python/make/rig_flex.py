
import pymel.core as pm
import maya.cmds as cmds

from make.rig_controls import *

from rutils.rig_utils import *
from rutils.rig_measure import *
from rutils.rig_curve import *
from rutils.rig_anim import *
from rutils.rig_transform import *
from rutils.rig_nodes import *
from rutils.rig_name import *

'''

isotonic is the automatic flexing measured from difference in length
isometric is the manual flexing that animators will control 


'''


class rig_flex(object):
    
    
    def __init__(self, **kwds):
        
        self.name = defaultReturn('muscleFlex', 'name', param=kwds)

        self.flexLoc = defaultReturn('flexShapes_LOC', 'flexLoc', param=kwds)

        # names of shapes
        self.flexor = defaultReturn('bicep', 'flexor', param=kwds)
        self.extensor = defaultReturn('tricep', 'extensor', param=kwds)

        # start and end contrainers
        self.start = defaultReturn(None, 'start', param=kwds)
        self.end = defaultReturn(None, 'end', param=kwds)
        self.parent = defaultReturn(None, 'parent', param=kwds)

        self.controls = defaultReturn([], 'controls', param=kwds) # placement of control



    def lengthMeasure(self):
        rig_measure(name=self.name, start=self.start, end=self.end, parent=self.parent)




'''

bi-directional control

rig_flexControl('hyoid', 'hyoidShapeDriver_LOC', shapes=['hyoidIn_neck','hyoidOut_neck'], flexLoc='flexShapes_LOC')

'''
def rig_flexControl(name, shapeDriverLoc, shapes=[], flexLoc='flexShapes_LOC', **kwds):

    scale = defaultReturn(5, 'scale', param=kwds)
    shape = defaultReturn('sphere', 'shape', param=kwds)
    colour = defaultReturn('red', 'colour', param=kwds)

    flexCenter = rig_control(name=name+'FlexCenter', shape='box', scale=(scale,scale,scale),
                             colour='white',lockHideAttrs=['tx','ty','tz','rx','ry','rz'])
    pm.delete(pm.parentConstraint( shapeDriverLoc ,flexCenter.offset))

    flexCtrl = rig_control(name=name+'Flex', shape=shape, scale=(scale/2,scale/2,scale/2),
                             parentOffset=flexCenter.con, colour=colour,lockHideAttrs=['tx','tz','rx','ry','rz'])
    pm.delete(pm.parentConstraint( flexCenter.con ,flexCtrl.offset))

    rig_curveBetweenTwoPoints(flexCenter.con,flexCtrl.con, name=name+'_curveBetween' , degree=1, 
                                colour=colour, parent=flexCenter.offset)

    i = 0
    bi = 10
    for shape in shapes:
        if cmds.objExists(flexLoc+'.'+shape):
            rig_animDrivenKey(flexCtrl.ctrl.translateY, (0,bi), flexLoc+'.'+shape, (0,1))
            pm.transformLimits(flexCtrl.ctrl, ty=(i, 10), ety=(i, 1))
            i = -10
            bi = -10

    pm.setAttr(flexCenter.ctrl.overrideDisplayType, 1)
    
    pm.select(flexCtrl.ctrl.cv[1], flexCtrl.ctrl.cv[27], flexCtrl.ctrl.cv[36],
                 flexCtrl.ctrl.cv[46], flexCtrl.ctrl.cv[54], r=True)
    pm.move(0, 3, 0,r=True, os=True, wd=True)

    pm.select(flexCtrl.ctrl.cv[22], flexCtrl.ctrl.cv[32], flexCtrl.ctrl.cv[41],
                 flexCtrl.ctrl.cv[50], flexCtrl.ctrl.cv[61], r=True)
    pm.move(0, -1, 0,r=True, os=True, wd=True)
    
    
    return (flexCenter, flexCtrl)


'''

// Result: Connected l_armTotal_distance.globalOriginalPercent to remapValue1.inputValue. //

connectAttr -f l_armTotal_distance.globalOriginalPercent plusMinusAverage4.input1D[0];
connectAttr -f multiplyDivide1.outputX plusMinusAverage4.input1D[1];
connectAttr -f l_armTotal_distance.globalOriginalPercent multiplyDivide1.input1X;
setAttr "multiplyDivide1.input2X" -1; // -1 = auto off // 0 = auto on

connectAttr -f plusMinusAverage4.output1D condition1.firstTerm;
setAttr "condition1.secondTerm" 0;
setAttr "condition1.colorIfTrueR" 1;
connectAttr -f condition1.outColorR remapValue1.inputValue;
connectAttr -f plusMinusAverage4.output1D condition1.colorIfFalseR;

setAttr "remapValue1.value[0].value_Interp" 2;
 
// Result: Connected remapValue1.outValue to flexShapes_LOC.l_upperFront_arm. //

to take away flex
setAttr "remapValue1.inputMin" 0.38;
to add flex
setAttr "remapValue1.outputMin" 0.55;


setAttr "remapValue1.value[1].value_Interp" 2;
setAttr "remapValue1.inputMin" 1;
setAttr "remapValue1.inputMax" 0;

'''
def rig_autoFlexControl(name, shapeDriverLoc, startEnd=(), shapeDriven='', flexLoc='flexShapes_LOC',module=None, **kwds):


    scale = defaultReturn(5, 'scale', param=kwds)
    shape = defaultReturn('sphere', 'shape', param=kwds)
    colour = defaultReturn('red', 'colour', param=kwds)

    if not cmds.objExists(flexLoc+'.'+shapeDriven):
        pm.warning( flexLoc+'.'+shapeDriven+' = does not exist ! Not making auto flex control' )
        return 


    if module == None:
        parent = rig_transform(0, name=name + '_measureSetup').object
    else:
        parent = module.parts

    distNode = rig_measure(name=name+'FlexDistance', start=startEnd[0], end=startEnd[1],
                            parent=parent)


    flexCenter = rig_control(name=name+'FlexCenter', shape='box', scale=(scale,scale,scale),
                             colour='white',lockHideAttrs=['tx','ty','tz','rx','ry','rz'], parentOffset=module.controls)
    pm.delete(pm.parentConstraint( shapeDriverLoc ,flexCenter.offset))

    flexCtrl = rig_control(name=name+'Flex', shape=shape, scale=(scale/2,scale/2,scale/2),
                             parentOffset=flexCenter.con, colour=colour,lockHideAttrs=['tx','tz','rx','ry','rz'])
    pm.delete(pm.parentConstraint( flexCenter.con ,flexCtrl.offset))

    rig_curveBetweenTwoPoints(flexCenter.con,flexCtrl.con, name=name+'_curveBetween' , degree=1, 
                                colour=colour, parent=flexCenter.offset)

    pm.addAttr(flexCtrl.ctrl, longName='autoFlex',
               attributeType="long",
               min=0, max=1, defaultValue=1, keyable=True)


    mdNode = multiplyDivideNode( name+'_flexMD', 'multiply', 
                input1=[distNode.distance+'.globalOriginalPercent',0,0], input2=[1,1,1],output=[])
    pmNode = plusMinusNode( name+'_flexPM', 'sum', distNode.distance, 'globalOriginalPercent', 
                                                    mdNode, 'outputX' )
    conNode = conditionNode( name+'_flexCondition', 'equal', (pmNode, 'output1D'), 
                                ('',0), ('',1), (pmNode, 'output1D') )
    remapNode = remapValueNode( conNode+'.outColorR', 1, 0, 0, 1, name=name, valueinterp=2 )

    rig_animDrivenKey(flexCtrl.ctrl.autoFlex, (0,1), mdNode+'.input2X', (-1,0))

    rig_animDrivenKey(flexCtrl.ctrl.translateY, (0,-10), remapNode+'.inputMin', (1,0.8))
    rig_animDrivenKey(flexCtrl.ctrl.translateY, (0,10), remapNode+'.outputMin', (0,1))

    pm.setAttr(remapNode+'.inputMax', 0.8 )

    pm.connectAttr(remapNode+'.outValue', flexLoc+'.'+shapeDriven, f=True)

    pm.transformLimits(flexCtrl.ctrl, ty=(-10, 10), ety=(1, 1))

    mdNode = multiplyDivideNode( name+'_flexOffsetMD', 'multiply', 
                input1=[remapNode+'.outValue',0,0], input2=[10,1,1],output=[flexCtrl.offset+'.translateY'])

    pm.setAttr(flexCenter.ctrl.overrideDisplayType, 1)
    
    pm.select(flexCtrl.ctrl.cv[1], flexCtrl.ctrl.cv[27], flexCtrl.ctrl.cv[36],
                 flexCtrl.ctrl.cv[46], flexCtrl.ctrl.cv[54], r=True)
    pm.move(0, 3, 0,r=True, os=True, wd=True)

    pm.select(flexCtrl.ctrl.cv[22], flexCtrl.ctrl.cv[32], flexCtrl.ctrl.cv[41],
                 flexCtrl.ctrl.cv[50], flexCtrl.ctrl.cv[61], r=True)
    pm.move(0, -1, 0,r=True, os=True, wd=True)



    return (flexCenter, flexCtrl)












