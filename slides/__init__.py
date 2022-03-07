import bpy
import os
import random
import json

bl_info = {
  "name": "Slides",
  "description": "Create presentation slides using Geometry Nodes",
  "author": "Michael Gold",
  "version": (0, 0, 1),
  "blender": (3, 1, 0),
  "location": "Object > Modifier",
  "warning": "",
  "doc_url": "Slides",
  "tracker_url": "https://github.com/michaelgold/slides",
  "support": "COMMUNITY",
  "category": "Presentations"
}


custom_icons = None

class SLIDES_PG_slide_list_item(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    slide: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        description="Only make this object available for selection if one of the objects in this list have been selected"
    )


class SLIDES_UL_slide_list(bpy.types.UIList):
    """Slide UI List"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            text = item.slide.name if hasattr(item.slide, "name") else "Select an Object"
            layout.label(text=text, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)


class SLIDES_OT_slide_list_new_item(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "slides.slide_list_new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.scene.slides.slide_list.add()

        return{'FINISHED'}


class SLIDES_OT_slide_list_delete_item(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "slides.slide_list_delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.scene.slides.slide_list

    def execute(self, context):
        slide_list = context.scene.slides.slide_list
        index = context.scene.slides.slide_list_index

        slide_list.remove(index)
        context.scene.slides.slide_list_index = min(max(0, index - 1), len(slide_list) - 1)

        return{'FINISHED'}


class SLIDES_OT_slide_list_move_item(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "slides.slide_list_move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.scene.slides.slide_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.slides.slide_list_index
        list_length = len(bpy.context.scene.slides.slide_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.slides.slide_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        slide_list = context.scene.slides.slide_list
        index = context.scene.slides.slide_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        slide_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}


  
class SLIDES_PG_scene(bpy.types.PropertyGroup):
    generated_metadata: bpy.props.StringProperty(name="Generated Meta Data")
    enable_pre_generation_script: bpy.props.BoolProperty(name="Run Custom Script Before Generation", default=False)
    pre_generation_script: bpy.props.PointerProperty(name="Pre-generation Script", type=bpy.types.Text)

    enable_post_generation_script: bpy.props.BoolProperty(name="Run Custom Script After Generation", default=False)
    post_generation_script: bpy.props.PointerProperty(name="Post-generation Script", type=bpy.types.Text)

    
    slide_list: bpy.props.CollectionProperty(type=SLIDES_PG_slide_list_item)
    
    slide_list_index: bpy.props.IntProperty(name = "Index for slides.slide_list", default = 0)


class SLIDES_PT_settings(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Slides"
    bl_label = "Settings"
    bl_idname = "SLIDES_PT_settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        row = layout.row()
        grid_flow = row.grid_flow(columns=1, even_columns=True, row_major=True)
        col = grid_flow.column()
        this_context = bpy.context.scene
        
        col.prop(this_context.slides, 'enable_pre_generation_script')

        if this_context.slides.enable_pre_generation_script:
            box = col.box()
            box.prop(this_context.slides, 'pre_generation_script', text="Python Script")

        col.prop(this_context.slides, 'enable_post_generation_script')

        if this_context.slides.enable_post_generation_script:
            box = col.box()
            box.prop(this_context.slides, 'post_generation_script', text="Python Script")

class SLIDES_PT_slide_list(bpy.types.Panel):
    bl_label = "Slides"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Slides" 



    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        layout = self.layout 
        this_context = context.scene
        slide_context = context.object

        
        split = layout.split(factor=0.1)
        col = split.column()
        col = split.column()
        
        

        row = col.row()
        row.template_list("SLIDES_UL_slide_list", "The_List", this_context.slides,
                          "slide_list", this_context.slides, "slide_list_index")

        row = col.row()
        row.operator('slides.slide_list_new_item', text='NEW')
        row.operator('slides.slide_list_delete_item', text='REMOVE')
        row.operator('slides.slide_list_move_item', text='UP').direction = 'UP'
        row.operator('slides.slide_list_move_item', text='DOWN').direction = 'DOWN'

        if this_context.slides.slide_list_index >= 0 and this_context.slides.slide_list:
            item = this_context.slides.slide_list[this_context.slides.slide_list_index]

            row = col.row()
            row.prop(item, "slide")
            # row.prop(item, "random_prop")



classes = [
    SLIDES_PG_slide_list_item,
    SLIDES_PG_scene,
    SLIDES_PT_slide_list,
    SLIDES_UL_slide_list,
    SLIDES_PT_settings,
    SLIDES_OT_slide_list_new_item,
    SLIDES_OT_slide_list_delete_item,
    SLIDES_OT_slide_list_move_item,
]


def register():
    # global custom_icons
    # custom_icons = bpy.utils.previews.new()
    # addon_path =  os.path.dirname(__file__)
    # icons_dir = os.path.join(addon_path, "icons")
    
    # custom_icons.load("custom_icon", os.path.join(icons_dir, "icon.png"), 'IMAGE')
   

    for this_class in classes:
        bpy.utils.register_class(this_class)

    #adds the property group class to the object context (instantiates it)
    # bpy.types.Object.slides = bpy.props.PointerProperty(type=SLIDES_PG_main)
    bpy.types.Scene.slides = bpy.props.PointerProperty(type=SLIDES_PG_scene)


#same as register but backwards, deleting references
def unregister():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    #delete the custom property pointer
    #NOTE: this is different from its accessor, as that is a read/write only
    #to delete this we have to delete its pointer, just like how we added it
    # del bpy.types.Object.slides 
    del bpy.types.Scene.slides

    for this_class in classes:
        bpy.utils.unregister_class(this_class)  

#a quick line to autorun the script from the text editor when we hit 'run script'
if __name__ == '__main__':
    register()


