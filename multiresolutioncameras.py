# THE MULTI-RESOLUTION CAMERA ADD-ON
#
# Developed in March 2023 by Johan Basberg
#
# This version of the script adds a rendering outline to the customized camera.
# Without that mesh, you will not be able to see exactly what will be rendered.
#
# I hope you enjoy this add-on, cause I spent a lot of time developing it.
# Give me a shout-out on Twitter if you find it useful: @johanhwb
#
# Enjoy!
# Johan


bl_info = {
	"name": "Multi-Resolution Cameras",
	"author": "Johan Basberg",
	"version": (2, 6),
	"blender": (3, 0, 0),
	"location": "View3D > Sidebar [N] > Render Resolutions",
	"description": "Easily customize resolutions and render your cameras.",
	"category": "3D View",
}

import time
import math
import bpy
import os
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty


key_mesh = "Multi-Resolution Camera Mesh"
key_passepartout = "Multi-Resolution Camera Frame"


def on_highlighted_camera_index_update(self, context):
	scene = context.scene	
	if scene.move_focus_with_keys:
		selected_row = scene.camera_list.highlighted_camera_index
		selected_camera_item = context.scene.cameras[selected_row]
		camera_name = selected_camera_item.name
		
		print(f"Camera name: {camera_name}, Selected row: {selected_row}")
		
		bpy.ops.scene.select_camera(camera_name=camera_name, row_index=selected_row)


class CameraListProperties(bpy.types.PropertyGroup):
	highlighted_camera_index: bpy.props.IntProperty(
		name="Click to modify dimensions.",
		update=on_highlighted_camera_index_update
	)



class CAMERA_LIST_OT_clear_custom_size(bpy.types.Operator):
	bl_idname = "camera_list.reset_custom_dimension"
	bl_label = "Reset Width of Render Border"
	bl_description = "Restores default scene value"
	
	clear_dimension: bpy.props.StringProperty()
	
	def execute(self, context):

		scene = context.scene
		selected_row = scene.camera_list.highlighted_camera_index
		selected_camera_item = scene.cameras[selected_row]
		camera_name = selected_camera_item.name
				
		camera = bpy.data.objects[camera_name]
		if not camera or camera.type != "CAMERA":
			self.report({'WARNING'}, f"Camera {camera_name} not found - width not reset.")
			return {'CANCELLED'}
		
		if self.clear_dimension == "width":
			selected_camera_item.set_x_dim(None)
		else:
			selected_camera_item.set_y_dim(None)
		resize_passepartout(camera, selected_camera_item.x_dim, selected_camera_item.y_dim)
		return {'FINISHED'}





class CameraItemProperties(bpy.types.PropertyGroup):
	
	# Used to store the unique name of the camera
	name: bpy.props.StringProperty()

	def get_use_camera(self):
		obj = bpy.data.objects.get(self.name)
		if obj is not None and "use_camera" in obj.keys() and obj["use_camera"] is not None:
			return obj["use_camera"]
		else:
			return True

	def set_use_camera(self, value):
		obj = bpy.data.objects.get(self.name)
		if value in {True, False} and obj is not None and obj.type == "CAMERA":
			obj["use_camera"] = value
			
	use_camera: bpy.props.BoolProperty(
		name="Toggle camera membership of a subset used for rendering",
		get=get_use_camera,
		set=set_use_camera,
	)

	def get_x_dim(self):
		obj = bpy.data.objects.get(self.name)
		if obj is not None and "x_dim" in obj.keys() and obj["x_dim"] is not None:
			return obj["x_dim"]
		else:
			# Fallback to scene default
			return bpy.context.scene.render.resolution_x

	def set_x_dim(self, value):
		obj = bpy.data.objects.get(self.name)
		if obj is None or obj.type != "CAMERA":
			# Camera object not found
			return {'CANCELLED'}
		if value is None:
			# Clear the custom resolution
			# This prevents the camera to fake a custom setting when the user
			# changes the rendering resolution of the scene.
			obj["x_dim"] = None
		if obj is not None:
			obj["x_dim"] = value

	x_dim: bpy.props.IntProperty(
		name="Width of Render Border",
		get=get_x_dim,
		set=set_x_dim,
		min=1,
		max=10000,
	)

	def get_y_dim(self):
		obj = bpy.data.objects.get(self.name)
		if obj is not None and "y_dim" in obj.keys() and obj["y_dim"] is not None:
			return obj["y_dim"]
		else:
			# Fallback to scene default
			return bpy.context.scene.render.resolution_y

	def set_y_dim(self, value):
		obj = bpy.data.objects.get(self.name)
		if obj is None or obj.type != "CAMERA":
			# Camera object not found
			return {'CANCELLED'}
		if value is None:
			# Clear the custom resolution
			# This prevents the camera to fake a custom setting when the user
			# changes the rendering resolution of the scene.
			obj["y_dim"] = None
		if obj is not None:
			obj["y_dim"] = value

	y_dim: bpy.props.IntProperty(
		name="Height of Render Border",
		get=get_y_dim,
		set=set_y_dim,
		min=1,
		max=10000,		
	)
	
	def has_custom_resolution(self):
		obj = bpy.data.objects.get(self.name)
		return obj is not None and (("x_dim" in obj.keys() and obj["x_dim"] is not None) or ("y_dim" in obj.keys() and obj["y_dim"] is not None))



