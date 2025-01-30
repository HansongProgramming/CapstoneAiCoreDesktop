import bpy
import random

class BLOOD_SPLATTER_PT_Panel(bpy.types.Panel):
    bl_label = "Blood Splatter Simulator"
    bl_idname = "BLOOD_SPLATTER_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BloodSim'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.add_actors", text="Add Actors", icon='MESH_PLANE')
        layout.operator("object.simulate", text="Simulate", icon='PLAY')

class OBJECT_OT_AddActors(bpy.types.Operator):
    bl_idname = "object.add_actors"
    bl_label = "Add Blood Simulation Actors"
    
    def execute(self, context):
        self.create_canvas()
        self.create_brush()
        return {'FINISHED'}
    
    def create_canvas(self):
        bpy.ops.mesh.primitive_plane_add(size=5)
        canvas = bpy.context.object
        canvas.name = "Canvas"

        # Add Dynamic Paint Canvas
        mod = canvas.modifiers.new(name="Dynamic Paint", type='DYNAMIC_PAINT')
        mod.ui_type = 'CANVAS'
        bpy.ops.dpaint.type_toggle(type='CANVAS')

        # Get the surface list and configure the paint settings
        canvas_settings = mod.canvas_settings
        surface = canvas_settings.surface_list.new()
        surface.surface_type = 'PAINT'
        surface.use_dry = True  # Persistent stains
        surface.dry_speed = 0.3  # Slower drying for visible blood stains
        surface.color_dry = (0.3, 0, 0)  # Darker red when dried
        surface.effect_ui = 'SPREAD'  # Helps spread the blood slightly
        surface.spread_speed = 0.15  # Slight spread effect

        print("Canvas created")

    def create_brush(self):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 2))
        brush = bpy.context.object
        brush.name = "Brush"

        # Add Particle System
        ps = brush.modifiers.new(name="Blood Particles", type='PARTICLE_SYSTEM')
        psys = brush.particle_systems.active
        settings = psys.settings
        settings.count = 200  # More blood splatter particles
        settings.lifetime = 40
        settings.frame_start = 1
        settings.frame_end = 5
        settings.physics_type = 'NEWTON'
        settings.render_type = 'NONE'
        settings.emit_from = 'FACE'
        settings.normal_factor = -3.5  # Controls blood splatter direction
        settings.tangent_factor = random.uniform(0.5, 1.5)  # Slight side motion for variety
        settings.particle_size = 0.07
        settings.use_rotations = True
        settings.rotation_factor_random = 1.2  # More random splatter rotation
        settings.damping = 0.6  # Reduces bouncing for better blood-like movement
        settings.velocity_factor_random = 0.4  # Randomizes splatter velocity

        # Add Dynamic Paint Brush
        mod = brush.modifiers.new(name="Dynamic Paint", type='DYNAMIC_PAINT')
        mod.ui_type = 'BRUSH'
        bpy.ops.dpaint.type_toggle(type='BRUSH')

        brush_settings = mod.brush_settings
        brush_settings.paint_color = (1, 0, 0)  # Blood red
        brush_settings.paint_source = 'PARTICLE_SYSTEM'
        brush_settings.particle_system = psys

        # Add Material for Blood (for better rendering)
        blood_material = bpy.data.materials.get("BloodMaterial")
        if not blood_material:
            blood_material = bpy.data.materials.new(name="BloodMaterial")
            blood_material.use_nodes = True
            nodes = blood_material.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.6, 0, 0, 1)  # Dark red
                bsdf.inputs["Roughness"].default_value = 0.2  # Slight wet look
                bsdf.inputs["Metallic"].default_value = 0.1  # Subtle reflection
        brush.data.materials.append(blood_material)

        print("Brush created with improved splatter settings")

class OBJECT_OT_Simulate(bpy.types.Operator):
    bl_idname = "object.simulate"
    bl_label = "Play Simulation"

    def execute(self, context):
        bpy.ops.screen.animation_play()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BLOOD_SPLATTER_PT_Panel)
    bpy.utils.register_class(OBJECT_OT_AddActors)
    bpy.utils.register_class(OBJECT_OT_Simulate)

def unregister():
    bpy.utils.unregister_class(BLOOD_SPLATTER_PT_Panel)
    bpy.utils.unregister_class(OBJECT_OT_AddActors)
    bpy.utils.unregister_class(OBJECT_OT_Simulate)

if __name__ == "__main__":
    register()
