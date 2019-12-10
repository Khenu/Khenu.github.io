# neferMuscleDeltoidAddPoses.py
# Created by Laushon Neferkara on 9/20/13.
# Copyright (c) 2013 Skin+Bones Modeling and Rigging Company. All rights reserved.


# Add additional twist poses w45 and wn45.
# 1. Delete point constraint and blend shape node
# 2. Create w45 and wn45 pose groups and poses


import pymel.core as pm

class Driver():
	'''Create object to represent driver in scene'''
	def __init__(self, name, data):
		self.name = name
		self.data = data


class SimpleGrp():
	'''Create a group in the Maya scene with the translate, rotate and scale attributes 
	locked and hidden'''
	def __init__(self, name, parent, lockTrans=True):
		self.name = name
		# Test if parent is a object or a string?
		self.parent = parent
		hideList = [
			'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 
			'scaleX', 'scaleY', 'scaleZ']
		# Create the group in the scene
		newGrp = pm.group(em=True, r=True, n=self.name, p=self.parent)
		# Lock and hide the translate, rotate and scale attributes
		if lockTrans:
			for transform in hideList:
				newGrp.attr(transform).set(lock=True, keyable=False, cb=False)
		
	def parentConstraint(self, targetName):
		pm.parentConstraint(targetName, self.name, maintainOffset=False)
	
	def makeInvisible(self):
		pm.setAttr(self.name + '.visibility', False)
		
	def makeVisible(self):
		pm.setAttr(self.name + '.visibility', True)
		

class MuscleControl():
	'''Represents a Maya Muscle control of a neferMuscle.'''
	def __init__(self, muscleName, cIndex, nDriver):	
		self.muscleName = muscleName		
		self.name = 'iControlMidMus_%s%s1' % (muscleName, str(cIndex + 1))
		self.autoGrpName = 'grpiControlMidMus_%s%sAUTO1' % (muscleName, str(cIndex + 1))
		self.nDriver = nDriver
		self.targetList = []
		self.driverList = []
		# Disable jiggle
		mc.setAttr('%s.jiggle' % self.name, 0)

	def addTarget(self, target):
		self.targetList.append(target)
	
	def addDriver(self, driver):
		self.driverList.append(driver)

	def connectTargets(self):
		'Create point constraint to all of the targets'
		pm.pointConstraint(self.targetList, self.name, weight=0.0)

	def connectDriver(self):
		'Connect the Maya Muscle control point constraint to the driver.'
		for pIndex in range(len(self.targetList)):
			pm.connectAttr(
				'%s.%s' % (self.nDriver, self.driverList[pIndex]),
				'%s_pointConstraint1.%sW%s' % (self.name, self.targetList[pIndex], str(pIndex))
				)
							

class MuscleCrossSection():
	'''Represents a Maya Muscle cross section of a neferMuscle.'''
	def __init__(self, muscleName, cIndex, nDriver):	
		self.muscleName = muscleName
		self.name = 'iControlMidMus_%s%s1_crossSectionREST' % (self.muscleName, str(cIndex + 1))
		self.nDriver = nDriver
		self.targetList = []
		self.driverList = []			
		self.blendShape = '%s_blendShape' % self.name

	def addTarget(self, target):
		self.targetList.append(target)
	
	def addDriver(self, driver):
		self.driverList.append(driver)

	def connectTargets(self):
		'Create blend shape node to all of the targets'
		# Create blend shape node with 1st target
		pm.blendShape(self.targetList[0], self.name, name = self.blendShape)
		# Add the remaining targets to the blend shape node
		for bIndex in range(1, len(self.targetList)):
			pm.blendShape(self.blendShape, edit=True, 
				t=(self.name, bIndex, self.targetList[bIndex], 1.0))

	def connectDriver(self):
		'Connect the Maya Muscle control blend shape node to the driver.'
		for pIndex in range(len(self.targetList)):
			pm.connectAttr(
				'%s.%s' % (self.nDriver, self.driverList[pIndex]),
				'%s.%s' % (self.blendShape, self.targetList[pIndex])
				)
							

