
""" Basic class for holding scene data that rigs may need to query"""

class SceneData:
	def __init__(self, _hiddenLyr, _refLyr, _mainCtrlLyr, _detailCtrlLyr):
		self.m_hiddenLyr = _hiddenLyr
		self.m_refLyr = _refLyr
		self.m_mainCtrlLyr = _mainCtrlLyr
		self.m_detailCtrlLyr = _detailCtrlLyr

	def getHidden(self):
		return self.m_hiddenLyr

	def getLayer(self, _layerIdentifier):
		if _layerIdentifier == "hidden":
			return self.m_hiddenLyr
		elif _layerIdentifier == "ref":
			return self.m_refLyr
		elif _layerIdentifier == "mainCtrl":
			return self.m_mainCtrlLyr
		elif _layerIdentifier == "detailCtrl":
			return self.m_detailCtrlLyr
		else:
			assert false, "incorrect layer identifier specified!"