class CAMERA_LIST_PT_extra_features(bpy.types.Panel):
	bl_label = "Camera Assistant"
	bl_idname = "VIEW3D_PT_feature_list"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Render Resolutions'
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		layout = self.layout
		
		# Create a reference to the scene properties
		scene = context.scene
		
		# COMING FEATURE:	
		# The "Reformat camera name:" drop-down menu
		# row = layout.row()
		# row.label(text="Camera name:")
		# row.prop(scene, "reformat_camera_name", text="")
		
		
		# The "Adjust Lens Clip to show Render Border" checkbox
		row = layout.row()
		row.prop(scene, "move_focus_with_keys", text="Highlight selects Camera")
		
		# The "Adjust Lens Clip to show Render Border" checkbox
		row = layout.row()
		row.prop(scene, "adjust_lens_clip", text="Adjust Lens Clip if needed")

		# The "Always show Render Border" checkbox
		row = layout.row()
		row.prop(scene, "always_show_render_border", text="Always show Render Border")				
		
		# COMING FEATURES:
		# The "Adjust render size (keeping aspect ratio)" checkbox
		# row = layout.row()
		# row.prop(scene, "adjust_render_size", text="Scale render size:")
		
		# A box for "Aspect fit to:" drop-down menu and the text field
		#box = layout.box()
		
		# Set the enable state for the UI elements in the box
		# box_elements_enabled = scene.adjust_render_size
		
		# The "Aspect fit to:" drop-down menu
		# row = box.row()
		# row.enabled = box_elements_enabled
		# row.label(text="Aspect fit to:")
		# row.prop(scene, "aspect_fit_to", text="")
		
		# The text field
		# row = box.row()
		# row.enabled = box_elements_enabled
		# row.prop(scene, "custom_aspect_value", text="")
		
		# Add the informational text
		# layout.label(text="Process as you go, or click…")
		
		# Add the "Process All Now" button
		# layout.operator("camera_list.process_all_cameras", text="Process All Now")



# def update_aspect_fit_to(self, context):
# 		if self.aspect_fit_to == 'WIDTH':
# 			self.custom_aspect_value = context.scene.render.resolution_x
# 		elif self.aspect_fit_to == 'HEIGHT':
# 			self.custom_aspect_value = context.scene.render.resolution_y

def update_render_size(self, context):
	# Your code to handle the "Adjust render size (keeping aspect ratio)" checkbox logic
	pass

bpy.types.Scene.move_focus_with_keys = BoolProperty(
		name="Camera Follows Highlight",
		description="Highlight selects Camera",
		default=False
	)
	
bpy.types.Scene.adjust_lens_clip = BoolProperty(
	name="Adjust Lens Clip",
	description="Adjust Lens Clip to show Render Border",
	default=False
)

bpy.types.Scene.always_show_render_border = BoolProperty(
	name="Always show Render Border",
	description="Prevents Render Border from auto-hiding",
	default=False
)

# bpy.types.Scene.adjust_render_size = BoolProperty(
# 	name="Adjust render size",
# 	description="The aspect ratio will be ratined.",
# 	default=False,
# 	update=update_render_size,
# )

