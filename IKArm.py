# IK arm rig class

import maya.cmds as cmds
import math
import RiggingControls as rc
import RiggingGroups as rg
import ArmJoints as aj
reload(rc)
reload(aj)

class IKArmRig:
    def __init__(self, _sceneData, _joints, _name, _baseName, _isMirrored=False, _twistAxis="y"):
        self.m_sceneData = _sceneData
        self.m_joints = aj.ArmJoints(_joints)
        self.m_name = _name
        self.m_baseName = _baseName
        tmp = rg.stripMiddle(self.m_joints.m_shoulder, 0, 3)
        self.m_group = _name+"_GRP"
        self.m_group = cmds.group(n=self.m_group, em=1)
        cmds.parent(self.m_joints.m_shoulder, self.m_group, r=1)
        self.m_poleVecPinAttr = "polePin"
        self.m_maxStretchAttr = "maxStretchOffset"
        self.m_isMirrored = False
        self.m_twistAxis = _twistAxis
        self.m_allControls = {}
        self.m_isGenerated = False
        
    def generate(self):
       cmds.cycleCheck(e=False)
       self.rigWrist()
       self.setupIK()
       self.setupStretch()
       cmds.cycleCheck(e=True)
       self.m_isGenerated = True

    def getAllControls(self):
        return self.m_allControls

    def getIKControl(self):
        assert self.m_isGenerated, "Rig not generated"
        return self.m_wristCtrl

    def setPoleVecPinAttr(self, _attr):
        self.m_poleVecPinAttr = _attr

    def setMaxStretchAttr(self, _attr):
        self.m_maxStretchAttr = _attr

    def getMainTransform(self):
        return "%s_0" %(self.m_shoulderCtrl)
        
    def rigWrist(self):
        self.m_wristCtrl = rg.stripMiddle(self.m_joints.m_wrist, 0, 1)+"_CTRL"
        self.m_wristCtrl = cmds.spaceLocator(n = self.m_wristCtrl)[0]
        rc.orientControl(self.m_wristCtrl, self.m_joints.m_wrist)
        rg.add3Groups(self.m_wristCtrl, ["_SDK", "_CONST", "_0"])
        cmds.parent(self.m_wristCtrl+"_0", self.m_group, r=1)
        # Add to controls
        rc.addToControlDict(self.m_allControls, "%s_IKWrist" %(self.m_baseName), self.m_wristCtrl)
        rc.addToLayer(self.m_sceneData, "mainCtrl", self.m_wristCtrl)
        
    def setupIK(self):
        #Create shoulder 
        self.m_shoulderCtrl = cmds.spaceLocator(
            n=self.m_joints.m_shoulder.replace("_JNT", "_LOC")
            )[0]
        # Add to controls
        rc.addToControlDict(self.m_allControls, "%s_IKShoulder" %(self.m_baseName), self.m_shoulderCtrl)
        rc.addToLayer(self.m_sceneData, "hidden", self.m_shoulderCtrl)
        rc.orientControl(self.m_shoulderCtrl, self.m_joints.m_shoulder)
        rg.add3Groups(self.m_shoulderCtrl, ["_SDK", "_CONST", "_0"])
        cmds.parent(self.m_shoulderCtrl+"_0", self.m_group, r=1)
        cmds.pointConstraint(
            self.m_shoulderCtrl, 
            self.m_joints.m_shoulder, 
            mo=1
            )
        desiredName = self.m_wristCtrl.replace("_CTRL", "_IK")
        self.m_ikHandle = cmds.ikHandle(
            n = desiredName, 
            sj = self.m_joints.m_shoulder, 
            ee = self.m_joints.m_wrist, 
            sol = "ikRPsolver", 
            see = True
            )[0]
        # deselect so we don't get errors
        cmds.select(d=1)
        rc.addToLayer(self.m_sceneData, "hidden", [self.m_ikHandle])
        cmds.parent(self.m_ikHandle, self.m_wristCtrl)
        self.setupPoleVec()
        
    def setupPoleVec(self):
        middleName = rg.stripMiddle(self.m_joints.m_shoulder, 0, 3)
        desiredName = self.m_name+"PoleVec_LOC"
        self.m_poleVec = cmds.spaceLocator(n = desiredName)[0]
        # Add to controls
        rc.addToControlDict(self.m_allControls, "%s_IKPoleVec" %(self.m_baseName), self.m_poleVec)
        rc.addToLayer(self.m_sceneData, "mainCtrl", self.m_poleVec)
        cmds.addAttr(
            self.m_poleVec, 
            ln=self.m_poleVecPinAttr, 
            min=0, 
            max=1, 
            k=True, 
            dv=0
            )
        cmds.addAttr(
            self.m_poleVec, 
            ln=self.m_maxStretchAttr, 
            at = "float", 
            min=0, 
            dv=10, 
            k=1
            )
        self.m_maxStretch = "%s.%s" %(self.m_poleVec, self.m_maxStretchAttr)
        rc.orientControl(self.m_poleVec, self.m_joints.m_elbow1)
        groups = rg.add3Groups(self.m_poleVec, ["_SDK", "_CONST", "_0"])
        cmds.poleVectorConstraint(self.m_poleVec, self.m_ikHandle)
        cmds.parent(groups[-1], self.m_group, r=1)
        # Lock unused attributes
        rc.lockAttrs(
            self.m_poleVec,
            ["scale", "rotate"],
            True,
            False
            )


        axis , offset = self.getPoleVecAxis(2)
        if axis != "":
            cmds.setAttr("%s.t%s" %(groups[1], axis), offset) 

        #Create line
        midGroup = cmds.group(em=1, n=self.m_name+"PoleVec_GRP")
        cmds.parent(midGroup, self.m_group)
        cmds.pointConstraint(self.m_joints.m_elbow1, midGroup)
        cmds.pointConstraint(self.m_joints.m_elbow2, midGroup)
        lineNodes = rc.createLine([self.m_poleVec, midGroup], self.m_sceneData, "mainCtrl")
        cmds.parent(lineNodes[0], self.m_group)

    def createAngleNode(self, _locator1, _locator2, _locator3):
        # Should probably check here to make sure that the locators
        # are locators and are shapes rather than transforms

        # Create subtraction node to convert positions to vectors
        subNode = ["", ""]
        for i in range(len(subNode)):
            subNode[i] = cmds.createNode(
                "plusMinusAverage",
                n="%s_stretchAngle_%d_SUB" %(self.m_name, i+1)
                )
            # set node to subtract
            cmds.setAttr("%s.operation" %(subNode[i]), 2)
        #   First
        cmds.connectAttr(
            "%s.worldPosition[0]" %(_locator1),
            "%s.input3D[1]" %(subNode[0])
            )
        #   Mid 
        cmds.connectAttr(
            "%s.worldPosition[0]" %(_locator2),
            "%s.input3D[0]" %(subNode[0])
            )
        cmds.connectAttr(
            "%s.worldPosition[0]" %(_locator2),
            "%s.input3D[0]" %(subNode[1])
            )
        #   Last
        cmds.connectAttr(
            "%s.worldPosition[0]" %(_locator3),
            "%s.input3D[1]" %(subNode[1])
            )
        # Create angle node
        stretchAngleNode = cmds.createNode(
            "angleBetween",
            n = "%s_stetchAngle_ANGLE" %(self.m_name)
            )
        for i in [0, 1]:
            cmds.connectAttr(
                "%s.output3D" %(subNode[i]),
                "%s.vector%d" %(stretchAngleNode, i+1)
                )
        return "%s.angle" %(stretchAngleNode)

    def createStretchExp(self, _mainDist, _topDist, _botDist, _angleAttr):
        exp = "// Expression to manage joint lengths for ik system\n"
        # Get initial values
        topJointInit = cmds.getAttr("%s.tx" %(self.m_joints.m_elbow1))
        botJointInit = cmds.getAttr("%s.tx" %(self.m_joints.m_wrist))
        midJointInit = cmds.getAttr("%s.tx" %(self.m_joints.m_elbow2))
        mainDistInit = cmds.getAttr("%s.distance" %(_mainDist))

        # blend attribute
        exp = "%sfloat $blendAttr = %s.%s;\n" %(
            exp, 
            self.m_poleVec, 
            self.m_poleVecPinAttr
            )
        exp = "%sfloat $blendAttrOpp = 1 - $blendAttr;\n" %(exp)
        exp = "%sfloat $theta = %s / 57.296;\n" %(exp, _angleAttr)
        exp = "%s\n//Mid offset\n" %(exp)
        exp = "%sfloat $sinTheta = sin($theta / 2.0);\n" %(exp)
        exp = "%sfloat $midOffset = 0;\n" %(exp)
        exp = "%s\nif ($sinTheta != 0)\n" %(exp)
        exp = "%s{\n$midOffset = (%f / (2.0 * $sinTheta));\n}\n"%(exp, midJointInit)
        exp = "%selse\n{\n$midOffset = %f / 2.0;\n}\n" %(exp, midJointInit)
        exp = "%s\n// Stretch values\n" %(exp)
        exp = "%sfloat $mainStretch = clamp(%f, %f + %s, %s) / %f;\n" %(exp, mainDistInit, mainDistInit, "%s.%s" %(self.m_poleVec, self.m_maxStretchAttr), "%s.distance" %(_mainDist),  mainDistInit)
        exp = "%sfloat $topPinStretch = %s.distance - $midOffset;\n" %(exp, _topDist)
        exp = "%sfloat $botPinStretch = %s.distance - $midOffset;\n" %(exp, _botDist)
        exp = "%s\n// Top Joint\n" %(exp)
        exp = "%s%s.tx = ($blendAttrOpp * $mainStretch * %f) + ($topPinStretch * $blendAttr);\n" %(exp, self.m_joints.m_elbow1, topJointInit)
        exp = "%s\n// Bottom Joint\n" %(exp)
        exp = "%s%s.tx = ($blendAttrOpp * $mainStretch * %f) + ($botPinStretch * $blendAttr);\n" %(exp, self.m_joints.m_wrist, botJointInit)
        return exp
    
    def setupStretch(self):
        # Create nodes to get locator positions
        topDecomp = cmds.createNode(
            "decomposeMatrix", 
            n=self.m_name+"_posMatTop_NODE"
            )
        bottomDecomp = cmds.createNode(
            "decomposeMatrix", 
            n=self.m_name+"_posMatBottom_NODE"
            )
        middleDecomp = cmds.createNode(
            "decomposeMatrix",
            n="%s_posMatMid_NODE" %(self.m_name)
            )
        cmds.connectAttr(
            self.m_shoulderCtrl+".worldMatrix", 
            topDecomp+".inputMatrix"
            )
        cmds.connectAttr(
            self.m_wristCtrl+".worldMatrix", 
            bottomDecomp+".inputMatrix"
            )
        cmds.connectAttr(
            self.m_poleVec+".worldMatrix", 
            middleDecomp+".inputMatrix"
            )
        #Create distance nodes
        distTotal = cmds.createNode(
            "distanceDimShape", 
            n=self.m_name+"_StretchMain_DIST"
            )

        distTop = cmds.createNode(
            "distanceDimShape", 
            n=self.m_name+"_StretchTop_DIST"
            )
        distBottom = cmds.createNode(
            "distanceDimShape", 
            n=self.m_name+"_StretchBottom_DIST"
            )
        # Connect distance nodes to locator positions
        #   main
        cmds.connectAttr(topDecomp+".outputTranslate", distTotal+".startPoint")
        cmds.connectAttr(bottomDecomp+".outputTranslate", distTotal+".endPoint")
        #   top
        cmds.connectAttr(
            "%s.outputTranslate" %(topDecomp),
            "%s.startPoint" %(distTop)
            )
        cmds.connectAttr(
            "%s.outputTranslate" %(middleDecomp),
            "%s.endPoint" %(distTop)
            )
        #   bottom
        cmds.connectAttr(
            "%s.outputTranslate" %(middleDecomp),
            "%s.startPoint" %(distBottom)
            )
        cmds.connectAttr(
            "%s.outputTranslate" %(bottomDecomp),
            "%s.endPoint" %(distBottom)
            )

        #Neaten up dist nodes
        distNodes = [distTotal, distTop, distBottom]
        for node in distNodes:
            distParent = cmds.listRelatives(node, p=1)
            distParent = distParent[0]
            cmds.parent(distParent, self.m_group) 
        rc.addToLayer(self.m_sceneData, "hidden", distNodes)

        #Create angle nodes
        angleAttr = self.createAngleNode(
            cmds.listRelatives(self.m_shoulderCtrl, s=1)[0], 
            cmds.listRelatives(self.m_poleVec, s=1)[0], 
            cmds.listRelatives(self.m_wristCtrl, s=1)[0]
            )
        exp = self.createStretchExp(distTotal, distTop, distBottom, angleAttr)
        cmds.expression(n="%s_stretch_EXP" %(self.m_name), s=exp)


    def getTotalLength(self):
        length = 0
        joints =  self.m_joints.getJointList()
        for jnt in joints[1:]:
            length += math.fabs(cmds.getAttr(jnt+".tx"))
        return length

    def getPoleVecAxis(self, _offsetDist, _tolerance=0.01):
        yValue = cmds.getAttr("%s.jointOrientY" %(self.m_joints.m_elbow1))
        zValue = cmds.getAttr("%s.jointOrientZ" %(self.m_joints.m_elbow1))
        
        yAbs = math.fabs(yValue)
        zAbs = math.fabs(zValue)

        # if there are rotations on both y and z
        # Don't know what to do so leave
        if yAbs > _tolerance and zAbs > _tolerance:
            # don't do anything
            return "", 0

        # If there are not rotations don't know what
        # to do so just leave
        if yAbs < _tolerance and zAbs < _tolerance:
            # do nothting
            return "", 0

        mirror = 1
        if self.m_isMirrored:
            mirror = -1
        # If there are rotations only on y
        if yAbs > _tolerance:
            if yValue > 0:
                return "z", _offsetDist * mirror * -1
            else:
                return "z", _offsetDist * mirror
            
        # If there are rotations only on z
        if zAbs > _tolerance:
            if yValue > 0:
                return "y", _offsetDist * mirror * -1
            else:
                return "y", _offsetDist * mirror
