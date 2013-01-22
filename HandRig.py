"""
A script that takes in a list of joints representing the hand and then creates
a control rig for the hand.
"""

import maya.cmds as cmds
import FingerRig as fing
import RiggingControls as rc
import RiggingGroups as rg
reload(fing)
reload(rc)
reload(rg)

class HandRig:
    def __init__(
            self,
            _name,
            _joints
            ):
        self.m_name = _name
        self.m_group = cmds.group(n="%s_GRP" %(self.m_name), em=True)
        self.m_handJoints = HandJoints(_joints)

    def generate(self):
        self.m_fingers = []
        names = ["indexFing", "middleFing", "ringFing", "pinkyFing", "thumb"]
        for i in range(len(names)):
            thumb = False
            if i == (len(names) - 1):
                thumb = True
            newFinger = fing.FingerRig(
                "%s_%s" %(self.m_name, names[i]),
                self.m_handJoints.getFinger(i),
                thumb
                )
            newFinger.generate()
            cmds.parent(newFinger.getGroup(), self.m_group)
            self.m_fingers.append(newFinger)

        #create control
        self.m_control = cmds.spaceLocator(n="%s_CTRL" %(self.m_name))[0]


        rc.orientControl(self.m_control, self.m_fingers[3].getKnuckle())
        group = rg.addGroup(self.m_control, "%s_0" %(self.m_control))
        rc.lockAttrs(self.m_control, ["tx", "rotate", "scale"], True, False)
        cmds.parent(group, self.m_group)
        cmds.expression(n="%s_EXP" %(self.m_name), s=self.createExp())

    def createExp(self):
        length = self.m_fingers[0].getUpperLength()
        exp = "float $dispZ = %s.translateZ;\n \
        float $dispY = %s.translateY;\n \
        float $len = %f;\n \
        float $angleY = asind(clamp(-1.0, 1.0, ($dispZ*-1) / $len)) / 2;\n \
        float $angleZ = asind(clamp(-1.0, 1.0, ($dispY) / $len)) / 2;\n \
        float $squashOffset = 0;\n \
        if($dispY > 0)\n \
        {\n \
        $squashOffset = $angleZ * 0.5;\n \
        }\n \
        %s.rotateY = $angleY;\n \
        %s.rotateY = $angleY * 0.5 + $squashOffset;\n \
        %s.rotateY = $angleY * 0.125 + $squashOffset;\n \
        %s.rotateZ = $angleZ;\n \
        %s.rotateZ = $angleZ * 0.5;\n \
        %s.rotateZ = $angleZ * 0.125;" %(
            self.m_control,
            self.m_control,
            length,
            self.m_fingers[3].getUpperSDK(),
            self.m_fingers[2].getUpperSDK(),
            self.m_fingers[1].getUpperSDK(),
            self.m_fingers[3].getUpperSDK(),
            self.m_fingers[2].getUpperSDK(),
            self.m_fingers[1].getUpperSDK()
            )
        return exp



"""
Class to manage all the joints for the hand. Basically treated like a struct
"""
class HandJoints:
    def __init__(self, _joints):
        assert len(_joints) == 24, "Wrong number of joints"
        self.m_indexJoints = _joints[:5]
        self.m_middleJoints = _joints[5:10]
        self.m_ringJoints = _joints[10:15]
        self.m_pinkyJoints = _joints[15:20]
        self.m_thumbJoints = _joints[20:24]

    def getFinger(self, _i):
        assert type(_i) is int, "_i should be an int"
        assert _i >= 0 and _i <= 4, "_i out of range"
        if _i == 0:
            return self.m_indexJoints
        if _i == 1:
            return self.m_middleJoints
        if _i == 2:
            return self.m_ringJoints
        if _i == 3:
            return self.m_pinkyJoints
        if _i == 4:
            return self.m_thumbJoints

    def getThumb(self):
        return self.m_thumbJoints

    def checkJoints(self):
        # We could put error checking in here
        pass
    
