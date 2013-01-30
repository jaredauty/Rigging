#Rig Arm
"""
This script should take in a collection of joints, that represent an arm and 
set up a default rig for them
"""
import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
import FKArm as fk
import IKArm as ik
import BINDArm as bind
import ArmJoints as aj
reload(rc)
reload(rg)
reload(fk)
reload(ik)
reload(bind)
reload(aj)

class ArmRig:
    def __init__(
            self,
            _sceneData,
            _joints,
            _name,
            _twistAxis="y",
            _rigWrist=True,
            _blendControl=False
            ):
        self.m_sceneData = _sceneData
        self.m_startJoints = aj.ArmJoints(_joints)
        # Make sure to strip blendParent2 attribute otherwise ik fk blending
        # can break. This sometimes happens if joints are taken from a previous
        # version of the rig and used to generate a new one.
        for joint in self.m_startJoints.getJointList():
            rc.stripAttr(joint, "blendParent2")

        self.m_name = _name
        self.m_group = "%s_GRP" %(self.m_name)
        if not cmds.objExists(self.m_group):
            self.m_group = cmds.group(n=self.m_group, em=True)

        self.m_twistAxis = _twistAxis
        self.m_rigWrist = _rigWrist
        self.m_blendControl = _blendControl
        self.m_isMirrored = self.checkMirroring()
        if not self.m_blendControl:
            self.m_blendControl = cmds.circle(n=self.m_name+"_IKFKBlend_CTRL")[0]
            cmds.parent(self.m_blendControl, self.m_group)
            rc.addToLayer(self.m_sceneData, "mainCtrl", self.m_blendControl)	
        self.m_isGenerated = False
        # stretch chain parameters
        self.m_numUpperControls = 2
        self.m_numLowerControls = 2
        self.m_numUpperJoints = 5
        self.m_numLowerJoints = 5
        self.m_upperStretchJoints = False
        self.m_lowerStretchJoints = False

    def setUpperStretchChain(
            self,
            _numControls,
            _joints,
            _numJoints = 0
            ):
        self.m_numUpperControls = _numControls
        if _joints:
            self.m_upperStretchJoints = _joints
            self.m_numUpperJoints = len(_joints)
        else:
            self.m_numUpperJoints = _numJoints

    def setLowerStretchChain(
            self,
            _numControls,
            _joints,
            _numJoints = 0
            ):
        self.m_numLowerControls = _numControls
        if _joints:
            self.m_lowerStretchJoints = _joints
            self.m_numLowerJoints = len(_joints)
        else:
            self.m_numLowerJoints = _numJoints

    def getVisibilityAttrs(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        return self.m_ikVisibilityAttr, self.m_fkVisibilityAttr

    def getFKParent(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        return self.m_fkRig.getFKParent()

    def getBINDParent(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        return self.m_bindRig.getEndJoint()

    def getTwistControls(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        return self.m_bindRig.getTwistControls()

    def getAnkleTwist(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        return self.m_bindRig.getEndTwistParent()

    def checkMirroring(self):
        return cmds.getAttr("%s.tx" %(self.m_startJoints.m_elbow1)) < 0
    
    def getBlendControl(self):
        return self.m_blendControl

    def getIKControl(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        return self.m_ikRig.getIKControl()

    def generate(self):
        cmds.cycleCheck(e=False)
        # -- Duplicate joints and rename for IK-FK switch --- #
        self.m_bindJoints = self.duplicateJoints(self.m_startJoints, "BIND")
        rc.addToLayer(self.m_sceneData, "ref", self.m_bindJoints[0])
        self.m_ikJoints = self.duplicateJoints(self.m_startJoints, "IK")
        rc.addToLayer(self.m_sceneData, "ref", self.m_ikJoints[0])
        self.m_fkJoints = self.duplicateJoints(self.m_startJoints, "FK")
        rc.addToLayer(self.m_sceneData, "ref", self.m_fkJoints[0])

        # -- Create shoulder locator -- #
        self.m_shoulderLocator = self.m_name+"_shoulder_CTRL"
        self.m_shoulderLocator = cmds.spaceLocator(n=self.m_shoulderLocator)[0]
        rc.addToLayer(self.m_sceneData, "detailCtrl", self.m_shoulderLocator)
        rc.orientControl(self.m_shoulderLocator, self.m_startJoints.m_shoulder)
        shoulderGRPs = rg.add3Groups(
            self.m_shoulderLocator, 
            ["_SDK", "_CONST", "_0"]
            )
        cmds.parent(shoulderGRPs[-1], self.m_group)
        # -- Setup FK rig -- #
        tmpList = self.m_fkJoints.getJointList()
        self.m_fkRig = fk.FKArmRig(self.m_sceneData, tmpList, self.m_name+"_FK")
        self.m_fkRig.generate()
        cmds.parent(self.m_fkRig.m_group, self.m_group)
        cmds.parentConstraint(
            self.m_shoulderLocator, 
            self.m_fkRig.getMainTransform(),
            mo=True
            )
        # -- Setup IK rig -- #
        tmpList = self.m_ikJoints.getJointList()
        self.m_ikRig = ik.IKArmRig(
            self.m_sceneData,
            tmpList, 
            self.m_name+"_IK",
            self.m_isMirrored,
            self.m_twistAxis
            )
        self.m_ikRig.generate()
        cmds.parent(self.m_ikRig.m_group, self.m_group)
        cmds.pointConstraint(
            self.m_shoulderLocator,
            self.m_ikRig.getMainTransform(),
            mo=True
            )
        # -- Setup BIND rig -- #
        tmpList = self.m_bindJoints.getJointList()
        self.m_bindRig = bind.BINDArmRig(
            self.m_sceneData,
            tmpList, 
            self.m_name+"_BIND",
            self.m_blendControl,
            self.m_numUpperControls,
            self.m_numLowerControls,
            self.m_numUpperJoints,
            self.m_numLowerJoints,
            self.m_upperStretchJoints,
            self.m_lowerStretchJoints,
            self.m_isMirrored,
            self.m_twistAxis,
            self.m_rigWrist
            )    
        self.m_bindRig.generate()
        cmds.parent(self.m_bindRig.m_group, self.m_group) 
        cmds.pointConstraint(
            self.m_shoulderLocator,
            self.m_bindRig.getMainTransform(),
            mo=True
            )
        
        # -- Connect up rigs -- #
        try:
            tmp = self.m_blendControl
        except:
            self.m_blendControl = self.createBlendControl()
        self.connectIKFK()
        # -- Setup visibility -- #
        self.setupVisibility()
         
        cmds.cycleCheck(e=True)
        
        self.m_isGenerated = True
        
        
    def setupVisibility(self):
        #Create vis node
        add1 = cmds.createNode(
            "addDoubleLinear", 
            n=self.m_name+"_IK_visNode_ADD"
            )
        add2 = cmds.createNode(
            "addDoubleLinear", 
            n=self.m_name+"_FK_visNode_ADD"
            )
        self.m_ikVisibilityAttr = "%s.output" %(add1)
        self.m_fkVisibilityAttr = "%s.output" %(add2)
        cmds.connectAttr(self.m_blendAttr, add1+".input1")
        cmds.connectAttr(self.m_blendOppAttr, add2+".input1")
        cmds.setAttr(add1+".input2", 0.49)
        cmds.setAttr(add2+".input2", 0.49)
        cmds.connectAttr(
            self.m_ikVisibilityAttr,
            self.m_ikRig.m_group+".visibility"
            )
        cmds.connectAttr(
            self.m_fkVisibilityAttr,
            self.m_fkRig.m_group+".visibility"
            )
        
    def createBlendControl(self):
        blendControl = cmds.circle()
        blendControl = blendControl[0]
        return blendControl

    def stripPostFix(self, _string):
        position = _string.rfind("_")
        return _string[:position]
        
    def duplicateJoints(self, _joints, _postFix):
        newJoints = cmds.duplicate(_joints.m_shoulder, rc=1)
        for i in range(0, len(_joints)):
            jointNameEnd = _joints[i].find("_")
            newName = self.m_name+"_"+_postFix+"_"+\
                _joints[i][:jointNameEnd] + "_JNT"
            newJoints[i] = cmds.rename(newJoints[i], newName)
        return aj.ArmJoints(newJoints)
        
        
    def createBlendAttr(
            self, 
            _name, 
            _attr1, 
            _attr2, 
            _blendAttr, 
            _blendAttrOpp = False
            ):
        # setup first attr
        mult1 = cmds.createNode("multiplyDivide", n=_name+"_MULT")
        cmds.connectAttr(_blendAttr, mult1 + ".input1X")
        cmds.connectAttr(_attr1, mult1 + ".input2X")
        # setup second attr
        mult2 = cmds.createNode("multiplyDivide", n=_name+"Opp_MULT")
        cmds.connectAttr(_blendAttrOpp, mult2 + ".input1X")
        cmds.connectAttr(_attr2, mult2 + ".input2X")
        # blend attrs
        blendNode = cmds.createNode("addDoubleLinear", n=_name+"_Blend_ADD")
        cmds.connectAttr(mult1 + ".outputX", blendNode + ".input1")
        cmds.connectAttr(mult2 + ".outputX", blendNode + ".input2")
        return blendNode + ".output"
        
    def connectIKFK(self):
        blendAttrName = "IK_FK_Blend"
        self.m_blendAttr = self.m_blendControl + "." + blendAttrName
        try:
            cmds.setAttr(self.m_blendAttr, 0)
            print "WARNING, IK_FK_Blend attribute already exsits"
        except:
            cmds.addAttr(
                self.m_blendControl, 
                ln=blendAttrName, 
                min = 0, 
                max = 1, 
                k = 1
                )
        self.m_blendAttr = self.m_blendControl + "." + blendAttrName
        self.m_blendOppAttr = rc.create1MinusNode(
            self.m_blendAttr, 
            self.m_name+"_IKFKBlendOpp_CTRL"
            )
        # Attach each joint to BIND
        bindJoints = self.m_bindRig.m_joints
        ikJoints = self.m_ikRig.m_joints
        fkJoints = self.m_fkRig.m_joints
        for i in range(0, len(bindJoints) - 1):
            #Orientation
            const1 = cmds.parentConstraint(
                ikJoints[i], 
                bindJoints[i],
                st = ["x", "y", "z"]
                )
            const1 = const1[0]
            const2 = cmds.parentConstraint(
                fkJoints[i], 
                bindJoints[i],
                st = ["x", "y", "z"]
                )
            const2 = const2[0]
            cmds.connectAttr(
                self.m_blendOppAttr, 
                "%s.blendParent2" %(bindJoints[i])
                )
            # Set rotation method to quarternion
            #   get pair blend node
            pairBlend = cmds.listConnections(
                "%s.constraintRotateX" %(const1), 
                d=True
                )
            pairBlend = pairBlend[0]
            cmds.setAttr("%s.rotInterpolation" %(pairBlend), 1)

        for i in range(1, len(bindJoints)):
            # Connect up blended lengths
            blendedAttr = self.createBlendAttr(
                rg.stripMiddle(ikJoints[i], 0, 1), 
                ikJoints[i] + ".translateX", 
                fkJoints[i] + ".translateX", 
                self.m_blendAttr, self.m_blendOppAttr
                )
            cmds.connectAttr(blendedAttr, bindJoints[i] + ".translateX")

        # Fix wrist rotations
        self.m_bindRig.aimWrist(self.m_ikRig.getIKControl(), [self.m_blendAttr, self.m_blendOppAttr])




