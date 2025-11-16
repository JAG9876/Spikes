'''
Shows that two locations with different latitude, when globe is tilted;
    - the locations have a different delta time between each other during sunrise than during sunset.
'''

import pybullet as p
import pybullet_data
import time

physicsClient = p.connect(p.GUI)

p.setAdditionalSearchPath(pybullet_data.getDataPath())
planeId = p.loadURDF("plane.urdf")

p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1) # Enable shadows for better visualization of lighting
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0) # Disable the GUI for a cleaner view
p.configureDebugVisualizer(rgbBackground=[0,0,0], shadowMapIntensity=1, lightPosition=[1, 0, -0.2])
#p.resetDebugVisualizerCamera(cameraDistance=3, cameraYaw=0, cameraPitch=-30, cameraTargetPosition=[0,0,0])

startPos = [0, 0, 1]
globeTilt = 0  # -6.283*23./360.
startOrientation = p.getQuaternionFromEuler([0, globeTilt, 0])
globe = p.loadURDF("sun-rise-set\\my-sphere.urdf", startPos, startOrientation)

for i in range(10000):
    # Spin the globe around the Z-axis
    angle = i * 0.001
    newOrientation = p.getQuaternionFromEuler([0, globeTilt, angle])
    p.resetBasePositionAndOrientation(globe, startPos, newOrientation)
    
    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()
