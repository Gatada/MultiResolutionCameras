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
	"version": (2, 5),
	"blender": (3, 0, 0),
	"location": "View3D > Sidebar [N] > Render Resolutions",
	"description": "Easily customize resolutions and render your cameras.",
	"category": "3D View",
}

import math
import bpy
import os
from bpy.app.handlers import persistent


key_mesh = "Multi-Resolution Camera Mesh"
key_passepartout = "Multi-Resolution Camera Frame"


class CameraListProperties(bpy.types.PropertyGroup):
	highlighted_camera_index: bpy.props.IntProperty(
		name="Click to modify dimensions.")



class CAMERA_LIST_OT_ResetXDimension(bpy.types.Operator):
	bl_idname = "camera_list.reset_x_dimension"
	bl_label = "Reset X Dimension"
	bl_description = "Restores default scene value"

	def execute(self, context):
		scene = context.scene
		camera_list = scene.camera_list
		selected_camera = scene.cameras[camera_list.highlighted_camera_index]
		selected_camera.x_dim = bpy.context.scene.render.resolution_x
		bpy.data.objects[selected_camera.name]["x_dim"] = selected_camera.x_dim
		return {'FINISHED'}


class CAMERA_LIST_OT_ResetYDimension(bpy.types.Operator):
	bl_idname = "camera_list.reset_y_dimension"
	bl_label = "Reset Y Dimension"
	bl_description = "Restores default scene value"	

	def execute(self, context):
		scene = context.scene
		camera_list = scene.camera_list
		selected_camera = scene.cameras[camera_list.highlighted_camera_index]
		selected_camera.y_dim = bpy.context.scene.render.resolution_y
		bpy.data.objects[selected_camera.name]["y_dim"] = selected_camera.y_dim
		return {'FINISHED'}



class CameraItemProperties(bpy.types.PropertyGroup):

	name: bpy.props.StringProperty()

	def get_use_camera(self):
		return self.get("use_camera", True)


	def set_use_camera(self, value):
		self["use_camera"] = value
			

	bpy.types.Object.use_camera = bpy.props.BoolProperty(name="Use Camera", default=True)

	def get_x_dim(self):
		obj = bpy.data.objects.get(self.name)
		if obj is not None and "x_dim" in obj.keys():
			return obj["x_dim"]
		else:
			return bpy.context.scene.render.resolution_x

	def set_x_dim(self, value):
		obj = bpy.data.objects.get(self.name)
		if obj is not None:
			obj["x_dim"] = value

	x_dim: bpy.props.IntProperty(
		name="X Dimension",
		get=get_x_dim,
		set=set_x_dim,
	)

	def get_y_dim(self):
		obj = bpy.data.objects.get(self.name)
		if obj is not None and "y_dim" in obj.keys():
			return obj["y_dim"]
		else:
			return bpy.context.scene.render.resolution_y

	def set_y_dim(self, value):
		obj = bpy.data.objects.get(self.name)
		if obj is not None:
			obj["y_dim"] = value

	y_dim: bpy.props.IntProperty(
		name="Y Dimension",
		get=get_y_dim,
		set=set_y_dim,
	)





class CameraListPanel(bpy.types.Panel):
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
		row.template_list("CAMERA_UL_custom_resolution_camera_list", "", scene, "cameras", camera_list, "highlighted_camera_index", rows=10)
			
	
		if len(cameras) > 0:
			selected_camera = bpy.data.objects.get(cameras[camera_list.highlighted_camera_index].name)
			if selected_camera is not None and selected_camera.type == 'CAMERA':
				# Add X and Y dimension text fields and reset buttons
				row = layout.row(align=True)
				row.prop(selected_camera, '["x_dim"]', text="Width")
				row.operator("camera_list.reset_x_dimension", text="", icon='LOOP_BACK')
	
				row = layout.row(align=True)
				row.prop(selected_camera, '["y_dim"]', text="Height")
				row.operator("camera_list.reset_y_dimension", text="", icon='LOOP_BACK')
		else:
			# Draw the update button spanning two columns
			row = layout.row(align=True)
			row.scale_y = 2
			row.operator("scene.update_camera_list_operator", text="Refresh Camera List")
	
		row = layout.row(align=True)
		row.operator("render.selected_cameras", text="Selected", icon="OUTPUT")
		row.operator("render.all_cameras", text="Render All")