# bpy.types.Scene.aspect_fit_to = EnumProperty(
# 	name="Aspect fit to",
# 	description="Choose the dimension to fit the aspect ratio to",
# 	items=[
# 		("WIDTH", "Width", "Fit aspect ratio to width"),
# 		("HEIGHT", "Height", "Fit aspect ratio to height"),
# 	],
# 	default="WIDTH",
# 	update=update_aspect_fit_to,
# )

# bpy.types.Scene.reformat_camera_name = EnumProperty(
# 	name="Reformat camera name",
# 	description="Choose how to reformat the camera name",
# 	items=[
# 		("LEAVE", "Leave as is", "Do not change the camera name format"),
# 		("SNAKE", "snake_case", "Format the camera name in snake_case"),
# 		("CAMEL", "camelCase", "Format the camera name in camelCase"),
# 		("PASCAL", "PascalCase", "Format the camera name in PascalCase"),
# 		("TITLErπ", "Title Case", "Format the camera name in Title Case"),
# 	],
# 	default="LEAVE",
# )

# bpy.types.Scene.custom_aspect_value = IntProperty(
# 	name="Size of selected side",
# 	description="Enter the length of the fixed side.",
# )

# bpy.types.Scene.custom_aspect_value = bpy.props.IntProperty(
# 	name="Custom aspect value",
# 	description="Enter a custom aspect value",
# 	default=0,
# 	min=0,
# 	soft_max=10000,
# )

class PROCESS_OT_all_cameras(bpy.types.Operator):
	bl_idname = "camera_list.process_all_cameras"
	bl_label = "Process All Cameras"
	
	def execute(self, context):
		# Your code to process all cameras
		return {'FINISHED'}


class CAMERA_LIST_PT_render_panel(bpy.types.Panel):
	bl_label = "Camera List"	
	bl_idname = "VIEW3D_PT_camera_list"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Render Resolutions'
	
	def draw(self, context):
		layout = self.layout
		
		scene = bpy.context.scene
		cameras = scene.cameras
		camera_list = scene.camera_list
	
		# The List of Cameras
		
		row = layout.row()
		row.template_list("CAMERA_UL_custom_resolution_camera_list", "", scene, "cameras", camera_list, "highlighted_camera_index", rows=5)
		
		# The dimensions of the render border
	
		if len(cameras) > 0:
			# selected_camera = bpy.data.objects.get(cameras[camera_list.highlighted_camera_index].name)
			list_index = camera_list.highlighted_camera_index 
			camera_item = cameras[list_index]
			if camera_item is not None:
				# Add X and Y dimension text fields and reset buttons
				row = layout.row(align=True)
				row.prop(camera_item, "x_dim", text="Width")
				row.operator("camera_list.reset_custom_dimension", text="", icon='LOOP_BACK').clear_dimension="width"
	
				row = layout.row(align=True)
				row.prop(camera_item, "y_dim", text="Height")
				row.operator("camera_list.reset_custom_dimension", text="", icon='LOOP_BACK').clear_dimension="height"
					
		else:
			# Draw the update button spanning two columns
			row = layout.row(align=True)
			row.scale_y = 2
			row.operator("scene.update_camera_list_operator", text="Refresh Camera List")
	
		# Render buttons
		
		selected_camera_items = [camera_item for camera_item in bpy.context.scene.cameras if camera_item.use_camera]
		selected_camera_count = len(selected_camera_items)
		
		if selected_camera_count > 0:
			render_selection_text = f"Render {selected_camera_count}"
			render_selection_toggle = True			
		else:
			render_selection_text = "Render None"
			render_selection_toggle = False
		
		row = layout.row(align=True)
		row.operator("render.confirm_dialog_selected_cameras", text=render_selection_text) #, icon="OUTPUT")
		#op.enabled = render_selection_toggle
		
		row.operator("render.confirm_dialog_all_cameras", text="Render All") #, icon="OUTPUT")
		

bpy.types.Object.y_dim = bpy.props.IntProperty(
			name="Height",
			description="Enter a positive integer value for the height",
			default=1,
			min=1,
			soft_max=10000,
		)
		
def get_selected_camera_count():
		selected_camera_items = [camera_item for camera_item in bpy.context.scene.cameras if camera_item.use_camera]
		camera_count = len(selected_camera_items)
		return f"Render {camera_count}"



