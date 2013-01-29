# BIND arm rig class

import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
import ArmJoints as aj
import StretchChain as chain
reload(chain)
reload(rc)
reload(rg)
reload(aj)

class BINDArmRig:
    def __init__(
            self, 
            _joints,
            _name,
            _controlObject,
            _numUpperControls,
            _numLowerControls,
            _numUpperJoints,
            _numLowerJoints,
            _upperStretchJoint,
            _lowerStretchJoint,
            _isMirrored=False,
            _twistAxis = "y",
            _rigWrist = True,
            ):
        self.m_isMirrored = _isMirrored
        self.m_joints = aj.ArmJoints(_joints)
        self.m_name = _name
        self.m_controlObject = _controlObject
        self.m_twistAxis = _twistAxis
        self.m_rigWrist = _rigWrist
        tmp = rg.stripMiddle(self.m_joints.m_shoulder, 0, 3)
        self.m_group = self.m_name+"_GRP"
        self.m_group = cmds.group(n=self.m_group, em=1)
        cmds.parent(self.m_joints.m_shoulder, self.m_group, r=1)
        #Add transform group
        self.m_mainTransform = rg.addGroup(
            self.m_joints.m_shoulder, 
            "%s_0" %(self.m_joints.m_shoulder)
            )
        self.m_isGenerated = False

        # stretch chain parameters
        self.m_numUpperControls = _numUpperControls
        self.m_numLowerControls = _numLowerControls
        self.m_numUpperJoints = _numUpperJoints
        self.m_numLowerJoints = _numLowerJoints
        self.m_upperStretchJoints = _upperStretchJoint
        self.m_lowerStretchJoints = _lowerStretchJoint
        
    def generate(self):
        cmds.cycleCheck(e=False)
        if self.m_rigWrist:
            self.rigWrist()
        self.setupStretch()
        if self.m_rigWrist:
            self.aimWrist()
        cmds.cycleCheck(e=True)
        self.m_isGenerated = True

    def getEndJoint(self):
        assert self.m_isGenerated, "Rig not generated"
        return self.m_joints.m_wrist

    def getEndTwistParent(self):
        assert self.m_isGenerated, "Rig hasn't been generated"
        twistControl = self.m_lowerStretch.getTwistControls()[1]
        # return the group above the twist
        return cmds.listRelatives(twistControl, p=1)[0]
        
        
    def getMainTransform(self):
        return self.m_mainTransform
    
    def getTwistControls(self):
        assert self.m_isGenerated, "Rig not generated"
        return [
            self.m_upperStretch.getTwistControls(),
            self.m_lowerStretch.getTwistControls()
            ]

    def rigWrist(self):
        gimbalCtrls = rc.makeGimbalCTRL(self.m_joints.m_wrist, False, False)
        self.m_wristCtrl = gimbalCtrls[1]
        self.m_wristGBLCtrl = gimbalCtrls[0]
        #Lock controls
        for control in [self.m_wristCtrl, self.m_wristGBLCtrl]:
            cmds.setAttr(control+".translate", l=1)
            cmds.setAttr(control+".scale", l=1)
        
        cmds.parent(self.m_wristCtrl+"_0", self.m_group)
        cmds.pointConstraint(self.m_joints.m_wrist, self.m_wristCtrl+"_CONST")
        cmds.orientConstraint(
            self.m_wristGBLCtrl, 
            self.m_joints.m_wrist, 
            mo=True
            )
        # Move and parent blend control
        rc.orientControl(self.m_controlObject, self.m_wristCtrl)
        group = rg.addGroup(self.m_controlObject, "%s_0" %(self.m_controlObject))
        moveValue = -2
        if self.m_isMirrored:
            moveValue *= -1
        cmds.setAttr("%s.t%s" %(self.m_controlObject, self.m_twistAxis), moveValue)
        cmds.parentConstraint(self.m_wristCtrl, group, mo=1)
        rc.lockAttrs(
            self.m_controlObject, 
            [
                "tx", 
                "ty",
                "tz", 
                "rx", 
                "ry", 
                "rz", 
                "sx", 
                "sy", 
                "sz", 
                "visibility"
            ],
            True,
            True
            )
        
    def setupStretch(self):
       #Create the bendy bits 
        self.m_upperStretch = chain.StretchChain(
            self.m_joints.m_shoulder, 
            self.m_joints.m_elbow1, 
            self.m_name+"_upperStretch", 
            self.m_numLowerControls, 
            self.m_numUpperJoints
            )
        self.m_upperStretch.setMirroring(self.m_isMirrored)
        self.m_upperStretch.setBendFromParent(False)
        self.m_upperStretch.setBlendControl(self.m_controlObject)
        self.m_upperStretch.setBlendAttrName("upperBend") 
        self.m_upperStretch.setSquetchAttrName("upperSquetchiness")
        self.m_upperStretch.setSquetchBoolAttrName("upperSquetchOnOff")
        self.m_upperStretch.setAttrHeading("UPPER")
        self.m_upperStretch.setTwistAxis(self.m_twistAxis)
        self.m_upperStretch.setBindJoints(self.m_upperStretchJoints)
        self.m_upperArmGRP = self.m_upperStretch.generate()
        cmds.parent(self.m_upperArmGRP, self.m_group)
 
        self.m_lowerStretch = chain.StretchChain(
            self.m_joints.m_elbow2, 
            self.m_joints.m_wrist, 
            self.m_name+"_lowerStretch",
            self.m_numLowerControls, 
            self.m_numLowerJoints
            )
        self.m_lowerStretch.setMirroring(self.m_isMirrored)
        self.m_lowerStretch.setBlendControl(self.m_controlObject)
        self.m_lowerStretch.setBlendAttrName("lowerBend")
        self.m_lowerStretch.setSquetchAttrName("lowerSquetchiness")
        self.m_lowerStretch.setSquetchBoolAttrName("lowerSquetchOnOff")
        self.m_lowerStretch.setAttrHeading("LOWER")
        self.m_lowerStretch.setTwistAxis(self.m_twistAxis)
        self.m_lowerStretch.setBindJoints(self.m_lowerStretchJoints)
        self.m_lowerArmGRP = self.m_lowerStretch.generate()
        cmds.parent(self.m_lowerArmGRP, self.m_group)
        # parent lower twist
        twistControls = self.m_lowerStretch.getTwistControls()
        cmds.parent(twistControls[0], self.m_upperStretch.getTwistControls()[1])
        # Hide unused twist controls
        for control in twistControls:
            cmds.setAttr("%s.visibility" %(control), 0)

    def aimWrist(self): 
        # Make sure wrist is aimed right
        cmds.aimConstraint(
            self.m_joints.m_elbow2,
            "%s_CONST" %(self.m_wristCtrl),
            worldUpType = "object",
            worldUpObject = self.m_lowerStretch.getTwistControls()[0],
            mo = True
            )
