bl_info = {
    "name": "Auto Arkit UE Shapekeys (ARKit / Unified Expressions)",
    "author": "Claude, MooshPaw",
    "version": (1, 2, 0),
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

# Your personal preset - custom order + only the blended shapes you actually use
MY_CUSTOM_SHAPES = [
    # Eye Brows
    "BrowDownLeft", "BrowDownRight",
    "BrowInnerUpLeft", "BrowInnerUpRight",
    "BrowLowererLeft", "BrowLowererRight",
    "BrowOuterUpLeft", "browOuterUpRight",
    "BrowPinchLeft", "BrowPinchRight",

    # Cheeks
    "CheekPuffLeft", "CheekPuffRight",
    "CheekSquintLeft", "CheekSquintRight",
    "CheekSuckLeft", "CheekSuckRight",

    # Eyes
    "EyeClosedLeft", "EyeClosedRight",
    "EyeSquintLeft", "EyeSquintRight",
    "EyeWideLeft", "EyeWideRight",
    "EyeLookDownLeft", "EyeLookDownRight",
    "EyeLookInLeft", "EyeLookInRight",
    "EyeLookOutLeft", "EyeLookOutRight",
    "EyeLookUpLeft", "EyeLookUpRight",
    "EyeDilationLeft", "EyeDilationRight",
    "EyeConstrictLeft", "EyeConstrictRight",

    # Jaw
    "JawBackward", "JawForward",
    "JawLeft", "JawOpen", "JawRight",

    # Lips
    "LipSuckUpperLeft", "LipSuckUpperRight",
    "LipSuckLowerLeft", "LipSuckLowerRight",

    # Mouth
    "MouthClosed",
    "MouthDimpleLeft", "MouthDimpleRight",
    "MouthFrownLeft", "MouthFrownRight",
    "MouthLeft", "MouthRight",
    "MouthPressLeft", "MouthPressRight",
    "MouthRaiserUpper", "MouthRaiserLower",
    "MouthSmileLeft", "mouthSmileRight",
    "MouthStretchLeft", "MouthStretchRight",
    "MouthUpperUpLeft", "MouthUpperUpRight",
    "MouthLowerDownLeft", "MouthLowerDownRight",

    #Nose
    "NoseSneerLeft", "NoseSneerRight",
    "NasalDilationLeft", "NasalDilationRight",
    "NasalConstrictLeft", "NasalConstrictRight",

    # Tongue
    "TongueOut",
    "TongueUp", "TongueDown",
    "TongueLeft", "TongueRight",
    "TongueRoll",
    "TongueBendDown", "TongueCurlUp",
    "TongueSquish", "TongueFlat",
    "TongueTwistLeft", "TongueTwistRight",

    # IF YOU DON'T PLAN ON USING BLENDED SHAPES, PUT A # NEXT TO "---BLENDED SHAPES---,"
    "---Blended Shapes---",
    "BrowInnerUp",
    "CheekPuff",
    "LipSuckLower",
    "LipSuckUpper",
    "LipFunnel", "LipPucker",
    "EyesLookDown", "EyesLookUp",
]


# ---------------------------------------------------------------------------
# ARKit <-> Unified Expressions name mapping
# Source: VRCFaceTracking's official ARKit compatibility table
# (docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/arkit)
# Only shapes with a direct equivalent are listed. Some Unified Expressions
# names here are "Blended Shapes" (e.g. LipPucker, BrowInnerUp, MouthLeft),
# which is expected since ARKit's shapes are often a combined equivalent.
# MouthLeft/MouthRight are not in the official table but are added here since
# they are the direct Blended Shape equivalents of ARKit's mouthLeft/mouthRight.
# ---------------------------------------------------------------------------
UNIFIED_TO_ARKIT = {
    "EyeLookUpRight": "eyeLookUpRight",
    "EyeLookDownRight": "eyeLookDownRight",
    "EyeLookInRight": "eyeLookInRight",
    "EyeLookOutRight": "eyeLookOutRight",
    "EyeLookUpLeft": "eyeLookUpLeft",
    "EyeLookDownLeft": "eyeLookDownLeft",
    "EyeLookInLeft": "eyeLookInLeft",
    "EyeLookOutLeft": "eyeLookOutLeft",
    "EyeClosedRight": "eyeBlinkRight",
    "EyeClosedLeft": "eyeBlinkLeft",
    "EyeSquintRight": "eyeSquintRight",
    "EyeSquintLeft": "eyeSquintLeft",
    "EyeWideRight": "eyeWideRight",
    "EyeWideLeft": "eyeWideLeft",
    "BrowDownRight": "browDownRight",
    "BrowDownLeft": "browDownLeft",
    "BrowInnerUp": "browInnerUp",
    "BrowOuterUpRight": "browOuterUpRight",
    "BrowOuterUpLeft": "browOuterUpLeft",
    "NoseSneerRight": "noseSneerRight",
    "NoseSneerLeft": "noseSneerLeft",
    "CheekSquintRight": "cheekSquintRight",
    "CheekSquintLeft": "cheekSquintLeft",
    "CheekPuff": "cheekPuff",
    "JawOpen": "jawOpen",
    "MouthClosed": "mouthClose",
    "JawRight": "jawRight",
    "JawLeft": "jawLeft",
    "JawForward": "jawForward",
    "LipSuckUpper": "mouthRollUpper",
    "LipSuckLower": "mouthRollLower",
    "LipFunnel": "mouthFunnel",
    "LipPucker": "mouthPucker",
    "MouthUpperUpRight": "mouthUpperUpRight",
    "MouthUpperUpLeft": "mouthUpperUpLeft",
    "MouthLowerDownRight": "mouthLowerDownRight",
    "MouthLowerDownLeft": "mouthLowerDownLeft",
    "MouthSmileRight": "mouthSmileRight",
    "MouthSmileLeft": "mouthSmileLeft",
    "MouthFrownRight": "mouthFrownRight",
    "MouthFrownLeft": "mouthFrownLeft",
    "MouthStretchRight": "mouthStretchRight",
    "MouthStretchLeft": "mouthStretchLeft",
    "MouthDimpleRight": "mouthDimpleRight",
    "MouthDimpleLeft": "mouthDimpleLeft",
    "MouthRaiserUpper": "mouthShrugUpper",
    "MouthRaiserLower": "mouthShrugLower",
    "MouthPressRight": "mouthPressRight",
    "MouthPressLeft": "mouthPressLeft",
    "TongueOut": "tongueOut",
    "MouthLeft": "mouthLeft",
    "MouthRight": "mouthRight",
}
ARKIT_TO_UNIFIED = {v: k for k, v in UNIFIED_TO_ARKIT.items()}


class MESH_OT_add_facial_blendshapes(Operator):
    """Add a full set of empty (zero-deformation) shape keys to the active mesh"""
    bl_idname = "mesh.add_facial_blendshapes"
    bl_label = "Add FT Blendshapes"
    bl_options = {'REGISTER', 'UNDO'}

    standard: EnumProperty(
        name="Standard",
        description="Which blendshape naming standard to add",
        items=[
            ('ARKIT', "ARKit", "The 52 standard Apple ARKit blendshapes"),
            ('UNIFIED', "Unified Expressions", "The VRCFaceTracking Unified Expressions standard"),
            ('CUSTOM', "My Preset", "My personal shape key preset (Must be manually edited on the .py)"),
        ],
        default='CUSTOM',
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
        elif self.standard == 'UNIFIED':
            groups = [("---Face Tracking---", UNIFIED_BASE_SHAPES)]
            if self.include_blended:
                groups.append(("---Blended Shapes---", UNIFIED_BLENDED_SHAPES))
        else:  # CUSTOM
            groups = [("---Face Tracking---", MY_CUSTOM_SHAPES)]

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


class MESH_OT_convert_facial_blendshapes(Operator):
    """Duplicate existing shape keys under the other naming scheme, keeping their deformation"""
    bl_idname = "mesh.convert_facial_blendshapes"
    bl_label = "Convert Blendshape Naming"
    bl_options = {'REGISTER', 'UNDO'}

    target: EnumProperty(
        name="Convert To",
        description="Which naming scheme to translate existing shape keys into",
        items=[
            ('ARKIT', "ARKit", "Duplicate matching shape keys using ARKit names"),
            ('UNIFIED', "Unified Expressions", "Duplicate matching shape keys using Unified Expressions names"),
        ],
        default='UNIFIED',
    )
    skip_existing: BoolProperty(
        name="Skip Existing",
        description="Don't create a duplicate if a shape key with the target name already exists",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'MESH' and obj.data.shape_keys is not None

    def execute(self, context):
        obj = context.object
        mesh = obj.data
        key_blocks = mesh.shape_keys.key_blocks

        mapping = ARKIT_TO_UNIFIED if self.target == 'UNIFIED' else UNIFIED_TO_ARKIT
        target_label = "---Unified Expressions---" if self.target == 'UNIFIED' else "---ARKit---"
        source_label = "---ARKit---" if self.target == 'UNIFIED' else "---Unified Expressions---"

        # The generic "---Face Tracking---" separator (from the Add FT Blendshapes
        # operator) doesn't say which standard it holds. Now that we know - because
        # we're converting FROM it - rename it to be explicit.
        if "---Face Tracking---" in key_blocks:
            key_blocks["---Face Tracking---"].name = source_label

        source_names = [kb.name for kb in key_blocks]
        existing = {kb.name for kb in key_blocks}

        # Work out which shapes will actually be converted before touching anything,
        # so we don't create an empty separator when there's nothing to convert.
        matches = []
        skipped = 0
        for name in source_names:
            target_name = mapping.get(name)
            if target_name is None:
                continue
            if self.skip_existing and target_name in existing:
                skipped += 1
                continue
            matches.append((name, target_name))

        converted = 0
        if matches:
            if not (self.skip_existing and target_label in existing):
                obj.shape_key_add(name=target_label, from_mix=False)
                existing.add(target_label)

            for name, target_name in matches:
                source_kb = key_blocks[name]
                new_kb = obj.shape_key_add(name=target_name, from_mix=False)
                for i, point in enumerate(source_kb.data):
                    new_kb.data[i].co = point.co
                existing.add(target_name)
                converted += 1

        self.report(
            {'INFO'},
            f"Created {converted} duplicate shape keys as {self.target.title()}. Skipped {skipped} that already existed."
        )
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# UI Panel
# ---------------------------------------------------------------------------

class VIEW3D_PT_facial_blendshapes(Panel):
    bl_label = "Face Tracking Blendshapes"
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

        layout.separator()
        layout.label(text="Convert Existing Blendshapes:")
        row = layout.row(align=True)
        op_a = row.operator("mesh.convert_facial_blendshapes", text="To ARKit")
        op_a.target = 'ARKIT'
        op_a.skip_existing = settings.skip_existing
        op_u = row.operator("mesh.convert_facial_blendshapes", text="To Unified")
        op_u.target = 'UNIFIED'
        op_u.skip_existing = settings.skip_existing


class FacialBlendshapeSettings(bpy.types.PropertyGroup):
    standard: EnumProperty(
        name="Standard",
        items=[
            ('ARKIT', "ARKit", "The 52 standard Apple ARKit blendshapes"),
            ('UNIFIED', "Unified Expressions", "The VRCFaceTracking Unified Expressions standard"),
            ('CUSTOM', "My Preset", "My personal shape key preset (Must be manually edited on the .py)"),
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
    MESH_OT_convert_facial_blendshapes,
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