class CAMERA_UL_custom_resolution_camera_list(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			scene = context.scene
			valid_camera = bpy.data.objects.get(item.name)
			if valid_camera is not None and valid_camera.type == "CAMERA":
				row = layout.row(align=True)

				camera_item = scene.cameras[index]			
				
				# CHECKBOX: Toggles the selected state of a camera, allowing user
				# to decide to include or exclude it from Render Selected
				
				use_camera_checkbox = 'CHECKBOX_HLT' if camera_item.use_camera else 'CHECKBOX_DEHLT'
				row.operator("camera_list.toggle_use_camera", text="", icon=use_camera_checkbox, emboss=False).camera_name = item.name

				# NAME: Name of the camera
				# Click to modify dimensions of camera.
				# Double click to modify name.
				row.prop(valid_camera, "name", text="", emboss=False)


				# WRENCH: shows as filled when camera has custom dimensions
				has_been_customized = camera_item.has_custom_resolution()
				modifier_icon = 'MODIFIER_ON' if has_been_customized else 'MODIFIER_OFF'

				# Pass the index of the current row to the entry button operator
				row.operator("camera_list.clear_scene_resolution", text="", icon=modifier_icon, emboss=False).camera_index = index

				# RENDER STILL: render the camera to the Render Viewer using custom resolution—if there is one.
				row.operator("render.render_still_with_custom_resolution", text="", icon='RENDER_STILL', emboss=False).camera_name = camera_item.name
				
				if not context.scene.move_focus_with_keys:	
					# Add operator to select camera and set it as the current rendering camera when the row is clicked
					camera_select_op = row.operator("scene.highlight_and_select_camera", text="", icon='OUTLINER_DATA_CAMERA', emboss=False)
					camera_select_op.camera_name = camera_item.name
					camera_select_op.row_index = index
				

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text="", icon='CAMERA_DATA')



class CAMERA_LIST_OT_highlight_and_select_camera(bpy.types.Operator):
	bl_idname = "scene.highlight_and_select_camera"
	bl_label = "Highlight Camera in Camera List and make it Scene Camera"
	
	camera_name: bpy.props.StringProperty(name="Camera Name")
	row_index: bpy.props.IntProperty()
	
	def execute(self, context):			
		bpy.context.scene.camera_list.highlighted_camera_index = self.row_index
		print(f"NAME: {self.camera_name} ROW: {self.row_index}")
		bpy.ops.scene.select_camera(camera_name=self.camera_name, row_index=self.row_index)
		return {'FINISHED'}


class CAMERA_LIST_OT_select_camera(bpy.types.Operator):
	bl_idname = "scene.select_camera"
	bl_label = "Select Camera"

	camera_name: bpy.props.StringProperty(name="Camera Name")
	row_index: bpy.props.IntProperty()
	
	def execute(self, context):
		camera = bpy.data.objects.get(self.camera_name)
		if camera is not None:
		
			# Select the camera in the scene
			bpy.ops.object.select_all(action='DESELECT')
			camera.select_set(True)
			context.view_layer.objects.active = camera
			
			# Set the camera as the current rendering camera
			context.scene.camera = camera
			
			# The formula for the relationship between camera object size and clip start is:
			maximum_clip_start_to_avoid_hiding_render_border = 1.465 * camera.scale.x - 0.0158

			if camera.data.clip_start > maximum_clip_start_to_avoid_hiding_render_border:
				if context.scene.adjust_lens_clip:
					camera.data.clip_start = min(1.3888888, maximum_clip_start_to_avoid_hiding_render_border)
					self.report({'INFO'}, f"Adjusted camera clip start to: {maximum_clip_start_to_avoid_hiding_render_border}")
				else:
					rounded_value = round(maximum_clip_start_to_avoid_hiding_render_border, 4)
					self.report({'WARNING'}, f"Reduce Camera Lens Clip Start to below {rounded_value} if the Render Border is clipped (hidden).")
			else:
				rounded_x = round(camera.scale.x, 6)
				rounded_y = round(camera.scale.y, 6)
				rounded_z = round(camera.scale.z, 6)				
				if not (rounded_x == rounded_y == rounded_z):
					self.report({'WARNING'}, "Non-uniform camera scale affects the Multi-Camera Render Border and rendering result.")

		return {'FINISHED'}
		
		
		
		
