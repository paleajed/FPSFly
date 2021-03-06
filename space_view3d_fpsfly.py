# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__bpydoc__ = """\
The FPSFly addon facilitates a 3d view navigation mode using WASD + mouse for 
movement like in an FPS game.


Documentation


First go to User Preferences->Addons and enable the FPSFly addon in the 3d View category.
Press CTRL+SHIFT+F to enter navigation mode.  Click CTRL+SHIFT+F again or ESC to exit.
Also in N-panel is an on/off toggle.  Works in EditMode and Object Mode.
Use WASD (or ZQSD on Azerty) during navigation to move left/right forward/backward and mouse to look in
a certain direction (default RIGHTMOUSE needs to be kept pressed to do mouselook.
Also added EQ/EA for moving up/down.  update: now also X and V for down and SPACEBAR for up.
Use mousewheel to adjust speed.
Keep SHIFT pressed to run.
Check "Walkmode" to switch from fly to walk mode; youll always be at a fixed distance above one or
all objects; two options: "All", youll be walking on any object under you, or "Drop": youll drop down
and the first object you hit will be your ground object.
Teleport feature: point crosshair at any object, including ground and youll be teleported to the spot
you were pointing at.
Choose a ground object in the pulldown menu (Npanel) before entering nav mode
to use walkmode; in walkmode you are always at the same distance above the chosen
ground object, you can change this distance during nav by using Up/Down controls.
Press F during navigation to switch between walk and fly mode.

Only works in perspective mode!

Go to FPSFly Addon Preferences (UserPreferences->Addons->3D View->FPSFly and click arrow next to it) to change options :
Active/Passive mode :  always mouselook (passive=off) or when RIGHTMOUSE pressed (active=on).
Height : the default height above ground when walking on ground object.
Teleport Distance :  how close to the object youre teleported.
Scene Scale :  sets multiplier for Height and Teleport Distance
Navigation speed :  set flying speed.
Keyboard layout :  choose QWERTY or AZERTY.
Mouse sensitivity.
Mirror Y : opposite Y direction.
Key bindings: Set up to three keys/buttons for each control.


"""


bl_info = {
	"name": "FPSFly",
	"author": "Gert De Roost",
	"version": (0, 8, 5),
	"blender": (2, 6, 8),
	"location": "View3D > UI > FPSFly",
	"description": "FPS viewport navigation",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "3D View"}


import bpy
from bgl import glBegin, glColor3f, glVertex2f, glEnd, GL_LINES
from mathutils import Vector, Matrix, Color
import math
from bpy.app.handlers import persistent

			






class SetKey(bpy.types.Operator):
	bl_idname = "fpsfly.setkey"
	bl_label = "Set Key Binding"
	
	key = bpy.props.StringProperty()

	def execute(self, context):
	
		context.window_manager.modal_handler_add(self)
		
		self.addonprefs = context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
	
		isset = False
		if not(event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER', 'NONE'}):
			if event.value == 'PRESS':
				setattr(self.addonprefs, self.key, event.type)
				context.scene.update()
				isset = True
		
		if isset:
			context.region.tag_redraw()
			return {'FINISHED'}
		else:
			return {'RUNNING_MODAL'}



class FPSFlyPanel(bpy.types.Panel):
	bl_label = "FPSFly"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	def draw(self, context):
		
		scn = context.scene
		self.layout.operator("view3d.fpsfly", "Enter FPS navigation")
		self.layout.prop(scn, "FPS_Walk")
		if scn.FPS_Walk:
			self.layout.prop(scn, "FPS_GroundMode")
		


class FPSFlyAddonPreferences(bpy.types.AddonPreferences):

	bl_idname = "space_view3d_fpsfly"
	
	oldkeyboard = bpy.props.StringProperty(
			name = "Helper property", 
			description = "",
			default = "RIGHTMOUSE")

	mouselook = bpy.props.StringProperty(
			name = "Mouselook Button/Key", 
			description = "Key binding for mouselook",
			default = "RIGHTMOUSE")

	teleport = bpy.props.StringProperty(
			name = "Teleport Button/Key", 
			description = "Key binding for teleport",
			default = "T")

	walkmode = bpy.props.StringProperty(
			name = "Switch walk/fly mode Button/Key", 
			description = "Key binding for switching walk/fly mode",
			default = "F")

	left1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for strafing left",
			default = "A")

	left2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for strafing left",
			default = "NOT SET")

	left3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for strafing left",
			default = "NOT SET")

	right1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for strafing right",
			default = "D")

	right2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for strafing right",
			default = "NOT SET")

	right3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for strafing right",
			default = "NOT SET")

	forward1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving forward",
			default = "W")

	forward2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving forward",
			default = "NOT SET")

	forward3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving forward",
			default = "NOT SET")

	back1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving back",
			default = "S")

	back2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving back",
			default = "NOT SET")

	back3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving back",
			default = "NOT SET")

	up1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving up",
			default = "E")

	up2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving up",
			default = "SPACE")

	up3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving up",
			default = "NOT SET")

	down1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving down",
			default = "Q")

	down2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving down",
			default = "C")

	down3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving down",
			default = "X")

	Keyboard = bpy.props.EnumProperty(
			items = (("QWERTY", "QWERTY", "Set keyboard layout to QWERTY"), ("AZERTY", "AZERTY", "Set keyboard layout to AZERTY")),
			name = "Keyboard", 
			description = "Keyboard layout used",
			default = "QWERTY")

	Speed = bpy.props.FloatProperty(
			name = "Speed", 
			description = "Sets the navigation speed",
			min = 0,
			max = 1000,
			default = 50)
	
	MSens = bpy.props.IntProperty(
			name = "Mouse Sensitivity", 
			description = "Sets the mouse sensitivity",
			min = 1,
			max = 20,
			default = 10)
			
	YMirror = bpy.props.BoolProperty(
			name = "Mirror Y", 
			description = "Mirror Y direction",
			default = False)
			
	ActPass = bpy.props.BoolProperty(
			name = "Active/passive mouselook mode", 
			description = "Switch between active and passive mouselook mode",
			default = True)
			
	Height = bpy.props.FloatProperty(
			name = "Height above ground objects", 
			description = "Sets the  default walker distance above the ground",
			min = 0,
			max = 1000,
			default = 1.7)
			
	TDistance = bpy.props.FloatProperty(
			name = "Teleport distance", 
			description = "Sets how close viewer teleports to the targeted object",
			min = 0,
			max = 1000,
			default = 2)
			
	Scale = bpy.props.FloatProperty(
			name = "Scene scale", 
			description = "Allows to multiply Speed, Distance and Teleport Distance according to scene scale",
			min = 0.000001,
			max = 1000,
			default = 1)
			
	UseLens = bpy.props.BoolProperty(
			name = "Use set focal length", 
			description = "Focal length will be set when entering nav mode",
			default = False)
			
	Lens = bpy.props.FloatProperty(
			name = "Focal Length", 
			description = "Set nav mode focal length",
			min = 1,
			max = 250,
			default = 23.6)
			
	def draw(self, context):

		self.layout.prop(self, "ActPass")
		self.layout.prop(self, "Height")
		row = self.layout.row()
		row.prop(self, "UseLens")
		if self.UseLens:
			row.prop(self, "Lens")
		self.layout.prop(self, "TDistance")
		self.layout.prop(self, "Scale")
		self.layout.prop(self, "Speed")
		self.layout.prop(self, "MSens")
		self.layout.prop(self, "YMirror")
		self.layout.label(text="Key Bindings:")
		self.layout.prop(self, "Keyboard")
		row = self.layout.row()
		row.prop(self, "mouselook")
		row.operator("fpsfly.setkey", text="Set").key="mouselook" 		
		row = self.layout.row()
		row.prop(self, "teleport")
		row.operator("fpsfly.setkey", text="Set").key="teleport" 		
		row = self.layout.row()
		row.prop(self, "walkmode")
		row.operator("fpsfly.setkey", text="Set").key="walkmode" 		
		split = self.layout.split(0.1)
		split.label(text="left Key")
		row = split.row()
		row.prop(self, "left1")
		row.operator("fpsfly.setkey", text="Set").key="left1" 
		row.prop(self, "left2")
		row.operator("fpsfly.setkey", text="Set").key="left2" 
		row.prop(self, "left3")
		row.operator("fpsfly.setkey", text="Set").key="left3" 
		split = self.layout.split(0.1)
		split.label(text="right Key")
		row = split.row()
		row.prop(self, "right1")
		row.operator("fpsfly.setkey", text="Set").key="right1" 
		row.prop(self, "right2")
		row.operator("fpsfly.setkey", text="Set").key="right2" 
		row.prop(self, "right3")
		row.operator("fpsfly.setkey", text="Set").key="right3" 
		split = self.layout.split(0.1)
		split.label(text="forward Key")
		row = split.row()
		row.prop(self, "forward1")
		row.operator("fpsfly.setkey", text="Set").key="forward1" 
		row.prop(self, "forward2")
		row.operator("fpsfly.setkey", text="Set").key="forward2" 
		row.prop(self, "forward3")
		row.operator("fpsfly.setkey", text="Set").key="forward3" 
		split = self.layout.split(0.1)
		split.label(text="back Key")
		row = split.row()
		row.prop(self, "back1")
		row.operator("fpsfly.setkey", text="Set").key="back1" 
		row.prop(self, "back2")
		row.operator("fpsfly.setkey", text="Set").key="back2" 
		row.prop(self, "back3")
		row.operator("fpsfly.setkey", text="Set").key="back3" 
		split = self.layout.split(0.1)
		split.label(text="up Key")
		row = split.row()
		row.prop(self, "up1")
		row.operator("fpsfly.setkey", text="Set").key="up1" 
		row.prop(self, "up2")
		row.operator("fpsfly.setkey", text="Set").key="up2" 
		row.prop(self, "up3")
		row.operator("fpsfly.setkey", text="Set").key="up3" 
		split = self.layout.split(0.1)
		split.label(text="down Key")
		row = split.row()
		row.prop(self, "down1")
		row.operator("fpsfly.setkey", text="Set").key="down1" 
		row.prop(self, "down2")
		row.operator("fpsfly.setkey", text="Set").key="down2" 
		row.prop(self, "down3")
		row.operator("fpsfly.setkey", text="Set").key="down3" 



class FPSFlyStart(bpy.types.Operator):
	bl_idname = "view3d.fpsfly"
	bl_label = "Start FPSFly"
	bl_description = "FPS viewport navigation"
	bl_options = {"REGISTER"}
	
	def invoke(self, context, event):
	
		self.scn = context.scene
	
		self.addonprefs = bpy.context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
		context.window_manager.modal_handler_add(self)
		
		bpy.types.Scene.PreSelOff = bpy.props.BoolProperty(
				name = "PreSelOff", 
				description = "Switch off PreSel during FPS navigation mode",
				default = True)
		
		self.area = context.area
		self.area.header_text_set(text="FPS navigation mode active (ESC to exit)")

		self.addonprefs.oldkeyboard = self.addonprefs.Keyboard
		for self.region in context.area.regions:
			if self.region.type == "UI":
				self.regionui = self.region
		self.region = context.region
		self.rv3d = context.space_data.region_3d
		self.window = context.window
		
		if not(self.rv3d.is_perspective):
			self.rv3d.view_perspective = 'PERSP'
		if self.addonprefs.UseLens:
			self.oldlens = context.space_data.lens
			context.space_data.lens = self.addonprefs.Lens
		
		self.hchange = False
		if self.scn.FPS_Walk:
			self.ground = None
			self.movetoground()
			
		self.runmulti = 1	
		self.divi = 200
		self.acton = False
		self.leftnav = False
		self.rightnav = False
		self.forwardnav = False
		self.backnav = False
		self.upnav = False
		self.downnav = False
		
		self._handle = bpy.types.SpaceView3D.draw_handler_add(self.redraw, (), "WINDOW", "POST_PIXEL")

		self.cursor_hide(context)
		self.xcenter = int(self.region.x + self.region.width/2)
		self.ycenter = int(self.region.y + self.region.height/2)
		self.cursor_reset(context)
		context.scene.PreSelOff = True
		self.region.tag_redraw()
				
		self.movetimer = context.window_manager.event_timer_add(0.025, context.window)

		return {'RUNNING_MODAL'}


	def modal(self, context, event):
	
		mx = event.mouse_x
		my = event.mouse_y
		
		off = False
		if event.type == 'F':
			if event.shift and event.ctrl and not(event.alt) and event.value == 'PRESS':
				off = True
		if off or event.type == 'ESC' or not(self.rv3d.is_perspective):
			context.window_manager.event_timer_remove(self.movetimer)
			
			self.cursor_restore(context)
			self.regionui.tag_redraw()
			self.region.tag_redraw()

			del bpy.types.Scene.PreSelOff
			self.area.header_text_set()
			
			if self.addonprefs.UseLens:
				context.space_data.lens = self.oldlens

			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'FINISHED'}

		if event.type in {'LEFT_SHIFT', 'RIGHTSHIFT'}:
			if event.value == 'PRESS':
				self.runmulti = 1.5
			else:
				self.runmulti = 1

		if event.type == 'WHEELUPMOUSE':
			self.addonprefs.Speed *= 1.4
		if event.type == 'WHEELDOWNMOUSE':
			self.addonprefs.Speed *= 0.8
			
		if event.type == self.addonprefs.mouselook:
			if event.value == 'PRESS' and self.addonprefs.ActPass:
				self.acton = True
			else:
				self.acton = False
		if self.addonprefs.ActPass == False:
			self.acton = True
				
		if event.type in {'MOUSEMOVE', 'LEFTMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
			if event.type == 'MOUSEMOVE':
				if mx == self.xcenter and my == self.ycenter:
					return {'RUNNING_MODAL'}
				self.cursor_reset(context)
			if self.acton and event.type == 'MOUSEMOVE' and self.rv3d:
				if self.addonprefs.YMirror:
					ymult = -1
				else:
					ymult = 1
				smult = (self.addonprefs.MSens / 10) + 0.1
				dx = mx - self.xcenter
				dy = my - self.ycenter
				cmat = self.rv3d.view_matrix.inverted()
				dxmat = Matrix.Rotation(math.radians(-dx*smult / 5), 3, 'Z')
				cmat3 = cmat.copy().to_3x3()
				cmat3.rotate(dxmat)
				cmat4 = cmat3.to_4x4()
				cmat4.translation = cmat.translation
				self.rv3d.view_matrix = cmat4.inverted()
				self.rv3d.update()
				cmat = self.rv3d.view_matrix.inverted()
				dymat = Matrix.Rotation(math.radians(dy*ymult*smult / 5), 3, self.rv3d.view_matrix[0][:3])
				cmat3 = cmat.copy().to_3x3()
				cmat3.rotate(dymat)
				cmat4 = cmat3.to_4x4()
				cmat4.translation = cmat.translation
				tempmat = cmat4.inverted()
				upvec = Vector(tempmat[1][:3])
				downvec = -Vector(tempmat[1][:3])
				if upvec.angle(Vector((0, 0, 1))) < math.radians(90):
					if downvec.angle(Vector((0, 0, -1))) < math.radians(90):
						self.rv3d.view_matrix = tempmat
						self.rv3d.update()
			if mx > self.regionui.x or my < self.regionui.y:
				return {'PASS_THROUGH'}
			else:
				return {'RUNNING_MODAL'}
			
		if event.type in {self.addonprefs.left1, self.addonprefs.left2, self.addonprefs.left3}:
			if event.value == 'PRESS':
				self.leftnav = True
			else:
				self.leftnav = False
		elif event.type in {self.addonprefs.right1, self.addonprefs.right2, self.addonprefs.right3}:
			if event.value == 'PRESS':
				self.rightnav = True
			else:
				self.rightnav = False
		elif event.type in {self.addonprefs.forward1, self.addonprefs.forward2, self.addonprefs.forward3}:
			if event.value == 'PRESS':
				self.forwardnav = True
			else:
				self.forwardnav = False
		elif event.type in {self.addonprefs.back1, self.addonprefs.back2, self.addonprefs.back3}:
			if event.value == 'PRESS':
				self.backnav = True
			else:
				self.backnav = False
		elif event.type in {self.addonprefs.up1, self.addonprefs.up2, self.addonprefs.up3}:
			if event.value == 'PRESS':
				self.upnav = True
			else:
				self.upnav = False
		elif event.type in {self.addonprefs.down1, self.addonprefs.down2, self.addonprefs.down3}:
			if event.value == 'PRESS':
				self.downnav = True
			else:
				self.downnav = False
					

		if event.type == 'TIMER':
			moved = False
			if self.leftnav:
				moved = True
				self.moveleft()
			if self.rightnav:
				moved = True
				self.moveright()
			if self.forwardnav:
				moved = True
				self.moveforward()
			if self.backnav:
				moved = True
				self.moveback()
			if self.upnav:
				moved = True
				self.moveup()
			if self.downnav:
				moved = True
				self.movedown()
				
			if moved:
				self.rv3d.update()
				if self.scn.FPS_Walk:
					self.movetoground()
					
					
		if event.type == self.addonprefs.walkmode:
			if event.value == 'PRESS':
				self.scn.FPS_Walk = not(self.scn.FPS_Walk)
				if self.scn.FPS_Walk:
					self.hchange = True
				self.regionui.tag_redraw()
				
		if event.type == self.addonprefs.teleport:
			if event.value == 'PRESS':
				eyevec = -Vector(self.rv3d.view_matrix[2][:3])
				eye = Vector(self.rv3d.view_matrix.inverted().col[3][:3])
				start = eye
				eyevec.length = 10000
				end = start + eyevec
				hit = self.scn.ray_cast(start, end)
				if hit[0]:
					delta = hit[3] - eye
					length = delta.length - self.addonprefs.TDistance * self.addonprefs.Scale
					if length > 0:
						delta.length = length
					else:
						return {'RUNNING_MODAL'}
					self.rv3d.view_location += delta
					self.rv3d.update()
				if self.scn.FPS_Walk:
					self.movetoground()

					
					
		return {'RUNNING_MODAL'}

	

	# utility functions
	def cursor_reset(self, context):
		context.window.cursor_warp(self.xcenter, self.ycenter)

	def cursor_hide(self, context):
		context.window.cursor_modal_set('NONE')

	def cursor_restore(self, context):
		context.window.cursor_modal_restore()



	def moveleft(self):
		bfvec = Vector(self.rv3d.view_matrix[0][:3])
		bfvec.length = self.addonprefs.Speed * self.addonprefs.Scale * self.runmulti / self.divi
		self.rv3d.view_location -= bfvec
	def moveright(self):
		bfvec = Vector(self.rv3d.view_matrix[0][:3])
		bfvec.length = self.addonprefs.Speed * self.addonprefs.Scale * self.runmulti / self.divi
		self.rv3d.view_location += bfvec
	def moveforward(self):
		bfvec = Vector(self.rv3d.view_matrix[2][:3])
		bfvec.length = self.addonprefs.Speed * self.addonprefs.Scale * self.runmulti / self.divi
		self.rv3d.view_location -= bfvec
	def moveback(self):
		bfvec = Vector(self.rv3d.view_matrix[2][:3])
		bfvec.length = self.addonprefs.Speed * self.addonprefs.Scale * self.runmulti / self.divi
		self.rv3d.view_location += bfvec
	def moveup(self):
		bfvec = Vector((0, 0, 1))
		bfvec.length = self.addonprefs.Speed * self.addonprefs.Scale * self.runmulti / self.divi
		if self.scn.FPS_Walk:
			self.addonprefs.Height += bfvec.length * self.addonprefs.Scale
		else:
			self.rv3d.view_location += bfvec
	def movedown(self):
		bfvec = Vector((0, 0, 1))
		bfvec.length = self.addonprefs.Speed * self.addonprefs.Scale * self.runmulti / self.divi
		if self.scn.FPS_Walk:
			self.addonprefs.Height -= bfvec.length * self.addonprefs.Scale
			if self.addonprefs.Height <= 0:
				self.addonprefs.Height = 0.0001
		else:
			self.rv3d.view_location -= bfvec
			
	def movetoground(self):
	
		cammat = self.rv3d.view_matrix.inverted()
		eye = Vector(cammat.col[3][:3])
		start = eye
		end = eye + Vector((0, 0, -10000))
		if self.scn.FPS_GroundMode == "All":
			hit = self.scn.ray_cast(start, end)
			if not (hit[0]):
				return
			if self.hchange:
				self.hchange = False 
				self.addonprefs.Height = (eye - hit[3]).length
				return
			cammat.col[3][2] = hit[3][2] + (self.addonprefs.Height * self.addonprefs.Scale)
			self.rv3d.view_matrix = cammat.inverted()
			self.rv3d.update()
		else:
			while True:
				hit = self.scn.ray_cast(start, end)
				if hit[0]:
					if self.ground == None:
						self.ground = hit[1]
					if hit[1] == self.ground:
						if self.hchange:
							self.hchange = False
							self.addonprefs.Height = (eye - hit[3]).length
							return
						cammat.col[3][2] = hit[3][2] + (self.addonprefs.Height * self.addonprefs.Scale)
						self.rv3d.view_matrix = cammat.inverted()
						self.rv3d.update()
						return
					start = hit[3] + Vector((0, 0, -0.00001))
				else:
					self.scn.FPS_Walk = False
					self.regionui.tag_redraw()
					return
			


	def redraw(self):
	
		if self.region:
		
			x = self.region.width / 2
			y = self.region.height / 2
			glBegin(GL_LINES)
			glColor3f(0.7, 0, 0)
			glVertex2f(x - 8, y)
			glVertex2f(x + 8, y)
			glVertex2f(x, y - 8)
			glVertex2f(x, y + 8)
			glEnd()
			
			
def addtomenu(self, context):  
	self.layout.operator("view3d.fpsfly", text = "Enter FPS navigation mode") 		

def register():

	bpy.types.Scene.FPS_Walk = bpy.props.BoolProperty(
			name = "Walkmode", 
			description = "Toggle the use of walkmode",
			default = False)

	bpy.types.Scene.FPS_GroundMode = bpy.props.EnumProperty(
			items = [("All", "All", "Use all objects for walking on"), ("Drop", "Drop", "FPS_Walk on object you drop down on")],
			name = "Ground", 
			description = "Set object used as ground to walk on",
			default = "All")

	bpy.utils.register_module(__name__)
	
	bpy.types.VIEW3D_MT_view_navigation.append(addtomenu)

	addonprefs = bpy.context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
	addonprefs.oldkeyboard = addonprefs.Keyboard
		
	bpy.app.handlers.scene_update_post.append(sceneupdate_handler)	

	wm = bpy.context.window_manager
	view3d_km_items = wm.keyconfigs.default.keymaps['3D View'].keymap_items
	view3d_km_items.new("view3d.fpsfly", 'F', 'PRESS', ctrl=True, shift=True)


def unregister():

	bpy.app.handlers.scene_update_post.remove(sceneupdate_handler)	
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
	




@persistent
def sceneupdate_handler(dummy):

	addonprefs = bpy.context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
		
	if not(addonprefs.Keyboard == addonprefs.oldkeyboard):
		if addonprefs.Keyboard == "QWERTY":
			addonprefs.left1 = "A"
			addonprefs.left2 = "NOT SET"
			addonprefs.left3 = "NOT SET"
			addonprefs.right1 = "D"
			addonprefs.right2 = "NOT SET"
			addonprefs.right3 = "NOT SET"
			addonprefs.forward1 = "W"
			addonprefs.forward2 = "NOT SET"
			addonprefs.forward3 = "NOT SET"
			addonprefs.back1 = "S"
			addonprefs.back2 = "NOT SET"
			addonprefs.back3 = "NOT SET"
			addonprefs.up1 = "E"
			addonprefs.up2 = "SPACE"
			addonprefs.up3 = "NOT SET"
			addonprefs.down1 = "Q"
			addonprefs.down2 = "C"
			addonprefs.down3 = "X"
		elif addonprefs.Keyboard == "AZERTY":
			addonprefs.left1 = "Q"
			addonprefs.left2 = "NOT SET"
			addonprefs.left3 = "NOT SET"
			addonprefs.right1 = "D"
			addonprefs.right2 = "NOT SET"
			addonprefs.right3 = "NOT SET"
			addonprefs.forward1 = "Z"
			addonprefs.forward2 = "NOT SET"
			addonprefs.forward3 = "NOT SET"
			addonprefs.back1 = "S"
			addonprefs.back2 = "NOT SET"
			addonprefs.back3 = "NOT SET"
			addonprefs.up1 = "E"
			addonprefs.up2 = "SPACE"
			addonprefs.up3 = "NOT SET"
			addonprefs.down1 = "A"
			addonprefs.down2 = "C"
			addonprefs.down3 = "X"
		addonprefs.oldkeyboard = addonprefs.Keyboard
