# This is to keep sets of joints together
class ArmJoints:
    def __init__(self, *args):
        argsLen = len(args)
        if argsLen == 4:
            self.m_shoulder = args[0]
            self.m_elbow1 = args[1]
            self.m_elbow2 = args[2]
            self.m_wrist = args[3]
        elif argsLen == 1:
            self.m_shoulder = args[0][0]
            self.m_elbow1 = args[0][1]
            self.m_elbow2 = args[0][2]
            self.m_wrist = args[0][3]
        else:
            #print "Number of args =", len(args)
            print "Failed to create joint object"
            print "WARNING, wrong number of arguments, takes 4 bone names or 1 list of 4 bones"
    def __getitem__(self, index):
        if index == 0:
            return self.m_shoulder
        elif index == 1:
            return self.m_elbow1
        elif index == 2:
            return self.m_elbow2
        elif index == 3:
            return self.m_wrist
        else:
            print "WARNING, trying to access a joint that doesn't exsist"
    def __len__(self):
        return len(self.getJointList())
    
    def getJointList(self):
        return [self.m_shoulder, self.m_elbow1, self.m_elbow2, self.m_wrist]
    