class CAMERA_LIST_OT_update_camera_list(bpy.types.Operator):
	bl_idname = "scene.update_camera_list_operator"
	bl_label = "Update Camera List"

	scene_name = bpy.props.StringProperty()

	def execute(self, context):
		scene = bpy.context.scene
		if scene is not None:
			update_camera_list(scene)
		return {'FINISHED'}




class CAMERA_LIST_OT_toggle_use_camera(bpy.types.Operator):
	bl_idname = "camera_list.toggle_use_camera"
	bl_label = "Toggle Selection"
	bl_description = "Enable to include Camera when using Render Selected below"

	camera_name: bpy.props.StringProperty()

	def execute(self, context):
		camera_item = context.scene.cameras[self.camera_name]
		if camera_item is None:
			self.report({'WARNING'}, f"Failed to toggle camera - {self.camera_name} not found.")
			return {'CANCELLED'}
		camera_item.use_camera = not camera_item.use_camera
		context.area.tag_redraw()
		return {'FINISHED'}
	
	def invoke(self, context, event):
		if event.alt:
			# Toggle selection state to all cameras
			camera_item = context.scene.cameras[self.camera_name]
			if camera_item is not None:
				camera_item.use_camera = not camera_item.use_camera
				new_toggle_state = camera_item.use_camera
				for camera_item in context.scene.cameras:
					camera_item.use_camera = new_toggle_state
				context.area.tag_redraw()
			return {'FINISHED'}
		else:
			self.report({'INFO'}, "TIP: Opt+Click / Alt+Click to toggle all Cameras.")
			return self.execute(context)



class RENDER_OT_render_custom_resolution(bpy.types.Operator):
	bl_idname = "render.render_still_with_custom_resolution"
	bl_label = "Render Camera"
	bl_description = "Will use Costum Resolution if set"

	camera_name: bpy.props.StringProperty()

	def execute(self, context):
		camera_item = None
		for item in context.scene.cameras:
			if item.name == self.camera_name:
				camera_item = item
				break
	
		if camera_item is not None:
			camera = bpy.data.objects.get(self.camera_name)
			if camera is not None and camera.type == 'CAMERA':
				# Store the current resolution
				original_resolution_x = context.scene.render.resolution_x
				original_resolution_y = context.scene.render.resolution_y
	
				# Set the custom resolution from the selected camera
				context.scene.render.resolution_x = camera_item.x_dim
				context.scene.render.resolution_y = camera_item.y_dim
	
				# Store the current active camera
				original_active_camera = context.scene.camera
	
				# Set the active camera to the selected camera
				context.scene.camera = camera
	
				self.report({'INFO'}, f"Rendering {camera.name} - interface will become more or less unresponsive.")
	
				# Render the image
				bpy.ops.render.render('EXEC_DEFAULT', write_still=True)
	
				# Restore the original active camera
				context.scene.camera = original_active_camera
	
				# Restore the original resolution
				context.scene.render.resolution_x = original_resolution_x
				context.scene.render.resolution_y = original_resolution_y
	
				# Update the area to refresh the UI
				context.area.tag_redraw()
				
				self.report({'INFO'}, f"Rendered camera to Blender Render window (may not update automatically).")
	
		return {'FINISHED'}


