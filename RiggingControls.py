import maya.cmds as cmds
import math
import RiggingGroups as rg

reload(rg)

#contains all of the procedures used to create controls

#--------------TOP LEVEL-------------#    
#these are procedures that are attached buttons

#a procedure which scales a control shape without effecting
#its orientation
#_factor is the scale factor and the other three inputs are
#boolean values defining which axis are scaled
#does this for each control in the selection

def sclCtrlShape (_sel, _factor,_sclX = True, _sclY = True, _sclZ = True):
    #set default scale factors    
    
    factorX = 1
    factorY = 1
    factorZ = 1
    

    #set the user defined values    
    
    if (_sclX == True):
        factorX = _factor
    if (_sclY == True):
        factorY = _factor
    if (_sclZ == True):
        factorZ = _factor
        
    #clear the selection
    
    cmds.select(clear = True)
        
    for controlName in _sel:
        #error catching, in case something other than a 
        #curve or circle is selected
        
        cmds.selectMode(component = True)
        
        try: 
            #selects the cvs in a nurbs curve or circle
            
            cmds.select(controlName+".cv[0:"+ str(getCVs(controlName)-1) + "]")
        except:
            #prints the reason for the failure
            
            print "Button not Activated: Control to Scale Must be a Curve or Circle"
        
        cmds.scale(factorX,factorY,factorZ, os = True, r = True)
    
    #select all of the controls that were originally selected
    
    cmds.selectMode(object = True)
    cmds.select(_sel)

#a procedure which rotates a control shape without effecting
#its orientation
#_isPositive defines whether the rotation is in the positive
#or negative x direction
#does this for each control in the selection

def rotCtrlShapeX (_isPositive):
    sel = cmds.ls(selection = True)
    for controlName in sel:
        #clear the selection
        
        cmds.select(clear = True)
        #error catching, in case something other than a  
        #curve or circle is selected
        
        cmds.selectMode(component = True)
        try:
            #selects the cvs in a nurbs curve or circle
            
            cmds.select(controlName+".cv[0:"+ str(getCVs(controlName)-1) + "]")
            
        except:
            #prints the reason for the failure
            
            print "Button not Activated: Control to Scale Must be a Curve or Circle"
        
        #does the rotation
        
        if (_isPositive == True):
            cmds.rotate(90,0,0, os = True, r = True)
        else:
            cmds.rotate(-90,0,0, os = True, r = True)
                
    #select all of the controls that were originally selected
    
    cmds.selectMode(object = True)
    cmds.select(sel)



# orients the selected objects to the last one selected

def orientSelection ():
    sel = cmds.ls(selection = True)
    length = len(sel)
    
    #check that there's enough objects selected
    
    if (length > 1):
        for i in range (0, (length -1)):
            orientControl (sel[i], sel[length-1])
    else:
        #if not print error message
        
        print "Button not Activated: At Least 2 Objects Must be Selected"

#creates a nurbs circle control, orients it to the selected
#object and names it based on the name of the joint.
#if _isDigitCtrl is true then the control is shaped into a default
#control shape for fingers or toes
#if _attachFK is true it creates an orient constraint from the newly
#created control to the joint
#this is done for each joint in the selection
#It will return a list of all the controls created

def makeCTRL(_jointName, _isDigitCtrl, _attachFK, _ext = False,_jntExt = "_CTRL"):
    _controlName = changeExt (_jointName, _jntExt)
    
    #create a circle with the desired name and orient
    #it to the joint
    
    cmds.circle(name = _controlName, nr=(1, 0, 0), c=(0, 0, 0) )
    orientControl (_controlName, _jointName)
    #if it is a control meant for a finger or toe or claw or any other
    #kind of digit imaginable, modify the shape accordingly
    
    if (_isDigitCtrl == True):
        cmds.select(_controlName+".cv[0:7]")
        cmds.move(0,0,-2, os = True, r = True)
        cmds.select(clear = True) 
        cmds.select(_controlName+".cv[4]", _controlName+".cv[6]")
        cmds.scale(1,0.1,1)
        cmds.move(0,0,-0.6, os = True, r = True)
        cmds.select(clear = True) 
        cmds.select(_controlName+".cv[3]", _controlName+".cv[7]") 
        cmds.scale(1,0.7,1)
        cmds.select(clear = True) 
        cmds.select(_controlName+".cv[0:7]")
        cmds.scale(1,0.8,1)
        cmds.scale(0.5,0.5,0.5, os = True)
        cmds.select(clear = True)

    #add the default 3 groups
    rg.add3Groups(_controlName, _ext)
    
    #if attachFK is true, set up the orient constraint
    
    if (_attachFK == True):
        """
        cmds.parentConstraint(
            _controlName,
            _jointName,
            st = ["x", "y", "z"]
            )
        """
        cmds.orientConstraint(_controlName, _jointName)
    return _controlName

