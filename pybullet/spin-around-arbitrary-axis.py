import pybullet as p
import pybullet_data
import numpy as np
import time

# 1. Setup the PyBullet environment
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -10)
planeId = p.loadURDF("plane.urdf")

# Load an object (e.g., a simple cube or r2d2)
startPos = [0, 1, 2]
startOrientation = p.getQuaternionFromEuler([0.5, 0.5, 0])
boxId = p.loadURDF("r2d2.urdf", startPos, startOrientation, useFixedBase=True) # useFixedBase=True for this example

# 2. Define the rotation parameters
# The point around which to rotate (the center of rotation)
rotation_center = np.array([0, 1, 2])
# The arbitrary axis to rotate around (as a unit vector)
rotation_axis = np.array([0, 0, 1]) 
rotation_axis = rotation_axis / np.linalg.norm(rotation_axis) # Normalize the axis

angle = 0.01

# Keep the simulation running to observe the result
while p.isConnected():
#for i in range(2000):
    # The angle to rotate by (in radians)
    #angle = np.pi / 4 # 45 degrees
    #angle = angle + 0.05

    # 3. Get the object's current position and orientation
    current_pos, current_orn_quat = p.getBasePositionAndOrientation(boxId)
    current_pos = np.array(current_pos)

    # 4. Calculate the new orientation quaternion
    # PyBullet's built-in axis-angle to quaternion function:
    # We create a new rotation that we will compose with the current one
    axis_angle_quat = p.getQuaternionFromAxisAngle(rotation_axis, angle)

    # The new orientation is the composition of the current orientation and the new rotation
    # p.multiplyTransforms is used to combine rotations (quaternions)
    new_orn_quat = p.multiplyTransforms([0,0,0], current_orn_quat, [0,0,0], axis_angle_quat)[1]


    # 5. Calculate the new position
    # Vector from rotation center to current object position
    vec_to_obj = current_pos - rotation_center

    # Rotate this vector using the new orientation (relative to the axis-angle rotation)
    # We can use the axis-angle quat for this specific vector rotation
    #rotated_vec_to_obj, _ = p.multiplyTransforms([0,0,0], axis_angle_quat, vec_to_obj, [0,0,0])
    rotated_vec_to_obj, _ = p.multiplyTransforms([0,0,0], axis_angle_quat, vec_to_obj.tolist(), [0,0,0,1])

    # The new position is the rotation center plus the rotated vector
    new_pos = rotation_center + rotated_vec_to_obj


    # 6. Apply the new position and orientation to the object
    p.resetBasePositionAndOrientation(boxId, new_pos, new_orn_quat)

    p.stepSimulation()
    time.sleep(1./240.)

    #pass