class CAMERA_UL_custom_resolution_camera_list(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			camera = bpy.data.objects.get(item.name)
			if camera is not None:
				row = layout.row(align=True)
				
				# CHECKBOX: Toggles the selected state of a camera, allowing user to decide to include or exclude it from Render Selected

				use_camera_icon = 'CHECKBOX_HLT' if camera.use_camera else 'CHECKBOX_DEHLT'
				toggle_op = row.operator("camera_list.toggle_use_camera", text="", icon=use_camera_icon, emboss=False)
				toggle_op.camera_name = item.name


				# NAME: Name of the camera
				# Click to modify dimensions of camera.
				# Double click to modify name.
				
				row.prop(camera, "name", text="", emboss=False)


				# WRENCH: shows as filled when camera has custom dimensions
				
				custom_dimensions = (
					camera['x_dim'] != context.scene.render.resolution_x
					or camera['y_dim'] != context.scene.render.resolution_y
				)
				
				modifier_icon = 'MODIFIER_ON' if custom_dimensions else 'MODIFIER_OFF'

				# Pass the index of the current row to the entry button operator
				row.operator("camera_list.entry_button_1", text="", icon=modifier_icon, emboss=False).camera_index = index
				

				# RENDER STILL: render the camera to the Render Viewer using custom resolution—if there is one.
					
				render_op = row.operator("camera_list.render_custom_resolution", text="", icon='RENDER_STILL', emboss=False)
				render_op.camera_name = camera.name
				
								
				# Add operator to select camera and set it as the current rendering camera when the row is clicked
				camera_select_op = row.operator("camera_list.select_camera", text="", icon='OUTLINER_DATA_CAMERA', emboss=False)
				camera_select_op.camera_name = camera.name
				camera_select_op.row_index = index
				

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text="", icon='CAMERA_DATA')




class CAMERA_OT_select_camera(bpy.types.Operator):
	bl_idname = "camera_list.select_camera"
	bl_label = "Select Camera"

	camera_name: bpy.props.StringProperty(name="Camera Name")
	row_index: bpy.props.IntProperty()
	
	def execute(self, context):

		# Highlighting clicked row
		bpy.context.scene.camera_list.highlighted_camera_index = self.row_index

	
		camera = bpy.data.objects.get(self.camera_name)
		if camera is not None:
		
			# Select the camera in the scene
			bpy.ops.object.select_all(action='DESELECT')
			camera.select_set(True)
			context.view_layer.objects.active = camera
			
			# Set the camera as the current rendering camera
			context.scene.camera = camera
			
			if camera.scale.x != camera.scale.y != camera.scale.z:
				self.report({'WARNING'}, f"Non-uniform camera scale affects the Multi-Camera Render Border and rendering result.")
			elif camera.scale.x < 0.073 and camera.data.clip_start < 0.1:
				self.report({'WARNING'}, f"Current camera scale and clip start settings might hide the Multi-Camera Render Border.")
			elif camera.data.clip_start > 1.37:
				self.report({'WARNING'}, f"Current camera Clip Start setting degrades the visibility of the Multi-Camera Render Border.")
			elif camera.data.clip_end < 1.38:
				self.report({'WARNING'}, f"Current camera Clip End will hide the Multi-Camera Render Border.")

		return {'FINISHED'}
		
		
		
		
class UpdateCameraListOperator(bpy.types.Operator):
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
		camera = bpy.data.objects.get(self.camera_name)
		
		if camera is not None:
			camera.use_camera = not camera.use_camera
			context.area.tag_redraw()
		return {'FINISHED'}




class CAMERA_LIST_OT_render_custom_resolution(bpy.types.Operator):
	bl_idname = "camera_list.render_custom_resolution"
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
				x_dim = camera_item.get_x_dim()
				y_dim = camera_item.get_y_dim()
				context.scene.render.resolution_x = x_dim
				context.scene.render.resolution_y = y_dim
	
				# Store the current active camera
				original_active_camera = context.scene.camera
	
				# Set the active camera to the selected camera
				context.scene.camera = camera
	
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




class RENDER_OT_render_selected_cameras(bpy.types.Operator):
	bl_idname = "render.selected_cameras"
	bl_label = "Render Selected Cameras"
	bl_description = "Render selected cameras"	
	
	def execute(self, context):
		scene = context.scene

		selected_cameras = [camera for camera in scene.cameras if bpy.data.objects.get(camera.name).use_camera]

		if not selected_cameras:
			self.report({'WARNING'}, "No cameras selected")
			return {'CANCELLED'}
		
		original_camera = scene.camera
		original_resolution_x = scene.render.resolution_x
		original_resolution_y = scene.render.resolution_y
		
		# get output path
		file_path = bpy.path.abspath(scene.render.filepath)
		file_dir = os.path.dirname(file_path)
		if not file_dir:
			file_dir = bpy.path.abspath("//")
		file_name = os.path.splitext(os.path.basename(file_path))[0]
		
		render_progress = 0
		cameras_to_render = len(selected_cameras)

		for camera_data in selected_cameras:
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
			
			self.report({'INFO'}, f"Rendering {render_progress} of {cameras_to_render}: {camera.name} - interface will become more or less unresponsive.")

			
			# render
			bpy.ops.render.render(write_still=True)
		
		# restore original camera and resolution
		scene.camera = original_camera
		scene.render.resolution_x = original_resolution_x
		scene.render.resolution_y = original_resolution_y
		
		if len(selected_cameras) == 1:
			# Normalize the path and extract the file name
			output_path = os.path.normpath(scene.render.filepath)
			self.report({'INFO'}, f"Rendered camera to {output_path}")
		else:
			# Normalize the path and extract the file name
			output_path = os.path.normpath(file_dir)
			self.report({'INFO'}, f"Rendered {len(selected_cameras)} cameras to {output_path}")

		return {'FINISHED'}




