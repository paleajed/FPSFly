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

Only works in perspective mode!

Go to FPSFly Addon Preferences (UserPreferences->Addons->3D View->FPSFly and click arrow next to it) to change options :
Active/Passive mode :  always mouselook (passive=off) or when RIGHTMOUSE pressed (active=on).
Navigation speed :  set flying speed.
Keyboard layout :  choose QWERTY or AZERTY.
Mouse sensitivity.
Mirror Y : opposite Y direction.

"""


bl_info = {
	"name": "FPSFly",
	"author": "Gert De Roost",
	"version": (0, 6, 5),
	"blender": (2, 6, 8),
	"location": "View3D > UI > FPSFly",
	"description": "FPS viewport navigation",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "3D View"}


import bpy
from bgl import *
import blf
from mathutils import Vector, Matrix, Color
import math






class SetKey(bpy.types.Operator):
	bl_idname = "fpsfly.setkey"
	bl_label = "Set Key Binding"
	
	key = bpy.props.StringProperty()

	def invoke(self, context, event):
	
		context.window_manager.modal_handler_add(self)
		
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
	
		isset = False
		if not(event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER', 'NONE'}):
			if event.value == 'PRESS':
				setattr(addonprefs, self.key, event.type)
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
		
		self.layout.operator("view3d.fpsfly", "Enter FPS navigation")


class FPSFlyAddonPreferences(bpy.types.AddonPreferences):

	bl_idname = "space_view3d_fpsfly"
	
	oldkeyboard = None
	
	mouselook = bpy.props.StringProperty(
			name = "mouselook Button/Key", 
			description = "Key binding for mouselook",
			default = "RIGHTMOUSE")

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

	Speed = bpy.props.IntProperty(
			name = "Speed", 
			description = "Sets the navigation speed",
			min = 1,
			max = 1000,
			default = 20)
	
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
			
	def draw(self, context):

		self.layout.prop(self, "ActPass")
		self.layout.prop(self, "Speed")
		self.layout.prop(self, "Keyboard")
		self.layout.prop(self, "MSens")
		self.layout.prop(self, "YMirror")
		self.layout.label(text="Key Bindings:")
		row = self.layout.row()
		row.prop(self, "mouselook")
		row.operator("fpsfly.setkey", text="Set").key="mouselook" 		
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
	
		global mainop
		
		mainop = self
	
		context.window_manager.modal_handler_add(self)
		
		bpy.types.Scene.PreSelOff = bpy.props.BoolProperty(
				name = "PreSelOff", 
				description = "Switch off PreSel during FPS navigation mode",
				default = True)

		addonprefs.oldkeyboard = addonprefs.Keyboard
		bpy.app.handlers.scene_update_post.append(sceneupdate_handler)
		
		self.acton = False
		self.leftnav = False
		self.rightnav = False
		self.forwardnav = False
		self.backnav = False
		self.upnav = False
		self.downnav = False
		
		self._handle = bpy.types.SpaceView3D.draw_handler_add(redraw, (), "WINDOW", "POST_PIXEL")

		for self.region in context.area.regions:
			if self.region.type == "UI":
				self.regionui = self.region
		self.region = context.region
		self.rv3d = context.space_data.region_3d
		self.window = context.window
		self.cursor_hide(context)
		self.xcenter = int(self.region.x + self.region.width/2)
		self.ycenter = int(self.region.y + self.region.height/2)
		self.cursor_reset(context)
		context.scene.PreSelOff = True
		self.region.tag_redraw()
				
		return {'RUNNING_MODAL'}


	def modal(self, context, event):
	
		mx = event.mouse_x
		my = event.mouse_y
		
		off = False
		if event.type == 'F':
			if event.shift and event.ctrl and not(event.alt) and event.value == 'PRESS':
				off = True
		if off or event.type == 'ESC' or not(self.rv3d.is_perspective):
			self.cursor_restore(context)
			self.regionui.tag_redraw()
			self.region.tag_redraw()

			del bpy.types.Scene.PreSelOff

			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'FINISHED'}
			
		if event.type == 'WHEELUPMOUSE':
			addonprefs.Speed *= 1.5
		if event.type == 'WHEELDOWNMOUSE':
			addonprefs.Speed *= 0.8
			if addonprefs.Speed == 0:
				addonprefs.Speed = 2
			
		if event.type == addonprefs.mouselook:
			if event.value == 'PRESS' and addonprefs.ActPass:
				self.acton = True
			else:
				self.acton = False
		if addonprefs.ActPass == False:
			self.acton = True
				
		if event.type in {'MOUSEMOVE', 'LEFTMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
			if event.type == 'MOUSEMOVE':
				if mx == self.xcenter and my == self.ycenter:
					return {'RUNNING_MODAL'}
				self.cursor_reset(context)
			if self.acton and event.type == 'MOUSEMOVE' and self.rv3d:
				if addonprefs.YMirror:
					ymult = -1
				else:
					ymult = 1
				smult = (addonprefs.MSens / 10) + 0.1
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
				self.rv3d.view_matrix = cmat4.inverted()
				self.rv3d.update()
			if mx > self.regionui.x or my < self.regionui.y:
				return {'PASS_THROUGH'}
			else:
				return {'RUNNING_MODAL'}
			
		if event.type in {addonprefs.left1, addonprefs.left2, addonprefs.left3}:
			if event.value == 'PRESS':
				self.leftnav = True
				print ("left")
			else:
				self.leftnav = False
		elif event.type in {addonprefs.right1, addonprefs.right2, addonprefs.right3}:
			if event.value == 'PRESS':
				self.rightnav = True
			else:
				self.rightnav = False
		elif event.type in {addonprefs.forward1, addonprefs.forward2, addonprefs.forward3}:
			if event.value == 'PRESS':
				self.forwardnav = True
			else:
				self.forwardnav = False
		elif event.type in {addonprefs.back1, addonprefs.back2, addonprefs.back3}:
			if event.value == 'PRESS':
				self.backnav = True
			else:
				self.backnav = False
		elif event.type in {addonprefs.up1, addonprefs.up2, addonprefs.up3}:
			if event.value == 'PRESS':
				self.upnav = True
			else:
				self.upnav = False
		elif event.type in {addonprefs.down1, addonprefs.down2, addonprefs.down3}:
			if event.value == 'PRESS':
				self.downnav = True
			else:
				self.downnav = False
					

		return {'RUNNING_MODAL'}

	
	# utility functions
	def cursor_reset(self, context):
		context.window.cursor_warp(self.xcenter, self.ycenter)

	def cursor_hide(self, context):
		context.window.cursor_modal_set('NONE')

	def cursor_restore(self, context):
		context.window.cursor_modal_restore()


def register():

	global addonprefs

	bpy.utils.register_module(__name__)
	
	

	addonprefs = bpy.context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
	wm = bpy.context.window_manager
	view3d_km_items = wm.keyconfigs.default.keymaps['3D View'].keymap_items
	view3d_km_items.new("view3d.fpsfly", 'F', 'PRESS', ctrl=True, shift=True)


def unregister():

	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
	
	
	

def redraw():

	if mainop.region:
	
		x = mainop.region.width / 2
		y = mainop.region.height / 2
		glBegin(GL_LINES)
		glColor3f(0.7, 0, 0)
		glVertex2f(x - 8, y)
		glVertex2f(x + 8, y)
		glVertex2f(x, y - 8)
		glVertex2f(x, y + 8)
		glEnd()
		
		glColor3f(1, 1, 0.7)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, mainop.region.width, 0, mainop.region.height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		blf.position(0, mainop.region.width/2 - 80, mainop.region.height - 20, 0)
		blf.size(0, 15, 72)
		blf.draw(0, "FPS navigation (ESC exits)")


		divi = 200
		def moveleft():
			bfvec = Vector(mainop.rv3d.view_matrix[0][:3])
			bfvec.length = addonprefs.Speed / divi
			mainop.rv3d.view_location -= bfvec
		def moveright():
			bfvec = Vector(mainop.rv3d.view_matrix[0][:3])
			bfvec.length = addonprefs.Speed / divi
			mainop.rv3d.view_location += bfvec
		def moveforward():
			bfvec = Vector(mainop.rv3d.view_matrix[2][:3])
			bfvec.length = addonprefs.Speed / divi
			mainop.rv3d.view_location -= bfvec
		def moveback():
			bfvec = Vector(mainop.rv3d.view_matrix[2][:3])
			bfvec.length = addonprefs.Speed / divi
			mainop.rv3d.view_location += bfvec
		def moveup():
			bfvec = Vector((0, 0, 1))
			bfvec.length = addonprefs.Speed / divi
			mainop.rv3d.view_location += bfvec
		def movedown():
			bfvec = Vector((0, 0, 1))
			bfvec.length = addonprefs.Speed / divi
			mainop.rv3d.view_location -= bfvec
		
		if mainop.leftnav:
			moveleft()
		if mainop.rightnav:
			moveright()
		if mainop.forwardnav:
			moveforward()
		if mainop.backnav:
			moveback()
		if mainop.upnav:
			moveup()
		if mainop.downnav:
			movedown()
		mainop.rv3d.update()
		
		mainop.rv3d.view_matrix = mainop.rv3d.view_matrix



		
def sceneupdate_handler(dummy):

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