def render_images(scene, cameras_to_render):
	
	# Retain original camera details
	original_camera = scene.camera
	original_resolution_x = scene.render.resolution_x
	original_resolution_y = scene.render.resolution_y
			
	# get output path
	file_path = bpy.path.abspath(scene.render.filepath)
	file_dir = os.path.dirname(file_path)
	if not file_dir:
		file_dir = bpy.path.abspath("//")
	
	# Starting state
	render_progress = 1 # Yeah, feels right to start on 1.
	number_of_cameras_to_render = len(cameras_to_render)
	start_time = time.time()
	
	# Render each camera with custom resolution, or default resolution if not set
	for camera_data in cameras_to_render:
	
		camera = bpy.data.objects.get(camera_data.name)
		if not camera:
			self.report({'WARNING'}, f"Camera {camera_data.camera_name} not found")
			continue
			
		# set camera as active
		scene.camera = camera
		
		# set resolution
		scene.render.resolution_x = camera_data.x_dim
		scene.render.resolution_y = camera_data.y_dim
		
		# set output path
		camera_file_path = os.path.join(file_dir, f"{camera_data.name} {camera_data.x_dim} × {camera_data.y_dim}.png")
		scene.render.filepath = bpy.path.ensure_ext(camera_file_path, ".png")
		
		print(f"\nRendering {render_progress} of {number_of_cameras_to_render}: \"{camera.name}\". Interface will become more or less unresponsive.")
		
		# render
		bpy.ops.render.render(write_still=True)
					
		render_progress += 1
	
	# Done Rendering
	
	# Restore original camera and resolution
	scene.camera = original_camera
	scene.render.resolution_x = original_resolution_x
	scene.render.resolution_y = original_resolution_y
	
	# Record the end time
	end_time = time.time()
	
	# Calculate the time taken in seconds
	time_taken = end_time - start_time
	
	# Convert the time taken to hours, minutes, and seconds
	hours, rem = divmod(time_taken, 3600)
	minutes, seconds = divmod(rem, 60)
	
	# Display the time taken in hours, minutes, and seconds format
	formatted_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
	print("\nTotal time taken for rendering: ", formatted_time)
	
	if len(cameras_to_render) == 1:
		return f"Rendered camera to {file_dir}"
	else:
		return f"Rendered {number_of_cameras_to_render} cameras to {file_dir}"
	
	
	
	

class CAMERA_LIST_OT_clear_custom_resolution(bpy.types.Operator):
	bl_idname = "camera_list.clear_scene_resolution"
	bl_label = "Clear Custom Dimensions"
	bl_description = "Restores the camera to default dimensions"
	bl_options = {'UNDO'}
	
	camera_index: bpy.props.IntProperty()

	def execute(self, context):
		camera_item = context.scene.cameras[self.camera_index]

		if camera_item:
		
			# Modify the X and Y dimensions
			camera_item.set_x_dim(None)
			camera_item.set_y_dim(None)
			
			camera = bpy.data.objects.get(camera_item.name)
			if not camera and camera.type != "CAMERA":
				self.report({'WARNING'}, f"Camera {camera_data.camera_name} not found")
				return {'FINISHED'}

			resize_passepartout(camera, camera_item.x_dim, camera_item.y_dim)
			
			self.report({'INFO'}, "You can Opt+Click / Alt+Click to clear custom resolution from all cameras.")

		return {'FINISHED'}


	def invoke(self, context, event):
		if event.alt:
			# Clear custom resolution from all cameras
			for camera_item in context.scene.cameras:
			
				# Modify the X and Y dimensions
				camera_item.set_x_dim(None)
				camera_item.set_y_dim(None)
			
			camera_item = context.scene.cameras[self.camera_index]
			camera = bpy.data.objects.get(camera_item.name)
			if not camera:
				# No camera is selected, no need to update the render border
				return {'FINISHED'}

			resize_passepartout(camera, camera_item.x_dim, camera_item.y_dim)
			context.area.tag_redraw()
			return {'FINISHED'}
		
		else:			
			return self.execute(context)
	


# Confirmation dialog box
class RENDER_OT_confirm_dialog_render_all(bpy.types.Operator):
	bl_idname = "render.confirm_dialog_all_cameras"
	bl_label = "RENDER ALL CAMERAS"
	bl_description = "Render all Cameras in the Scene"


	def execute(self, context):
		scene = context.scene
		
		if not scene.cameras:
			self.report({'WARNING'}, "No cameras in scene")
			return {'CANCELLED'}
			
		render_feedback = render_images(scene, scene.cameras)
		self.report({'INFO'}, render_feedback)
		
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=200)

	def draw(self, context):
		layout = self.layout
		
		box = layout.box()  # Create a box layout
		col = box.column()
		col.label(text="Launch Blender from the terminal")
		col.label(text="to see Render Progress.")
		col = box.column()
		col.label(text="Try Ctrl+C in Python Console")
		col.label(text="to cancel the rendering.")

		col = layout.column()
		col.label(text=f"Proceed to render all Cameras?")  # Add another line of text here