def makeGimbalCTRL(_obj, _isDigitCtrl, _attachFK):
    mainCtrl = makeCTRL(_obj, _isDigitCtrl, False, ["_SDK", "_CONST", "_0"])
    
    # Create base
    gimbalName = makeCTRL(_obj, _isDigitCtrl, _attachFK, ["_SDK", "_CONST", "_0"], "_GBL_CTRL")
    cmds.parent(gimbalName+"_0", mainCtrl)
    # Edit gimbal shape
    gimbalShape(gimbalName, 0.5)
    return [gimbalName, mainCtrl]
            
# a procedure to generate a joint shaped control curve

def jointControl ():
    #generate 3 circles and store their names, this prevents
    #any chance of name clashes breaking the script
    
    circle1 = cmds.circle()
    circle2 = cmds.circle()
    circle3 = cmds.circle()
    
    #rotate two of the circles to make the joint shape
    
    cmds.rotate(0, 90, 0, circle2[0])
    cmds.rotate(90, 0, 0, circle3[0])
    
    #freezes transformations
    
    cmds.makeIdentity(circle2[0], apply = True)
    cmds.makeIdentity(circle3[0], apply = True)
    
    #stores the names of the shape nodes of the second two
    #circles
    
    circleShape2 = cmds.listRelatives(circle2[0],shapes = True)
    circleShape3 = cmds.listRelatives(circle3[0],shapes = True)
    
    #parents them to the transform node of the first circle
    
    cmds.parent(circle2[0]+"|"+circleShape2[0], circle1[0], s = True, add = True)
    cmds.parent(circle3[0]+"|"+circleShape3[0], circle1[0], s = True, add = True)
    
    #deletes the second two circles
    
    cmds.delete(circle2[0])
    cmds.delete(circle3[0])
    
    #renames the first
    
    cmds.rename(circle1[0], "jointCTRL")
    
def createLine(_parents):
    nodes = []
    lineCurve = ""
    firstTime = True
    for obj in _parents:
        pos = cmds.xform(obj, q=1, t=1, ws=1)
        if firstTime:
            lineCurve = cmds.curve(d=1, p=[pos])
            nodes.append(lineCurve)
            cmds.setAttr(lineCurve+".overrideEnabled", 1)
            cmds.setAttr(lineCurve+".overrideDisplayType", 2)
            cmds.setAttr(lineCurve+".inheritsTransform", 0)
            firstTime = False
        else:
            cmds.curve(lineCurve, a=True, p=pos)
    #Clusters must be added after all the cvs are created.
    #Don't ask me why!
    for j in range(len(_parents)):
        clusterName = _parents[j]+"_CLUSTER"
        clusterPoint = cmds.cluster(lineCurve+".cv["+str(j)+"]", n=clusterName)
        nodes.append(clusterPoint[1])
        cmds.setAttr(clusterPoint[1]+".visibility", 0)
        cmds.parent(clusterPoint[1], _parents[j], a=1)
    return nodes


#--------------Low Level-------------#
#these are low level procedures that are not directly
#attached to a button, but used by the ones that are

#returns the number of spans + the number of degrees,
#which is the exact number of cvs of a curve, but
#greater than the number of cvs on a circle. however,
#if asked to select cvs 0 to 10 when there are only 8,
#maya will only select the 8 that are there, so the fact that
#it returns an excess number for circles is not an issue

def getCVs (_controlName):
    val = cmds.getAttr(_controlName + ".spans") + cmds.getAttr(_controlName + ".degree")
    return val

#orients the control (first variable) to the joint 
#(second variable)

def orientControl (_controlName, _jointName):
    # get parent 
    parentObject = cmds.listRelatives(_controlName, p=1)
    cmds.parent(_controlName, _jointName)
    cmds.rotate(0,0,0, _controlName, absolute = True, os = True)
    cmds.move(0,0,0, _controlName, absolute = True, os = True)
    if parentObject:
        cmds.parent(_jointName+"|"+_controlName, parentObject)
    else:
        cmds.parent(_jointName+"|"+_controlName, world=True)
    
#a method to change the extension of the name
#for the inputted extension

def changeExt (_name, _newExt):
    index =  _name.rfind("_")
    _output = _name[:index]
    _output = _output+_newExt
    return _output


# Make circle into a gimbal shape
def gimbalShape(_circle, _scale):
    cvList = []
    for i in range(1, 8, 2):
        cvList.append("%s.cv[%d]" %(_circle, i))
    cmds.scale(_scale, _scale, _scale, cvList)

def getDistBetween(_object1, _object2):
    return getDist(
                cmds.xform(_object1, t=1, q=1, ws=1),
                cmds.xform(_object2, t=1, q=1, ws=1)
                )