class SceneTarget():
	'''Represents a target object in Maya.'''
	def __init__(self, name, baseObj, parentGrpName):	
		self.name = name
		self.baseObj = baseObj
		self.parentGrpName = parentGrpName
		
		# Duplicate muscle control
		pm.duplicate(self.baseObj.name, n=self.name)

		# Delete the child squash and stretch curves. (Cross sections do not have.) 
		children = pm.listRelatives(self.name, type='transform', path=True)
		# listRelatives returns a list
		if children:
			pm.delete(children)

		# Unlock transforms for reparenting
		attrList = [
			'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 
			'scaleX', 'scaleY', 'scaleZ']
		for attr in attrList:
			pm.setAttr('%s.%s' % (self.name, attr), lock=False)

		# Make visible
		visibility = '%s.visibility' % self.name
		pm.setAttr(visibility, keyable=True)	
		if pm.connectionInfo(visibility, isDestination=True):
			source = pm.connectionInfo(visibility, sourceFromDestination=True)
			pm.disconnectAttr(source, visibility)

		# Parent to parent grp
		pm.parent(self.name, parentGrpName)

		# Add muscle cross target to muscle controls's target list
		self.baseObj.addTarget(self.name)

class SceneTargetExists():
	'''Represents a target object in Maya.'''
	def __init__(self, name, baseObj, parentGrpName):	
		self.name = name
		self.baseObj = baseObj
		self.parentGrpName = parentGrpName
		
		# Add muscle cross target to muscle controls's target list
		self.baseObj.addTarget(self.name)


class MuscleCtrlTarget(SceneTarget):
	'''Represents a target for a Maya Muscle control.'''
	def __init__(self, name, musCtrl, parentGrpName):	
		SceneTarget.__init__(self, name, musCtrl, parentGrpName)
		# Lock unused transforms
		pm.setAttr('%s.rotate' % self.name, lock=True)
		pm.setAttr('%s.scale' % self.name, lock=True)
		# Make visible
		pm.setAttr('%s.visibility' % self.name, True)

class MuscleCrossTarget(SceneTarget):
	'''Represents a target for a Maya Muscle cross section.'''
	def __init__(self, name, musCross, parentGrpName):	
		SceneTarget.__init__(self, name, musCross, parentGrpName)
		# Lock all transforms
		pm.setAttr('%s.translate' % self.name, lock=True)
		pm.setAttr('%s.rotate' % self.name, lock=True)
		pm.setAttr('%s.scale' % self.name, lock=True)
		# Make visible
		pm.setAttr('%s.visibility' % self.name, True)


class MuscleCtrlTargetExists(SceneTargetExists):
	'''Represents a target for a Maya Muscle control.'''
	def __init__(self, name, musCtrl, parentGrpName):	
		SceneTargetExists.__init__(self, name, musCtrl, parentGrpName)

class MuscleCrossTargetExists(SceneTargetExists):
	'''Represents a target for a Maya Muscle cross section.'''
	def __init__(self, name, musCross, parentGrpName):	
		SceneTargetExists.__init__(self, name, musCross, parentGrpName)


