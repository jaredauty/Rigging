    # IK arm rig class

import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
import VecMath as vec

reload(rc)
reload(rg)
reload(vec)

class StretchChain:
    def __init__(self, _parent1, _parent2, _name, _numCtrls, _numJoints = 5):
        self.m_parent1 = _parent1
        self.m_parent2 = _parent2
        self.m_name = _name
        self.m_group = cmds.group(em=1, n=_name+"_GRP")
        self.m_numCtrls = _numCtrls
        self.m_numJoints = _numJoints
        self.m_isParentBend = True
        self.m_blendControl = False
        self.m_blendAttrName = "autoBend"
        self.m_squetchAttrName = "squetchiness"
        self.m_squetchBoolAttrName = "squetchOnOff"
        self.m_isMirrored = False
        self.m_twistAxis = "y"
        self.m_userJoints = False
        
        #create null for scale fixing
        self.m_scaleNull = cmds.group(em=1, n=_name+"_NULL", w=True)
        cmds.setAttr(self.m_scaleNull+".inheritsTransform", 0)
        cmds.parent(self.m_scaleNull, self.m_group)
        cmds.scaleConstraint(self.m_group, self.m_scaleNull) 

    def setBindJoints(self, _joints):
        self.m_userJoints = _joints

    def setTwistAxis(self, _axis):
        # Make sure the axis is valid
        validAxes = ["x", "y","z"]
        flag = False
        for axis in validAxes:
            if axis == _axis:
                flag = True
                break
        assert flag, "Trying to set invalid twist axis, use 'x', 'y' or 'z'"
        self.m_twistAxis = _axis

    def getTwistAxis(self):
        return self.m_twistAxis

    def setMirroring(self, _isMirrored):
        self.m_isMirrored = _isMirrored

    def getMirroring(self):
        return self.m_isMirrored

    def setBendFromParent(self, _isParentBend):
        self.m_isParentBend = _isParentBend

    def setBlendControl(self, _blendControl):
        self.m_blendControl = _blendControl
    
    def setBlendAttrName(self, _blendAttrName):
        self.m_blendAttrName = _blendAttrName
    
    def setSquetchAttrName(self, _squetchAttrName):
        self.m_squetchAttrName = _squetchAttrName

    def setSquetchBoolAttrName(self, _squetchBoolAttrName):
        self.m_squetchBoolAttrName = _squetchBoolAttrName

    def getTwistControls(self):
        return [self.m_twistControl1, self.m_twistControl2]

    def getEndBindJoint(self):
        return self.m_bindJoints[-1]

    def generate(self):    
        self.createJoints()
        self.createControls()
        self.createIK()
        self.createTwist()
        return self.m_group
    
    def createJoints(self):
        if not self.m_userJoints:
            self.m_bindJoints = []
            startPos = cmds.xform(self.m_parent1, q=1, t=1, ws=1)
            endPos = cmds.xform(self.m_parent2, q=1, t=1, ws=1)
            stepVec = vec.divide(
                vec.subtract(endPos, startPos), 
                self.m_numJoints - 1
                )
            currentPos = startPos
            for i in range(self.m_numJoints):
                newJoint = self.m_name+"_"+str(i)+"_BIND_JNT"
                newJoint = cmds.joint(n=newJoint, p=currentPos)
                cmds.setAttr("%s.radius" %(newJoint), 0.1)
                self.m_bindJoints.append(newJoint)
                currentPos = vec.add(currentPos, stepVec)
            #fix orientations
            cmds.joint(
                self.m_bindJoints[0], 
                e=1, 
                oj="xyz", 
                sao = "yup", 
                ch=1, 
                zso=1
                )
        else:
            # Duplicate joints and rename
            newJoints = cmds.duplicate(self.m_userJoints[0], rc=1)
            print newJoints
            for i in range(len(newJoints)):
                newJoint = "%s_%d_BIND_JNT" %(self.m_name, i)
                newJoints[i] = cmds.rename(newJoints[i], newJoint)
            self.m_bindJoints = newJoints
        #Put it in the right group
        cmds.parent(self.m_bindJoints[0], self.m_group)

    def createControls(self):
        #If no blend control is speified add one
        if not self.m_blendControl:
            self.m_blendControl = cmds.circle(n=self.m_name+"Blend_CTRL")
            self.m_blendControl = self.m_blendControl[0]
            cmds.parent(self.m_blendControl, self.m_group)
        cmds.addAttr(
            self.m_blendControl, 
            ln=self.m_blendAttrName, 
            k=1, min=0, max=1, dv=0
            )
        blendNodeAttr = self.m_blendControl+"."+self.m_blendAttrName
        oppBlendNodeAttr = rc.create1MinusNode(
            blendNodeAttr, 
            self.m_name+"OppBlend_CTRL" 
            )
        
        self.m_controls = []
        self.m_parentCtrls = []
        self.m_pointCtrls = []
        startPos = cmds.xform(self.m_parent1, q=1, t=1, ws=1)
        endPos = cmds.xform(self.m_parent2, q=1, t=1, ws=1)
        stepVec = vec.divide(
            vec.subtract(endPos, startPos), 
            self.m_numCtrls + 1
            )
        currentPos = vec.add(startPos, stepVec)
        for i in range(self.m_numCtrls):
            newCtrl = self.m_name+"_"+str(i)+"_CTRL"
            parentCtrl = self.m_name+"_"+str(i)+"_parent_CTRL"
            pointCtrl = self.m_name+"_"+str(i)+"_point_CTRL"
            
            newCtrl = cmds.spaceLocator(n=newCtrl)
            newCtrl = newCtrl[0]
            cmds.parent(newCtrl, self.m_group)
            cmds.xform(newCtrl, t=currentPos, ws=1)
            
            parentCtrl = cmds.duplicate(newCtrl, n=parentCtrl)
            parentCtrl = parentCtrl[0]
            cmds.setAttr(parentCtrl+".visibility", 0)
            pointCtrl = cmds.duplicate(newCtrl, n=pointCtrl)
            pointCtrl = pointCtrl[0]
            cmds.setAttr(pointCtrl+".visibility", 0)

            rg.add3Groups(newCtrl, ["_SDK", "_CONST", "_0"])
            
            #Create blend between parent and point setups
            blendConst = cmds.pointConstraint(parentCtrl, newCtrl+"_CONST")
            cmds.connectAttr(blendNodeAttr, blendConst[0]+"."+parentCtrl+"W0")
            blendConst = cmds.pointConstraint(pointCtrl, newCtrl+"_CONST")
            cmds.connectAttr(oppBlendNodeAttr, blendConst[0]+"."+pointCtrl+"W1")
            
            self.m_controls.append(newCtrl)
            self.m_parentCtrls.append(parentCtrl)
            self.m_pointCtrls.append(pointCtrl)
            currentPos = vec.add(currentPos, stepVec)

            grandParent = cmds.listRelatives(self.m_parent1, p=1)
            if grandParent == None or not self.m_isParentBend:
                grandParent = self.m_parent1
            
            parentConst = rc.applyWeightedConstraint(
                grandParent, 
                parentCtrl, 
                self.m_parent2, 
                cmds.parentConstraint
                )
            pointConst = rc.applyWeightedConstraint(
                self.m_parent1, 
                pointCtrl, 
                self.m_parent2, 
                cmds.pointConstraint
                )
            #lock attrs
            cmds.setAttr(newCtrl+".rotate", l=1)
            cmds.setAttr(newCtrl+".scale", l=1)
            
    def createIK(self):
        ikResult = cmds.ikHandle(
           sol = "ikSplineSolver",
           sj=self.m_bindJoints[0], 
           ee=self.m_bindJoints[-1],
           ns=self.m_numCtrls-1, 
           n = self.m_name + "_IK"
           )
        self.m_ikCurve = ikResult[2]
        newCurveName = self.m_name+"_IK_CURVE"
        self.m_ikCurve = cmds.rename(self.m_ikCurve, newCurveName)
        self.m_ikHandle = ikResult[0]
        cmds.parent(self.m_ikHandle, self.m_group)
        cmds.setAttr(self.m_ikHandle+".visibility", 0)
        #Make sure curve does not get double transformed
        cmds.setAttr(self.m_ikCurve+".inheritsTransform", 0)
        self.m_clusters = []
        
        #Create clusters
        for i in range(0, len(self.m_controls)):
            name = self.m_controls[i][:self.m_controls[i].rfind("_")]+\
                "_stretch_CLUSTER"
            self.clusterPoint(
                self.m_ikCurve+".cv["+str(i+1)+"]", 
                self.m_controls[i],
                name
                )
        name = self.m_parent1[:self.m_parent1.rfind("_")]+"_stretch_CLUSTER"
        self.clusterPoint(self.m_ikCurve+".cv[0]", self.m_parent1, name)
        name = self.m_parent2[:self.m_parent2.rfind("_")]+"_stretch_CLUSTER"
        self.clusterPoint(
            self.m_ikCurve+".cv["+str(self.m_numCtrls+2)+"]", 
            self.m_parent2, 
            name
            )
        
        #Do stretch
        self.m_curveInfo = cmds.createNode(
            "curveInfo", 
            n=self.m_name+"_CURVEINFO"
            )
        cmds.connectAttr(
            self.m_ikCurve+".worldSpace", 
            self.m_curveInfo+".inputCurve"
            )
        scaleComp = cmds.createNode(
            "multiplyDivide",
            n=self.m_name+"_IK_scaleComp_MULT"
            )
        cmds.setAttr(scaleComp+".operation", 2)
        cmds.connectAttr(
            self.m_curveInfo+".arcLength", 
            scaleComp+".input1X"
            )
        cmds.connectAttr(self.m_scaleNull+".sx", scaleComp+".input2X")
        normaliseNode = cmds.createNode(
            "multiplyDivide", 
            n=self.m_name+"_normalise_MULT"
            )
        cmds.connectAttr(scaleComp+".outputX", normaliseNode+".input1X")
        cmds.setAttr(normaliseNode+".input2X", self.m_numJoints-1)
        cmds.setAttr(normaliseNode+".operation", 2)
        #Go through and connect up all the joints
        # for jnt in self.m_bindJoints[1:]:
        #     cmds.connectAttr(normaliseNode+".outputX", jnt+".tx")
        #Make sure to rebuild the curve to make it all nice and smooth
        # cmds.rebuildCurve(
        #     self.m_ikCurve,
        #     rebuildType=0,
        #     spans=4,
        #     keepRange=0
        #     )
        # VOLUME RETENTION #
        #Create overall stretch node
        stretchAmount = cmds.createNode(
            "multiplyDivide", 
            n=self.m_name+"_IK_sretchValue_MULT"
            )
        # #---set to division
        cmds.setAttr(stretchAmount+".operation", 2)
        cmds.connectAttr(
            self.m_curveInfo+".arcLength", 
            stretchAmount+".input1X"
            )
        currentLen = cmds.getAttr(self.m_curveInfo+".arcLength")
        cmds.setAttr(stretchAmount+".input2X", currentLen)
        
        # Add squetch control
        cmds.addAttr(
            self.m_blendControl, 
            ln=self.m_squetchAttrName, 
            min=0, 
            dv=1, 
            k=1
            )
        cmds.addAttr(
            self.m_blendControl, 
            ln=self.m_squetchBoolAttrName, 
            k=1, 
            dv=1, 
            at="bool"
            )
        stretchExp =  self.makeStretchExpression(
            self.m_blendControl+"."+self.m_squetchAttrName,
            stretchAmount+".outputX",
            self.m_blendControl+"."+self.m_squetchBoolAttrName
            )
        cmds.expression(n=self.m_name+"_IK_stretch_EXP", s=stretchExp)
    
    def makeStretchExpression(
            self, 
            _stretchScaleAttr, 
            _stretchValueAttr, 
            _squetchBool
            ):
        squetchExp = "if("+_squetchBool+")\n{\n"+\
            "float $strUser = "+_stretchScaleAttr+";\n" +\
            "float $strUserOpp = 1 - $strUser;\n" +\
            "float $strV = 1 / "+_stretchValueAttr+";\n\n"
        centerDist = (len(self.m_bindJoints) - 1) / 2.0
        for i in range(1, (len(self.m_bindJoints) - 1)):
            initialLength = cmds.getAttr("%s.tx" %(self.m_bindJoints[i]))
            scaleOffset = 1.0 / ((abs(centerDist - i) * centerDist) + 0.0001)
            squetchExp = "%s\n%s.tx = %f * %s;\n" %(
                                                    squetchExp, 
                                                    self.m_bindJoints[i],
                                                    initialLength,
                                                    _stretchValueAttr
                                                    )
            squetchExp = squetchExp + "float $scale = clamp(0.001, 1000,"+\
                "$strUserOpp + pow($strV,"+ str(scaleOffset)+")*$strUser);\n"+\
                self.m_bindJoints[i]+".sy = $scale;\n"+\
                self.m_bindJoints[i]+".sz = $scale;\n\n"
        squetchExp = squetchExp + "}\n"
        return squetchExp

    def createTwist(self):
        numJoints = len(self.m_bindJoints)
        if numJoints == 0:
            raise Exception, "No joints, cannot create twist setup"
        
        #Create twist controls
        # Twist 1
        self.m_twistControl1 = cmds.spaceLocator(
            n="%s_upperTwist_CTRL" %(self.m_name)
            )[0]
        cmds.parent(self.m_twistControl1, self.m_parent1, r=1)
        
        # Twist 2
        self.m_twistControl2 = cmds.spaceLocator(
            n="%s_lowerTwist_CTRL" %(self.m_name)
            )[0]
        cmds.parent(self.m_twistControl2, self.m_parent2, r=1)

        for control in [self.m_twistControl1, self.m_twistControl2]: 
            if self.m_isMirrored:
                cmds.setAttr(
                    "%s.t%s" %(control, self.m_twistAxis),
                    1
                    )
            else:
                cmds.setAttr(
                    "%s.t%s" %(control, self.m_twistAxis),
                    -1
                    )
            rg.addSingleGroup([control], "_0")
            rc.lockAttrs(
                control,
                ["rotate", "scale"],
                True,
                False
                )

        cmds.setAttr("%s.dTwistControlEnable" %(self.m_ikHandle), 1)
        cmds.setAttr("%s.dWorldUpType" %(self.m_ikHandle), 2)
        cmds.setAttr("%s.dTwistValueType" %(self.m_ikHandle), 1)

        if self.m_twistAxis == "y":
            if self.m_isMirrored:
                cmds.setAttr("%s.dWorldUpAxis" %(self.m_ikHandle), 0)
            else:
                cmds.setAttr("%s.dWorldUpAxis" %(self.m_ikHandle), 1)
        else:
            if self.m_isMirrored:
                cmds.setAttr("%s.dWorldUpAxis" %(self.m_ikHandle), 3)
            else:
                cmds.setAttr("%s.dWorldUpAxis" %(self.m_ikHandle), 4)
        

        cmds.connectAttr(
            "%s.worldMatrix[0]" %(self.m_twistControl1),
            "%s.dWorldUpMatrix" %(self.m_ikHandle),
            f = True
            )
        cmds.connectAttr(
            "%s.worldMatrix[0]" %(self.m_twistControl2),
            "%s.dWorldUpMatrixEnd" %(self.m_ikHandle),
            f = True
            )
        
    def clusterPoint(self, _point, _control, _name):
        #pos = cmds.xform(_control, t=1, q=1, ws=1)
        #cmds.xform(_point, t=pos, ws=1)
        clusterResult = cmds.cluster(_point, n=_name)
        cmds.setAttr(clusterResult[1]+".visibility", 0)
        cmds.parent(clusterResult[1], _control)
        return clusterResult[1]
 
