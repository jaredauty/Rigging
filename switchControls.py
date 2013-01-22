# This script replaces a control shape with a new one without
# changing the transform node.
# WARNING this will not work properly if the new control has 
# connections into it.

import maya.cmds as cmds

def switchShape(_old, _new, _copy=False):
    if _copy:
        _new = cmds.duplicate(_new, rc=1)
    #Prepare the shape
    tmpGroup = cmds.group(em=1)
    cmds.parent(tmpGroup, _old, r=1)
    cmds.parent(_new, tmpGroup, a=1)
    cmds.parent(tmpGroup, w=1, r=1)
    cmds.makeIdentity(_new, apply=True)
    #Switch the shape
    newShape = cmds.listRelatives(_new, s=1)
    oldShape = cmds.listRelatives(_old, s=1)
    cmds.parent(newShape, _old, s=1, r=1)
    #Clean up
    cmds.delete(oldShape)
    cmds.delete(_new)
    cmds.delete(tmpGroup)


sel=cmds.ls(selection=1)
switchShape(sel[0], sel[1])