# Weighted parent
def getDist(_pos1, _pos2):
    return math.sqrt(((_pos1[0] - _pos2[0])**2) + ((_pos1[1] - _pos2[1])**2) + ((_pos1[2] - _pos2[2])**2)) 

def getWeighting(_first, _current, _second, _sqr = True):
    firstDist = getDist(_first, _current) 
    secondDist = getDist(_second, _current)
    if _sqr:
        firstDist = firstDist**2
        secondDist = secondDist**2
    return firstDist / (firstDist + secondDist)
    
def applyWeightedConstraint(
        _startObj,
        _currentObj,
        _endObj,
        _constraint=cmds.parentConstraint
        ):
    startPos = cmds.xform(_startObj, t=1, q=1, ws=1)
    currentPos = cmds.xform(_currentObj, t=1, q=1, ws=1)
    endPos = cmds.xform(_endObj, t=1, q=1, ws=1)
    weight = getWeighting(startPos, currentPos, endPos, False)
    _constraint(_startObj, _currentObj, w=1 - weight, mo=1)
    const = _constraint(_endObj, _currentObj, w=weight, mo=1)
    return const[0]

# Create 1 - _attr and return attribute
def create1MinusNode(_attr, _nodeName):
    #-- create 1-blend node --#
    oppBlend = cmds.createNode("plusMinusAverage", n=_nodeName)
    #cheat to get constant value
    constant1 = cmds.createNode("addDoubleLinear", n=_nodeName+"_CONSTFIX")
    constant1Attr = constant1 + ".input1"
    cmds.setAttr(constant1Attr, 1)
    cmds.setAttr(oppBlend+".operation", 2)
    cmds.connectAttr(constant1Attr, oppBlend + ".input1D[0]")
    cmds.connectAttr(_attr, oppBlend + ".input1D[1]")
    return oppBlend + ".output1D"

def lockAttrs(_object, _attrs, _lock = True, _hide = False):
    for attr in _attrs:
        if _lock:
            cmds.setAttr("%s.%s" %(_object, attr), lock = True)
        if _hide:
            cmds.setAttr("%s.%s" %(_object, attr), keyable = False, cb=False)

def stripAttr(_object, _attr):
    try:
        cmds.deleteAttr("%s.%s" %(_object, _attr))
    except:
        pass
        #print "Couldn't delete attribute %s.%s" %(_object, _attr)

def setMultiAttrs(_object, _attrs, _value):
    for attr in _attrs:
        cmds.setAttr("%s.%s" %(_object, attr), _value)

def copyTranslation(_destination, _source):
    worldTranslation = cmds.xform(_source, q=1, t=1, ws=1)
    cmds.xform(_destination, t=worldTranslation, ws=1)

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
    newShape = cmds.listRelatives(_new, s=1, f=1)
    oldShape = cmds.listRelatives(_old, s=1, f=1)
    cmds.parent(newShape, _old, s=1, r=1)
    #Clean up
    cmds.delete(oldShape)
    cmds.delete(_new)
    cmds.delete(tmpGroup)

def reorientRecursive(_topJoint, _up, _upVec=(0, 0, 1), _aimVec=(1, 0, 0)):
    children = cmds.listRelatives(_topJoint, children=True)
    # If it's the end 
    if children == None:
        newAim = (_aimVec[0]*-1, _aimVec[1]*-1, _aimVec[2]*-1)
        parentJoint = cmds.listRelatives(_topJoint, p=True)[0]
        constraint = cmds.aimConstraint(
            parentJoint, 
            _topJoint,
            wut="object",
            wuo=_up,
            aim=newAim,
            u=_upVec
            )
        cmds.delete(constraint)
        cmds.makeIdentity(_topJoint, apply=True, r=True)
        return 0
    child = children[0]
    depth = reorientRecursive(child, _up, _upVec, _aimVec)
    
    # 1. unparent child
    cmds.parent(child, world=True)
    
    # 2. orient joint
    
    constraint = cmds.aimConstraint(
        child,
        _topJoint,
        wut="object",
        wuo=_up,
        aim=_aimVec,
        u=_upVec
        )
        
    cmds.delete(constraint)
    cmds.makeIdentity(_topJoint, apply=True, r=True)
    # 3. reparent joint
    cmds.parent(child, _topJoint)
    return depth

def reorientJoints(_joints, _up=False, _upVec=(0, 0, 1),  _aimVec=(1, 0, 0)):
    for topJoint in _joints:
        # Clean translations
        cmds.joint(topJoint, edit=True, oj="xyz", sao="zup", ch=True, zso=True) 
        if _up:
            # Clean rotations
            reorientRecursive(topJoint, _up, _upVec, _aimVec)

