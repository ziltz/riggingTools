__author__ = 'Jerry'

import pymel.core as pm


def rig_animDrivenKey( driver, driverValues, driven, drivenValues ):

	for i in range(0, len(driverValues)):
		pm.setDrivenKeyframe(driven, cd=driver,
	                        v=drivenValues[i], dv=driverValues[i])
