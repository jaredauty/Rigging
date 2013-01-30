# FK arm rig class

import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
import ArmJoints as aj
reload(rc)
reload(rg)
reload(aj)

class FKArmRig:
    def __init__(self, _sceneData, _joints, _name):
        self.m_sceneData = _sceneData
        self.m_isShoulder = False
        self.m_isElbow = False
        self.m_isWrist = False
        self.m_joints = aj.ArmJoints(_joints)
        self.m_name = _name
        tmp = self.stripMiddle(self.m_joints.m_shoulder, 0, 3)
        self.m_group = self.m_name+"_GRP"
        self.m_group = cmds.group(n=self.m_group, em=1)
        cmds.parent(self.m_joints.m_shoulder, self.m_group, r=1)
        self.m_allControls = []
        self.m_isGenerated = False
        
    def generate(self):
       cmds.cycleCheck(e=False)
       self.rigShoulder()
       self.rigElbow()
       self.rigWrist()
       #-- Weird fix --#
       cmds.orientConstraint(
            self.m_joints.m_shoulder, 
            self.m_joints.m_wrist, 
            mo=1
            )
       cmds.cycleCheck(e=True)
       self.m_isGenerated = True
       
    def getAllControls(self):
      return self.m_allControls

    def getFKParent(self):
        assert self.m_isGenerated, "Rig not generated"
        return self.m_wristCtrl

    def getMainTransform(self):
        return self.m_shoulderCtrl+"_0"

    def rigShoulder(self):
       try:
           # --- Shoulder --- #
           #Create shoulder controls
           gimbalCtrls = rc.makeGimbalCTRL(
                self.m_joints.m_shoulder, 
                False, 
                True
                )
           self.m_shoulderGBLCtrl = gimbalCtrls[0]
           self.m_shoulderCtrl = gimbalCtrls[1]    
           # Add to controls
           self.m_allControls.append(self.m_shoulderCtrl)
           self.m_allControls.append(self.m_shoulderGBLCtrl)
           rc.addToLayer(self.m_sceneData, "mainCtrl", gimbalCtrls)      
           self.m_isShoulder = True
           cmds.parent(self.m_shoulderCtrl+"_0", self.m_group, r=1)
           cmds.pointConstraint(
                self.m_shoulderGBLCtrl, 
                self.m_joints.m_shoulder
                )
           #Sort out scaling
           cmds.scaleConstraint(
                self.m_shoulderGBLCtrl, 
                self.m_joints.m_shoulder
                )
            
           #Lock unused attributes
           rc.lockAttrs(
                self.m_shoulderCtrl,
                ["translate", "scale"],
                True,
                False
                )
           rc.lockAttrs(
                self.m_shoulderGBLCtrl,
                ["translate", "scale"],
                True,
                False
                )
       except:
           print "WARNING: FK Shoulder setup was unsuccessful!"
           self.m_isShoulder = False
       
    def rigElbow(self):
       #Check that shoulder has been done
       if not self.m_isShoulder:
           self.rigShoulder()
       
       #Rig for stretch
       self.m_stretchCtrl = rc.changeExt(
            self.m_joints.m_elbow1, 
            "_stretch_CTRL"
            )
       self.m_stretchCtrl = cmds.spaceLocator(
            n = self.m_stretchCtrl
            )[0]
       rc.orientControl(self.m_stretchCtrl, self.m_joints.m_shoulder)
       elbowDisplace = cmds.getAttr("%s.tx" %(self.m_joints.m_elbow1))
       groups = rg.add3Groups(self.m_stretchCtrl, ["_SDK", "_CONST", "_0"])
       cmds.parent(groups[2], self.m_shoulderGBLCtrl)
       cmds.setAttr("%s.tx" %(groups[2]), elbowDisplace)
       cmds.pointConstraint(self.m_stretchCtrl, self.m_joints.m_elbow1)

       # --- Elbow --- #
       self.m_elbowCtrl = rc.makeCTRL(
            self.m_joints.m_elbow1, 
            False, 
            True,
            ["_SDK", "_CONST", "_0"]
            )
       cmds.parent(self.m_elbowCtrl+"_0", self.m_stretchCtrl)
       #Connect up double rotations
       try:
           cmds.connectAttr(
                self.m_joints.m_elbow1+".rotate",
                self.m_joints.m_elbow2+".rotate", 
                f=1
                )
       except:
           print "Warning, double joint rotations seem to already be connected"
       
       #- lock and hide unused attributes -#
       rc.lockAttrs(
            self.m_stretchCtrl, 
            ["ty", "tz", "rx", "ry", "rz", "sx",  "sy",  "sz"]
            )

       rc.lockAttrs(
            self.m_elbowCtrl, 
            ["tx", "ty", "tz",  "sx",  "sy",  "sz"]
            )
       rc.addToLayer(self.m_sceneData, "mainCtrl", [self.m_stretchCtrl, self.m_elbowCtrl])
       #Add to controls
       self.m_allControls = self.m_allControls + [self.m_stretchCtrl, self.m_elbowCtrl]
       self.m_isElbow = True


    def rigWrist(self):
       #Check that shoulder has been done
       if not self.m_isElbow:
           self.rigElbow()
       # --- Wrist --- #
       self.m_wristCtrl = rc.makeCTRL(
            self.m_joints.m_wrist, 
            False,
            False,
            ["_SDK", "_CONST", "_0"]
            )
       # Sort orientation
       rc.orientControl(self.m_wristCtrl+"_0", self.m_joints.m_elbow2)
       rc.copyTranslation(self.m_wristCtrl+"_0", self.m_joints.m_wrist)
       #Parent for neatness
       cmds.parent(self.m_wristCtrl+"_0", self.m_elbowCtrl)
       #Connect up to previous joint
       cmds.parentConstraint(
            self.m_joints.m_elbow2,
            self.m_wristCtrl+"_CONST",
            mo=1
            )
       cmds.pointConstraint(
            self.m_wristCtrl,
            self.m_joints.m_wrist,
            skip=["y", "z"]
            )
       rc.lockAttrs(
            self.m_wristCtrl,
            ["ty", "tz", "rotate", "scale"],
            True,
            False
            )
       # Add to controls
       self.m_allControls.append(self.m_wristCtrl)
       rc.addToLayer(self.m_sceneData, "mainCtrl", self.m_wristCtrl)
       self.m_isWrist = True
           
    # Strip everything between underscores number _front and _back
    def stripMiddle(self, _string, _front = 0, _back = 0):
        newString = _string
        for i in range(_front):
            newString = newString[newString.find("_")+1:]
        for i in range(_back):
            newString = newString[:newString.rfind("_")]
        return newString