# Confirmation dialog box
#class RENDER_OT_confirm_dialog_render_selected(bpy.types.Operator):
#	bl_idname = "render.confirm_dialog_selected_cameras"
#	bl_label = "Start rendering selected cameras?"
#
#	def execute(self, context):
#		bpy.ops.render.selected_cameras()
#		return {'FINISHED'}
#
#	def invoke(self, context, event):
#		return context.window_manager.invoke_props_dialog(self)

class RENDER_OT_confirm_dialog_render_selected(bpy.types.Operator):
		bl_idname = "render.confirm_dialog_selected_cameras"
		bl_label = "RENDER SELECTED CAMERAS"
		bl_description = "Render only Cameras that are Selected in the list above"
		
		def execute(self, context):
			scene = context.scene
			selected_camera_items = [camera_item for camera_item in scene.cameras if camera_item.use_camera]
			if not selected_camera_items:
				self.report({'WARNING'}, "No cameras selected")
				return {'CANCELLED'}
				
			render_feedback = render_images(scene, selected_camera_items)
			self.report({'INFO'}, render_feedback)
			return {'FINISHED'}
		
		def invoke(self, context, event):
			selected_camera_count = len([camera_item for camera_item in bpy.context.scene.cameras if camera_item.use_camera])
			if selected_camera_count > 0:
				return context.window_manager.invoke_props_dialog(self, width=200)
			else:
				self.report({'WARNING'}, "Please select at least one Camera from the list above.")
				return {"CANCELLED"}
		
		def draw(self, context):
			layout = self.layout

			box = layout.box()  # Create a box layout
			col = box.column()
			col.label(text="Launch Blender from the terminal")
			col.label(text="to see Render Progress.")
			col = box.column() # Creates a bit more space
			col.label(text="Try Ctrl+C in Python Console")
			col.label(text="to cancel the rendering.")
			
			selected_camera_items = [camera_item for camera_item in bpy.context.scene.cameras if camera_item.use_camera]
			camera_count = len(selected_camera_items)
									
			col = layout.column()
			col.label(text=f"Proceed to render {camera_count} cameras?")  # Add another line of text here



@persistent
def update_camera_list(scene, depsgraph=None):
	scene.cameras.clear()
	for obj in scene.objects:
		if obj.type == 'CAMERA':
			item = scene.cameras.add()
			item.name = obj.name
			# The other properties have a default value.
			




def resize_passepartout(camera, width, height):

	# A factor that results in the correct placement of the render border
	# exactly at the front plane of the camera object.
	factor = 0.5

	# The ratio is used to scale the rendering border, as the shortest side
	# should match the same edge of the FOV.
	render_ratio = height/width
	
	# Scaling the sides to match behavior of Blender, so the rendering border
	# ends up showing what will actually be rendered.
	if render_ratio > 1:
		half_width = factor / render_ratio
		half_height = factor
	else:
		half_width = factor
		half_height = factor * render_ratio

	# Calculate the optimal distance using the camera's FOV
	optimal_distance = factor / math.tan(camera.data.angle / 2)
	distance = max(camera.data.clip_start, optimal_distance)
	
	# Scaling render border according to distance, so it always looks same same in view finder.
	if distance > optimal_distance:
		half_width = half_width * (distance / optimal_distance)
		half_height = half_height * (distance / optimal_distance)
	
	# Somehow the clip start, camera object scale affects optimal distance for the render border.
	# How to ensure the optimal distance is within the camera's scaled clip range?
	#
	# What I have observed:
	#
	# • The camera object scale affects clip start
	# • Default clip start is 0.1
	# • Default camera object scale is 1
	# • At a camera object scale lower than 0.072012 the render border is clipped (hidden)
	# • Distance from position to camera and render border is 1.3888889188714615 which is also relative to camera object scale
	#
	# For now, I'll just issue a warning when camera is selected.

	verts = [
		(-half_width, -half_height, -distance),  # Make the Z coordinate negative
		(half_width, -half_height, -distance),  # Make the Z coordinate negative
		(half_width, half_height, -distance),  # Make the Z coordinate negative
		(-half_width, half_height, -distance),  # Make the Z coordinate negative
	]

	edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
	faces = []

	mesh = bpy.data.meshes.get(key_mesh)
	if mesh is None:
		mesh = bpy.data.meshes.new(key_mesh)
	else:
		mesh.clear_geometry()
	
	mesh.from_pydata(verts, edges, faces)
	mesh.update()
	
	passepartout = bpy.data.objects.get(key_passepartout)
	if passepartout is None:
		passepartout = bpy.data.objects.new(key_passepartout, mesh)
		bpy.context.collection.objects.link(passepartout)
	
	passepartout.data = mesh

	passepartout.parent = camera
	passepartout.hide_render = True
	passepartout.hide_select = True
	
	return passepartout



