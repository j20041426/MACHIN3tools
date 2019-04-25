import bpy
import bmesh
from ... utils import MACHIN3 as m3


class ShadeSmooth(bpy.types.Operator):
    bl_idname = "machin3.shade_smooth"
    bl_label = "Shade Smooth"
    bl_description = "Set smooth shading in object and edit mode\nALT: Mark edges sharp if face angle > auto smooth angle"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.mode == "OBJECT":
            bpy.ops.object.shade_smooth()

            # set sharps based on face angles + activate auto smooth + enable sharp overlays
            if event.alt:
                for obj in context.selected_objects:
                    obj.data.use_auto_smooth = True
                    angle = obj.data.auto_smooth_angle

                    bm = bmesh.new()
                    bm.from_mesh(obj.data)
                    bm.normal_update()

                    sharpen = [e for e in bm.edges if e.calc_face_angle() > angle]

                    for e in sharpen:
                        e.smooth = False

                    bm.to_mesh(obj.data)
                    bm.clear()

                context.space_data.overlay.show_edge_sharp = True

        elif context.mode == "EDIT_MESH":
            bpy.ops.mesh.faces_shade_smooth()

        return {'FINISHED'}


class ShadeFlat(bpy.types.Operator):
    bl_idname = "machin3.shade_flat"
    bl_label = "Shade Flat"
    bl_description = "Set flat shading in object and edit mode\nALT: Clear all sharps, bweights, creases and seams."
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.mode == "OBJECT":
            bpy.ops.object.shade_flat()

            # clear all sharps, bweights, seams and creases
            if event.alt:
                for obj in context.selected_objects:
                    obj.data.use_auto_smooth = False

                    bm = bmesh.new()
                    bm.from_mesh(obj.data)
                    bm.normal_update()

                    bw = bm.edges.layers.bevel_weight.verify()
                    cr = bm.edges.layers.crease.verify()

                    for e in bm.edges:
                        e[bw] = 0
                        e[cr] = 0
                        e.smooth = True
                        e.seam = False

                    bm.to_mesh(obj.data)
                    bm.clear()


        elif context.mode == "EDIT_MESH":
            bpy.ops.mesh.faces_shade_flat()

        return {'FINISHED'}


class ToggleAutoSmooth(bpy.types.Operator):
    bl_idname = "machin3.toggle_auto_smooth"
    bl_label = "Toggle Auto Smooth"
    bl_description = "Toggle Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = m3.get_active()

        if active:
            sel = m3.selected_objects()
            if active not in sel:
                sel.append(active)

            autosmooth = not active.data.use_auto_smooth

            for obj in sel:
                obj.data.use_auto_smooth = autosmooth

        return {'FINISHED'}
