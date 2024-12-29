import math

def calculate_angle_of_impact(length, width):
    if length <= width:
        raise ValueError("Length must be greater than width to calculate angle")
    
    # Calculate the angle of impact using the formula: sin^-1(width / length)
    angle_rad = math.asin(width / length)  # Returns the angle in radians
    angle_deg = math.degrees(angle_rad)  # Convert the angle to degrees
    return angle_deg

# Example usage
length = 4  # in centimeters
width = 1   # in centimeters

try:
    angle = calculate_angle_of_impact(length, width)
    print(f"The angle of impact is approximately: {angle:.2f} degrees")
except ValueError as e:
    print(e)
