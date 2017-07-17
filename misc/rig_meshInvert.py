

'''

// chad vernon shape inverter
import cvShapeInverter as cvsi
reload(cvsi)
shapes = cvsi.invert()
cmds.delete(shapes, ch=True)

'''''
