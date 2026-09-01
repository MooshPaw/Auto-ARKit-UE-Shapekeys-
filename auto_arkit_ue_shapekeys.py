bl_info = {
    "name": "Facial Blendshape Adder (ARKit / Unified Expressions)",
    "author": "Claude",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > Sidebar (N-panel) > Tool",
    "description": "Adds a full set of empty (zero-deformation) shape keys following either "
                   "the ARKit 52 blendshape spec or the Unified Expressions standard "
                   "(used by VRCFaceTracking / VRChat / VRM face tracking).",
    "category": "Mesh",
}

import bpy
from bpy.props import EnumProperty, BoolProperty
from bpy.types import Operator, Panel

# ---------------------------------------------------------------------------
# Shape name data
# ---------------------------------------------------------------------------

# The 52 standard ARKit blendshapes (ARFaceAnchor.BlendShapeLocation)
ARKIT_SHAPES = [
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
    "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
    "eyeBlinkLeft", "eyeBlinkRight",
    "eyeLookDownLeft", "eyeLookDownRight", "eyeLookInLeft", "eyeLookInRight",
    "eyeLookOutLeft", "eyeLookOutRight", "eyeLookUpLeft", "eyeLookUpRight",
    "eyeSquintLeft", "eyeSquintRight", "eyeWideLeft", "eyeWideRight",
    "jawForward", "jawLeft", "jawOpen", "jawRight",
    "mouthClose", "mouthDimpleLeft", "mouthDimpleRight",
    "mouthFrownLeft", "mouthFrownRight", "mouthFunnel",
    "mouthLeft", "mouthLowerDownLeft", "mouthLowerDownRight",
    "mouthPressLeft", "mouthPressRight", "mouthPucker", "mouthRight",
    "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
    "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft", "mouthStretchRight",
    "mouthUpperUpLeft", "mouthUpperUpRight",
    "noseSneerLeft", "noseSneerRight", "tongueOut",
]

# Unified Expressions "Base Shapes" (VRCFaceTracking standard, docs.vrcft.io)
UNIFIED_BASE_SHAPES = [
    "EyeLookOutRight", "EyeLookInRight", "EyeLookUpRight", "EyeLookDownRight",
    "EyeLookOutLeft", "EyeLookInLeft", "EyeLookUpLeft", "EyeLookDownLeft",
    "EyeClosedRight", "EyeClosedLeft",
    "EyeSquintRight", "EyeSquintLeft",
    "EyeWideRight", "EyeWideLeft",
    "EyeDilationRight", "EyeDilationLeft",
    "EyeConstrictRight", "EyeConstrictLeft",
    "BrowPinchRight", "BrowPinchLeft",
    "BrowLowererRight", "BrowLowererLeft",
    "BrowInnerUpRight", "BrowInnerUpLeft",
    "BrowOuterUpRight", "BrowOuterUpLeft",
    "NoseSneerRight", "NoseSneerLeft",
    "NasalDilationRight", "NasalDilationLeft",
    "NasalConstrictRight", "NasalConstrictLeft",
    "CheekSquintRight", "CheekSquintLeft",
    "CheekPuffRight", "CheekPuffLeft",
    "CheekSuckRight", "CheekSuckLeft",
    "JawOpen", "MouthClosed", "JawRight", "JawLeft", "JawForward", "JawBackward",
    "JawClench", "JawMandibleRaise",
    "LipSuckUpperRight", "LipSuckUpperLeft", "LipSuckLowerRight", "LipSuckLowerLeft",
    "LipSuckCornerRight", "LipSuckCornerLeft",
    "LipFunnelUpperRight", "LipFunnelUpperLeft", "LipFunnelLowerRight", "LipFunnelLowerLeft",
    "LipPuckerUpperRight", "LipPuckerUpperLeft", "LipPuckerLowerRight", "LipPuckerLowerLeft",
    "MouthUpperUpRight", "MouthUpperUpLeft", "MouthLowerDownRight", "MouthLowerDownLeft",
    "MouthUpperDeepenRight", "MouthUpperDeepenLeft",
    "MouthUpperRight", "MouthUpperLeft", "MouthLowerRight", "MouthLowerLeft",
    "MouthCornerPullRight", "MouthCornerPullLeft",
    "MouthCornerSlantRight", "MouthCornerSlantLeft",
    "MouthFrownRight", "MouthFrownLeft",
    "MouthStretchRight", "MouthStretchLeft",
    "MouthDimpleRight", "MouthDimpleLeft",
    "MouthRaiserUpper", "MouthRaiserLower",
    "MouthPressRight", "MouthPressLeft",
    "MouthTightenerRight", "MouthTightenerLeft",
    "TongueOut", "TongueUp", "TongueDown", "TongueRight", "TongueLeft",
    "TongueRoll", "TongueBendDown", "TongueCurlUp", "TongueSquish", "TongueFlat",
    "TongueTwistRight", "TongueTwistLeft",
    "SoftPalateClose", "ThroatSwallow", "NeckFlexRight", "NeckFlexLeft",
]

