
import pymel.core as pm
import maya.cmds as cmds

from make.rig_controls import *

from rutils.rig_utils import *
from rutils.rig_measure import *
from rutils.rig_curve import *
from rutils.rig_anim import *

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

    flexCenter = rig_control(name=name+'FlexCenter', shape='box', scale=(scale,scale,scale),
                             colour='white',lockHideAttrs=['tx','ty','tz','rx','ry','rz'])
    pm.delete(pm.parentConstraint( shapeDriverLoc ,flexCenter.offset))

    flexCtrl = rig_control(name=name+'Flex', shape='sphere', scale=(scale/2,scale/2,scale/2),
                             parentOffset=flexCenter.con, colour='red',lockHideAttrs=['tx','tz','rx','ry','rz'])
    pm.delete(pm.parentConstraint( flexCenter.con ,flexCtrl.offset))

    rig_curveBetweenTwoPoints(flexCenter.con,flexCtrl.con, name=name+'_curveBetween' , degree=1, 
                                colour='white', parent=flexCenter.offset)

    i = 0
    bi = 10
    for shape in shapes:
        if cmds.objExists(flexLoc+'.'+shape):
            rig_animDrivenKey(flexCtrl.ctrl.translateY, (0,bi), flexLoc+'.'+shape, (0,1))
            pm.transformLimits(flexCtrl.ctrl, ty=(i, 10), ety=(i, 1))
            i = -10
            bi = -10

    pm.setAttr(flexCenter.ctrl.overrideDisplayType, 1)

    return flexCenter




