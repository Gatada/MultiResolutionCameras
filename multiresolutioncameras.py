bl_info = {
	"name": "Multi-Resolution Cameras",
	"author": "Johan Basberg",
	"version": (1, 1),
	"blender": (3, 0, 0),
	"location": "View3D > Sidebar [N] > Render Resolutions",
	"description": "Easily customize resolutions and render your cameras.",
	"category": "3D View",
}

import bpy
import os


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
	
		row = layout.row()
		row.template_list("CAMERA_UL_custom_resolution_camera_list", "", scene, "cameras", camera_list, "highlighted_camera_index", rows=10)
	
		if len(cameras) > 0:
			selected_camera = bpy.data.objects.get(cameras[camera_list.highlighted_camera_index].name)
			if selected_camera is not None and selected_camera.type == 'CAMERA':
				# Add X and Y dimension text fields and reset buttons
				row = layout.row(align=True)
				row.prop(selected_camera, '["x_dim"]', text="X")
				row.operator("camera_list.reset_x_dimension", text="", icon='LOOP_BACK')
	
				row = layout.row(align=True)
				row.prop(selected_camera, '["y_dim"]', text="Y")
				row.operator("camera_list.reset_y_dimension", text="", icon='LOOP_BACK')
		else:
			layout.label(text="No cameras available")
	
		row = layout.row(align=True)
		row.operator("camera_list.button_1", text="Selected", icon="OUTPUT")
		row.operator("camera_list.button_2", text="Render All")




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
				

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text="", icon='CAMERA_DATA')




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
				print(f"Active camera: {camera.name}") # Debug statement

	
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




class CAMERA_LIST_OT_Button1(bpy.types.Operator):
	bl_idname = "camera_list.button_1"
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




class CAMERA_LIST_OT_Button2(bpy.types.Operator):
	bl_idname = "camera_list.button_2"
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




def update_camera_list(scene):
	scene.cameras.clear()
	for obj in scene.objects:
		if obj.type == 'CAMERA':
			item = scene.cameras.add()
			item.name = obj.name

			if "x_dim" not in obj.keys():
				obj["x_dim"] = bpy.context.scene.render.resolution_x

			if "y_dim" not in obj.keys():
				obj["y_dim"] = bpy.context.scene.render.resolution_y




classes = (
	CameraListProperties,
	CameraItemProperties,
	CameraListPanel,
	CAMERA_UL_custom_resolution_camera_list,
	CAMERA_LIST_OT_Button1,
	CAMERA_LIST_OT_Button2,
	CAMERA_LIST_OT_EntryButton1,
	CAMERA_LIST_OT_ResetXDimension,
	CAMERA_LIST_OT_ResetYDimension,
	CAMERA_LIST_OT_toggle_use_camera,
	CAMERA_LIST_OT_render_custom_resolution,
)




def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.camera_list = bpy.props.PointerProperty(type=CameraListProperties)
	bpy.types.Scene.cameras = bpy.props.CollectionProperty(type=CameraItemProperties)
	bpy.app.handlers.depsgraph_update_post.append(update_camera_list)




def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.camera_list
	del bpy.types.Scene.cameras
	bpy.app.handlers.depsgraph_update_post.remove(update_camera_list)




if __name__ == "__main__":
	register()