# Unified Expressions "Blended Shapes" - simplified combinations of the base shapes,
# optional but commonly included for compatibility with simpler tracking setups.
UNIFIED_BLENDED_SHAPES = [
    "EyeClosed", "EyeWide", "EyeSquint", "EyeDilation", "EyeConstrict",
    "BrowDownRight", "BrowDownLeft", "BrowDown",
    "BrowInnerUp", "BrowUpRight", "BrowUpLeft", "BrowUp",
    "NoseSneer", "NasalDilation", "NasalConstrict",
    "CheekPuff", "CheekSuck", "CheekSquint",
    "LipSuckUpper", "LipSuckLower", "LipSuck",
    "LipFunnelUpper", "LipFunnelLower", "LipFunnel",
    "LipPuckerUpper", "LipPuckerLower", "LipPucker",
    "MouthUpperUp", "MouthLowerDown", "MouthOpen",
    "MouthRight", "MouthLeft",
    "MouthSmileRight", "MouthSmileLeft", "MouthSmile",
    "MouthSadRight", "MouthSadLeft", "MouthSad",
    "MouthStretch", "MouthDimple", "MouthTightener", "MouthPress",
]


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class MESH_OT_add_facial_blendshapes(Operator):
    """Add a full set of empty (zero-deformation) shape keys to the active mesh"""
    bl_idname = "mesh.add_facial_blendshapes"
    bl_label = "Add Facial Blendshapes"
    bl_options = {'REGISTER', 'UNDO'}

    standard: EnumProperty(
        name="Standard",
        description="Which blendshape naming standard to add",
        items=[
            ('ARKIT', "ARKit", "The 52 standard Apple ARKit blendshapes"),
            ('UNIFIED', "Unified Expressions", "The VRCFaceTracking Unified Expressions standard"),
        ],
        default='ARKIT',
    )
    include_blended: BoolProperty(
        name="Include Blended Shapes",
        description="Also add the simplified 'Blended Shapes' on top of the Unified Expressions base shapes",
        default=False,
    )
    skip_existing: BoolProperty(
        name="Skip Existing",
        description="Don't create a shape key if one with the same name already exists",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        obj = context.object
        mesh = obj.data

        if mesh.shape_keys is None:
            obj.shape_key_add(name="Basis", from_mix=False)

        if self.standard == 'ARKIT':
            groups = [("---Face Tracking---", ARKIT_SHAPES)]
        else:
            groups = [("---Face Tracking---", UNIFIED_BASE_SHAPES)]
            if self.include_blended:
                groups.append(("---Blended Shapes---", UNIFIED_BLENDED_SHAPES))

        added = 0
        skipped = 0
        for separator_name, names in groups:
            existing = {kb.name for kb in mesh.shape_keys.key_blocks}
            if self.skip_existing and separator_name in existing:
                skipped += 1
            else:
                obj.shape_key_add(name=separator_name, from_mix=False)
                added += 1

            existing = {kb.name for kb in mesh.shape_keys.key_blocks}
            for name in names:
                if self.skip_existing and name in existing:
                    skipped += 1
                    continue
                obj.shape_key_add(name=name, from_mix=False)
                added += 1

        self.report(
            {'INFO'},
            f"Added {added} empty shape keys ({self.standard.title()}). Skipped {skipped} that already existed."
        )
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# UI Panel
# ---------------------------------------------------------------------------

class VIEW3D_PT_facial_blendshapes(Panel):
    bl_label = "Facial Blendshapes"
    bl_idname = "VIEW3D_PT_facial_blendshapes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj is None or obj.type != 'MESH':
            layout.label(text="Select a mesh object", icon='ERROR')
            return

        scene = context.scene
        settings = scene.facial_blendshape_settings

        layout.prop(settings, "standard", expand=True)
        if settings.standard == 'UNIFIED':
            layout.prop(settings, "include_blended")
        layout.prop(settings, "skip_existing")

        op = layout.operator("mesh.add_facial_blendshapes", icon='SHAPEKEY_DATA')
        op.standard = settings.standard
        op.include_blended = settings.include_blended
        op.skip_existing = settings.skip_existing


class FacialBlendshapeSettings(bpy.types.PropertyGroup):
    standard: EnumProperty(
        name="Standard",
        items=[
            ('ARKIT', "ARKit", "The 52 standard Apple ARKit blendshapes"),
            ('UNIFIED', "Unified Expressions", "The VRCFaceTracking Unified Expressions standard"),
        ],
        default='ARKIT',
    )
    include_blended: BoolProperty(
        name="Include Blended Shapes",
        default=False,
    )
    skip_existing: BoolProperty(
        name="Skip Existing",
        default=True,
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    MESH_OT_add_facial_blendshapes,
    FacialBlendshapeSettings,
    VIEW3D_PT_facial_blendshapes,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.facial_blendshape_settings = bpy.props.PointerProperty(type=FacialBlendshapeSettings)


def unregister():
    del bpy.types.Scene.facial_blendshape_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
