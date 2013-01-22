import maya.cmds as cmds

#contains all of the procedures relating to joint creation

#--------------TOP LEVEL-------------#    
#these are procedures that are attached buttons

#runs the rotation to orient procedure for each selected
#object

def runRotToOrient():
    selection = cmds.ls(selection=True)
    for i in selection:
        rotToOrient(i)

#--------------Low Level-------------#
#these are low level procedures that are not directly
#attached to a button, but used by the ones that are

# a procedure to transfer the rotation of a joint into it's 
#orientation
def rotToOrient(_objName):
    initOrientX = cmds.getAttr(_objName+".jointOrientX")
    newOrientX = cmds.getAttr(_objName+".rotateX")+initOrientX
    cmds.setAttr(_objName+".jointOrientX", newOrientX)
    
    initOrientY = cmds.getAttr(_objName+".jointOrientY")
    newOrientY = cmds.getAttr(_objName+".rotateY")+initOrientY
    cmds.setAttr(_objName+".jointOrientY", newOrientY)
    
    initOrientZ = cmds.getAttr(_objName+".jointOrientZ")
    newOrientZ = cmds.getAttr(_objName+".rotateZ")+initOrientZ
    cmds.setAttr(_objName+".jointOrientZ", newOrientZ)
    
    cmds.rotate(0, 0, 0, _objName, absolute = True)
    