@persistent
def update_multiresolution_camera_frame(scene):
	# Get the active object and check if it is a camera
	active_object = bpy.context.active_object

	# Get existing passepartout, if there is one
	passepartout = bpy.data.objects.get(key_passepartout)
	
	if active_object and active_object.type == 'CAMERA':
		selected_camera = active_object

		# Check if the selected camera is in the list of cameras with custom dimensions
		custom_camera = bpy.context.scene.cameras.get(selected_camera.name)
		if custom_camera and (custom_camera.x_dim != bpy.context.scene.render.resolution_x or custom_camera.y_dim != bpy.context.scene.render.resolution_y):
			# Show the passepartout for the active camera with custom dimensions
			passepartout = resize_passepartout(selected_camera, custom_camera.x_dim, custom_camera.y_dim)
			passepartout.hide_viewport = False
		else:
			# Hiding passepartout since the selected camera does not have custom dimensions
			if passepartout:
				passepartout.hide_viewport = True
			
					
		# Link the passepartout to the selected camera
		if passepartout:
			passepartout.parent = selected_camera
			passepartout.matrix_world = selected_camera.matrix_world

	else:
		# Hide the passepartout if no camera is selected - and the user wants it hidden
		if passepartout and not bpy.context.scene.always_show_render_border:
			passepartout.hide_viewport = True





classes = (
	CameraListProperties,
	CameraItemProperties,

	CAMERA_LIST_PT_render_panel,
	CAMERA_UL_custom_resolution_camera_list,
	
	CAMERA_LIST_OT_clear_custom_resolution,
	CAMERA_LIST_OT_clear_custom_size,
	CAMERA_LIST_OT_toggle_use_camera,
	CAMERA_LIST_OT_select_camera,
	CAMERA_LIST_OT_highlight_and_select_camera,
	CAMERA_LIST_OT_update_camera_list,
	CAMERA_LIST_PT_extra_features,
	
	PROCESS_OT_all_cameras,

	RENDER_OT_render_custom_resolution,
	RENDER_OT_confirm_dialog_render_all,
	RENDER_OT_confirm_dialog_render_selected,
)




def register():
	
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.camera_list = bpy.props.PointerProperty(type=CameraListProperties)

	bpy.types.Scene.cameras = bpy.props.CollectionProperty(
		type=CameraItemProperties,
		 description="List of properties for each camera in the scene")
		 
	bpy.types.Scene.passepartout_width = bpy.props.IntProperty(
		name="Width",
		description="Passepartout width",
		default=500,
		min=1,
		soft_max=10000
	)
	
	bpy.types.Scene.passepartout_height = bpy.props.IntProperty(
		name="Height",
		description="Passepartout height",
		default=300,
		min=1,
		soft_max=10000
	)
	
	# bpy.context.scene.custom_aspect_value = bpy.context.scene.render.resolution_x
	
	# Register the depsgraph update handler
	bpy.app.handlers.depsgraph_update_post.append(update_multiresolution_camera_frame)
	bpy.app.handlers.depsgraph_update_post.append(update_camera_list)




def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.camera_list
	del bpy.types.Scene.cameras
	
	# Try to remove the passepartout
	passepartout = bpy.data.objects.get(key_passepartout)
	if passepartout:
		# Delete passepartout from the scene
		bpy.data.objects.remove(passepartout, do_unlink=True)
	
	# Unregister the depsgraph update handler
	bpy.app.handlers.depsgraph_update_post.remove(update_multiresolution_camera_frame)	
	bpy.app.handlers.depsgraph_update_post.remove(update_camera_list)
	
	# Remove the custom_aspect_value property
	# del bpy.types.Scene.custom_aspect_value


if __name__ == "__main__":
	register()
