import pybullet as p
import pybullet_data
import time

physicsClient = p.connect(p.GUI)

p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
planeId = p.loadURDF("plane.urdf")

startPos = [0, 0, 1]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
robot = p.loadURDF("r2d2.urdf", startPos, startOrientation)


for i in range(1000):
    # Spin the robot around the Z-axis
    angle = i * 0.01
    newOrientation = p.getQuaternionFromEuler([0, 0, angle])
    p.resetBasePositionAndOrientation(robot, startPos, newOrientation)
    
    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()