class NeferMuscle():
	'''Represents a neferMuscle: a Maya Muscle that is controlled by a multi-variable
	 pose controller.'''
	def __init__(self, muscleName, driverInfo):
		self.muscleName = muscleName
		self.muscleDriver = driverInfo.name
		self.data = driverInfo.data
		self.getMayaMusInfo()
		self.delTargetConnections()
		# self.setupMayaMus()
		self.createPoses()
		self.connectDriver()
		

	def delTargetConnections(self):
		for cIndex in range(self.numCtrls):
			mc.delete('iControlMidMus_%s%s1_pointConstraint1' % (self.muscleName, str(cIndex + 1)))
			mc.delete('iControlMidMus_%s%s1_crossSectionREST_blendShape' % (self.muscleName, str(cIndex + 1)))

	
	def getMayaMusInfo(self):
		# Calculate the number of controls on the Maya Muscle
		ctrlList = pm.ls('iControlMidMus_%s*1' % self.muscleName, exactType='transform')
		self.numCtrls = len(ctrlList)

		# Create objects to represent the Maya Muscle controls and cross sections and place in list
		self.musCtrls = []
		self.musCross = []
		for cIndex in range(self.numCtrls):
			self.musCtrls.append(MuscleControl(self.muscleName, cIndex, self.muscleDriver))
			self.musCross.append(MuscleCrossSection(self.muscleName, cIndex, self.muscleDriver))

	# def setupMayaMus(self):
	# 	# Set Based On attribute of Maya Muscle to pose
	#   	pm.setAttr('cMuscleCreatorMus_%s1.basedOn' % self.muscleName, 1)	


	def createPoses(self):

		def add2DriverList(driverPt):
			# Add driver to driver list
			for dIndex in range(self.numCtrls):
				self.musCtrls[dIndex].addDriver(driverPt)
				self.musCross[dIndex].addDriver(driverPt)


		def _createCtrlCrossPoses(parentGrpName, driverPt):
			'Create pose groups for each muscle control/cross section pair.'
			for dIndex in range(self.numCtrls):
				ctrlPoseGrp = SimpleGrp(
					parentGrpName.replace('_grp', '_control%s_grp' % str(dIndex + 1)), 
					parentGrpName, 
					False)
				
				# Constrain ctrlPoseGrp to Maya Muscle control AUTO to get auto movement
				ctrlPoseGrp.parentConstraint(self.musCtrls[dIndex].autoGrpName)
				
				# Create control target
				ctrlTargetName = '%s_control%s_%s_target' % (self.muscleName, str(dIndex + 1), driverPt)
				ctrlTarget = MuscleCtrlTarget(ctrlTargetName, self.musCtrls[dIndex], ctrlPoseGrp.name)
				
				# Create cross section target
				crossTargetName = '%s_crossSection%s_%s_target' % (self.muscleName, str(dIndex + 1), 
					driverPt)
				crossTarget = MuscleCrossTarget(crossTargetName, self.musCross[dIndex], ctrlTarget.name)
						
		def _createCtrlCrossPosesExists(parentGrpName, driverPt):
			'Create pose groups for each muscle control/cross section pair.'
			for dIndex in range(self.numCtrls):

				ctrlPoseGrpName = parentGrpName.replace('_grp', '_control%s_grp' % str(dIndex + 1))

				# Create control target
				ctrlTargetName = '%s_control%s_%s_target' % (self.muscleName, str(dIndex + 1), driverPt)
				ctrlTarget = MuscleCtrlTargetExists(ctrlTargetName, self.musCtrls[dIndex], ctrlPoseGrpName)
				
				# Create cross section target
				crossTargetName = '%s_crossSection%s_%s_target' % (self.muscleName, str(dIndex + 1), 
					driverPt)
				crossTarget = MuscleCrossTargetExists(crossTargetName, self.musCross[dIndex], ctrlTargetName)

		# Create the main pose group for the muscle
		# topPoseGrp = 'muscle_pose_grp'		# Already exists in the scene
		# mainPoseGrp = SimpleGrp('%s_pose_grp' % self.muscleName, topPoseGrp)

		# Create the poses within pose groups. Select based on number of axes.
		for pointA in self.data[0]:
			for pointB in self.data[1]:
				for pointC in self.data[2]:
					poseGrpParent = '%s_%s_%s_grp' % (self.muscleName, pointA, pointB)
					poseGrpName = '%s_%s_%s_%s_grp' % (self.muscleName, pointA, pointB, pointC)
					driverPt = '%s_%s_%s' % (pointA, pointB, pointC)
					if not mc.objExists(poseGrpName):
						poseGrpC = SimpleGrp(poseGrpName, poseGrpParent)
						poseGrpC.makeInvisible()
						_createCtrlCrossPoses(poseGrpC.name, driverPt)
					else:
						_createCtrlCrossPosesExists(poseGrpName, driverPt)
					add2DriverList(driverPt)

	
	def connectDriver(self):
		# Connect poses to muscle control and muscle cross sections
		for index in range(self.numCtrls):
			self.musCtrls[index].connectTargets()
			self.musCross[index].connectTargets()
		
		# Connect driver
		for index in range(self.numCtrls):
			self.musCtrls[index].connectDriver()
			self.musCross[index].connectDriver()





def main():

	n3driver = Driver(
		'N3_muscleDriver1', 
		(('x0', 'x45', 'x90', 'x135', 'x180', 'xn45'), 
		('y0', 'y45', 'y90', 'y135', 'y170'), 
		('w0', 'w45', 'w90', 'wn45', 'wn90'))
		)

	# muscle = NeferMuscle('L_deltoidAnteriorA', n3driver)
	# muscle = NeferMuscle('L_deltoidAnteriorB', n3driver)
	# muscle = NeferMuscle('L_deltoidAnteriorC', n3driver)
	# muscle = NeferMuscle('L_deltoidLateralA', n3driver)
	# muscle = NeferMuscle('L_deltoidLateralB', n3driver)
	# muscle = NeferMuscle('L_deltoidLateralC', n3driver)
	# muscle = NeferMuscle('L_deltoidPosteriorA', n3driver)
	# muscle = NeferMuscle('L_deltoidPosteriorB', n3driver)
	# muscle = NeferMuscle('L_deltoidPosteriorC', n3driver)
	muscle = NeferMuscle('L_deltoidPosteriorD', n3driver)

if __name__ == '__main__':
	main()

print '\r\rScript completed successfully. Wait for Channel Box to become active.\r\r'

