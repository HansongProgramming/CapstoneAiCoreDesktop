import bpy

#! CANVAS PLANE
# Create a plane (Canvas)
bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
canvas = bpy.context.object

# Add Subdivision Surface Modifier
subsurf = canvas.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 8
subsurf.render_levels = 8
subsurf.subdivision_type = 'SIMPLE'

# Add Dynamic Paint Modifier and set as Canvas
dp = canvas.modifiers.new(name="Dynamic Paint", type='DYNAMIC_PAINT')
bpy.ops.dpaint.type_toggle(type='CANVAS')

# Ensure the brush collection exists
if "brush" in bpy.data.collections:
    dp.canvas_settings.canvas_surfaces["Surface"].brush_collection = bpy.data.collections["brush"]

# Set initial color type
dp.canvas_settings.canvas_surfaces["Surface"].init_color_type = 'COLOR'

# Add Material
material = bpy.data.materials.new(name="DynamicPaintMaterial")
material.use_nodes = True  # Enable nodes
canvas.data.materials.append(material)  # Assign material to object

# Access Node Tree
node_tree = material.node_tree
nodes = node_tree.nodes
links = node_tree.links

# Create Attribute Node (without bpy.ops)
attribute_node = nodes.new(type="ShaderNodeAttribute")
attribute_node.location = (-300, 100)
attribute_node.attribute_name = "dp_paintmap"

# Link Attribute Node to Material Output (Example)
principled_bsdf = nodes.get("Principled BSDF")
if principled_bsdf:
    links.new(attribute_node.outputs["Color"], principled_bsdf.inputs["Base Color"])

# Enable Spread and Drip
dp.canvas_settings.canvas_surfaces["Surface"].use_spread = True
dp.canvas_settings.canvas_surfaces["Surface"].use_drip = True

# Find the Properties Editor area and override context
for area in bpy.context.screen.areas:
    if area.type == 'PROPERTIES':  # Look for the Properties Editor
        override = {'area': area, 'object': canvas}
        
        # Toggle output A (Alpha) and B (Wetmap)
        bpy.ops.dpaint.output_toggle(override, output='A')
        bpy.ops.dpaint.output_toggle(override, output='B')

        print("✔ Successfully toggled Output A & B!")
        break
else:
    print("⚠ Could not find the PROPERTIES area! bpy.ops.dpaint.output_toggle() may fail.")



# ! BRUSH PLANE

import bpy

# Create a Plane
bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 2.70914))
plane = bpy.context.object

# Rotate Plane
plane.rotation_euler[1] = 2.1342  # Rotate around Y-axis
plane.rotation_euler[0] = 3.14159  # Rotate around X-axis

# Add Subdivision Surface Modifier
subsurf = plane.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 8
subsurf.render_levels = 8

# Add Particle System
bpy.ops.object.particle_system_add()
particle_system = plane.particle_systems[0]
particle_settings = particle_system.settings
particle_settings.render_type = 'OBJECT'
particle_settings.display_size = 0.03
particle_settings.normal_factor = 3
particle_settings.factor_random = 3
particle_settings.frame_end = 5
particle_settings.count = 400

# Resize Plane
plane.scale = (0.145423, 0.145423, 0.145423)

# Create an Icosphere (Particle Instance)
bpy.ops.mesh.primitive_ico_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(4.83279, 0, 0))
ico_sphere = bpy.context.object
bpy.ops.object.shade_smooth()

# Resize Icosphere
ico_sphere.scale = (0.106316, 0.106316, 0.106316)

# Assign Icosphere as Particle Instance Object
particle_settings.instance_object = ico_sphere

# Add Dynamic Paint Modifier and Set as Brush
dp_brush = plane.modifiers.new(name="Dynamic Paint", type='DYNAMIC_PAINT')
bpy.ops.dpaint.type_toggle(type='BRUSH')

# Configure Dynamic Paint Brush
dp_brush.ui_type = 'BRUSH'
dp_brush.brush_settings.paint_source = 'PARTICLE_SYSTEM'
dp_brush.brush_settings.particle_system = particle_system
dp_brush.brush_settings.solid_radius = 0.03
dp_brush.brush_settings.smooth_radius = 0
dp_brush.brush_settings.paint_color = (0.8, 0.0171646, 0)

print("✔ Successfully set up Particle Brush!")

#! init scene
bpy.context.scene.frame_end = 100
bpy.context.space_data.shading.type = 'MATERIAL'
