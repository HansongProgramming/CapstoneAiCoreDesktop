import bpy

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
#       self.create_canvas()
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
        surface.dry_speed = 0.1  # Slower drying for visible blood stains
        surface.color_dry = (0.5, 0, 0)  # Dark red stain
        surface.effect_ui = 'SPREAD'  # Helps spread the blood slightly
        
        print("Canvas created")

    def create_brush(self):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 2))
        brush = bpy.context.object
        brush.name = "Brush"

        # Add Particle System
        ps = brush.modifiers.new(name="Blood Particles", type='PARTICLE_SYSTEM')
        psys = brush.particle_systems.active
        settings = psys.settings
        settings.count = 150  # More blood splat particles
        settings.lifetime = 30
        settings.frame_start = 1
        settings.frame_end = 5
        settings.physics_type = 'NEWTON'
        settings.render_type = 'NONE'
        settings.emit_from = 'FACE'
        settings.normal_factor = -2  # Controls blood splatter direction
        settings.tangent_factor = 1  # Adds slight side motion for variety
        settings.particle_size = 0.08
        settings.use_rotations = True
        settings.rotation_factor_random = 1.0  # Random splatter rotation

        # Add Dynamic Paint Brush
        mod = brush.modifiers.new(name="Dynamic Paint", type='DYNAMIC_PAINT')
        mod.ui_type = 'BRUSH'
        bpy.ops.dpaint.type_toggle(type='BRUSH')

        brush_settings = mod.brush_settings
        brush_settings.paint_color = (1, 0, 0)  # Blood red
        brush_settings.paint_source = 'PARTICLE_SYSTEM'
        brush_settings.particle_system = psys

        print("Brush created")

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
