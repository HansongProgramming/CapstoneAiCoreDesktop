import math

distanceZ = math.sqrt(((161.09545335 - -221.5)**2) + ((405.8439528 - -410)**2))
print(f"height: {distanceZ}")

import math

# The angle in degrees
angle_in_degrees = -24.55740437441537

# Convert the angle to radians and then compute the sine
result = math.sin(math.radians(angle_in_degrees))

print(result * distanceZ)
