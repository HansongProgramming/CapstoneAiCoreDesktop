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

bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.transform.translate(value=(0, 0, 2.70914), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, release_confirm=True)
bpy.ops.transform.rotate(value=2.1342, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, release_confirm=True)
bpy.ops.transform.rotate(value=3.14159, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.data.particles["ParticleSettings.001"].render_type = 'OBJECT'
bpy.context.object.modifiers["Subdivision"].levels = 8
bpy.context.object.modifiers["Subdivision"].render_levels = 8
bpy.ops.transform.resize(value=(0.145423, 0.145423, 0.145423), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
bpy.ops.object.particle_system_add()
bpy.data.particles["ParticleSettings.001"].display_size = 0.03
bpy.data.particles["ParticleSettings.001"].normal_factor = 3
bpy.data.particles["ParticleSettings.001"].factor_random = 3
bpy.data.particles["ParticleSettings.001"].frame_end = 5
bpy.data.particles["ParticleSettings.001"].count = 400
bpy.ops.mesh.primitive_ico_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.object.shade_smooth()
bpy.ops.transform.translate(value=(4.83279, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, release_confirm=True)
bpy.ops.transform.resize(value=(0.106316, 0.106316, 0.106316), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
bpy.data.particles["ParticleSettings.001"].instance_object = bpy.data.objects["Icosphere"]
bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
bpy.context.object.modifiers["Dynamic Paint"].ui_type = 'BRUSH'
bpy.ops.dpaint.type_toggle(type='BRUSH')
bpy.context.object.modifiers["Dynamic Paint"].brush_settings.paint_source = 'PARTICLE_SYSTEM'
bpy.context.object.modifiers["Dynamic Paint"].brush_settings.particle_system = bpy.data.objects["particles"].particle_systems["ParticleSystem"]
bpy.context.object.modifiers["Dynamic Paint"].brush_settings.solid_radius = 0.03
bpy.context.object.modifiers["Dynamic Paint"].brush_settings.smooth_radius = 0
bpy.context.object.modifiers["Dynamic Paint"].brush_settings.paint_color = (0.8, 0.0171646, 0)


#! init scene
bpy.context.scene.frame_end = 100
bpy.context.space_data.shading.type = 'MATERIAL'