class RENDER_OT_render_all_cameras(bpy.types.Operator):
	bl_idname = "render.all_cameras"
	bl_label = "Render All Cameras"
	bl_description = "Renders all cameras with custom resolution if set"

	def execute(self, context):
		scene = context.scene
		
		if not scene.cameras:
			self.report({'WARNING'}, "No cameras in scene")
			return {'CANCELLED'}
		
		original_camera = scene.camera
		original_resolution_x = scene.render.resolution_x
		original_resolution_y = scene.render.resolution_y
				
		# get output path
		file_path = bpy.path.abspath(scene.render.filepath)
		file_dir = os.path.dirname(file_path)
		if not file_dir:
			file_dir = bpy.path.abspath("//")
			
		render_progress = 0
		cameras_to_render = len(scene.cameras)

		# Render each camera with custom resolution, or default resolution if not set
		for camera_data in scene.cameras:
	
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
			
			self.report({'INFO'}, f"Rendering {render_progress} of {cameras_to_render}: {camera.name} - interface will become more or less unresponsive.")
			
			# render
			bpy.ops.render.render(write_still=True)

		# restore original camera and resolution
		scene.camera = original_camera
		scene.render.resolution_x = original_resolution_x
		scene.render.resolution_y = original_resolution_y

		if len(scene.cameras) == 1:
			self.report({'INFO'}, f"Rendered camera to {file_dir}")
		else:
			self.report({'INFO'}, f"Rendered {len(scene.cameras)} cameras to {file_dir}")
		
		return {'FINISHED'}




class CAMERA_LIST_OT_EntryButton1(bpy.types.Operator):
	bl_idname = "camera_list.entry_button_1"
	bl_label = "Clear Custom Dimensions"
	bl_description = "Restores the camera to default dimensions"
	bl_options = {'UNDO'}
	
	camera_name: bpy.props.StringProperty()
	camera_index: bpy.props.IntProperty(default=0)

	def execute(self, context):
		camera = context.scene.cameras[self.camera_index]

		if camera:
		
			# Modify the X and Y dimensions
			camera.x_dim = context.scene.render.resolution_x
			camera.y_dim = context.scene.render.resolution_y
			
			self.report({'INFO'}, f"Successfully reset {camera.name} to {camera.x_dim}×{camera.y_dim}")

		return {'FINISHED'}




# Confirmation dialog box
class RENDER_OT_confirm_dialog(bpy.types.Operator):
    bl_idname = "render.confirm_dialog"
    bl_label = "Start Rendering?"

    render_method: bpy.props.StringProperty()

    def execute(self, context):
        if self.render_method == "selected_cameras":
            bpy.ops.render.render_selected_cameras()
        elif self.render_method == "all_cameras":
            bpy.ops.render.render_all_cameras()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)




@persistent
def update_camera_list(scene, depsgraph=None):
	scene.cameras.clear()
	for obj in scene.objects:
		if obj.type == 'CAMERA':
			item = scene.cameras.add()
			item.name = obj.name

			if "x_dim" not in obj.keys():
				obj["x_dim"] = bpy.context.scene.render.resolution_x

			if "y_dim" not in obj.keys():
				obj["y_dim"] = bpy.context.scene.render.resolution_y





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
			# Show the passepartout for the active camera
			passepartout = resize_passepartout(selected_camera, custom_camera.x_dim, custom_camera.y_dim)
			passepartout.hide_viewport = False
		else:
			# Hide the passepartout if the selected camera does not have custom dimensions
			if passepartout:
				passepartout.hide_viewport = True
			
					
		# Link the passepartout to the selected camera
		if passepartout:
			passepartout.parent = selected_camera
			passepartout.matrix_world = selected_camera.matrix_world

	else:
		# Hide the passepartout if no camera is selected
		if passepartout:
			passepartout.hide_viewport = True





classes = (
	CameraListProperties,
	CameraItemProperties,
	CameraListPanel,
	CAMERA_UL_custom_resolution_camera_list,
	RENDER_OT_render_selected_cameras,
	RENDER_OT_render_all_cameras,
	CAMERA_LIST_OT_EntryButton1,
	CAMERA_LIST_OT_ResetXDimension,
	CAMERA_LIST_OT_ResetYDimension,
	CAMERA_LIST_OT_toggle_use_camera,
	CAMERA_LIST_OT_render_custom_resolution,
	UpdateCameraListOperator,
	CAMERA_OT_select_camera,
	RENDER_OT_confirm_dialog,
	RENDER_OT_render_with_confirmation,
)




def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.camera_list = bpy.props.PointerProperty(type=CameraListProperties)

	bpy.types.Scene.cameras = bpy.props.CollectionProperty(
		type=CameraItemProperties,
		 description="List of cameras in the scene")
		 
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




if __name__ == "__main__":
	register()
