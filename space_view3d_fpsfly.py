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
Also added EQ/EA for moving up/down.  Update: now also X and V for down and SPACEBAR for up.
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
	"version": (0, 4, 0),
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
from mathutils import *
import math
from bpy.app.handlers import persistent
import sys


black = Color((0, 0, 0))

ready = 0
started = 0
navon = 0
leftnav = 0
rightnav = 0
forwardnav = 0
backnav = 0
upnav = 0
downnav = 0
leave = 0
acton = 0
region = None
rv3d = None
lkey = {}
rkey = {}
fkey = {}
bkey = {}
ukey = {}
dkey = {}
lkey["QWERTY"] = "A"
lkey["AZERTY"] = "Q"
rkey["QWERTY"] = "D"
rkey["AZERTY"] = "D"
fkey["QWERTY"] = "W"
fkey["AZERTY"] = "Z"
bkey["QWERTY"] = "S"
bkey["AZERTY"] = "S"
ukey["QWERTY"] = ["E", "SPACE"]
ukey["AZERTY"] = ["E", "SPACE"]
dkey["QWERTY"] = ["Q", "C", "X"]
dkey["AZERTY"] = ["A", "C", "X"]



bpy.types.Scene.Toggle = bpy.props.BoolProperty(
		name = "FPS flymode", 
		description = "Turn on/off FPS navigation mode",
		default = False)

bpy.types.Scene.PreSelOff = bpy.props.BoolProperty(
		name = "PreSelOff", 
		description = "Switch off PreSel during FPS navigation mode",
		default = False)


class SetKey(bpy.types.Operator):
	bl_idname = "fpsfly.setkey"
	bl_label = "Set Key Binding"
	
	key = bpy.props.StringProperty()

	def invoke(self, context, event):
	
		context.window_manager.modal_handler_add(self)
		
		return {"RUNNING_MODAL"}

	def modal(self, context, event):
	
		isset = 0
		if not(event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE", "TIMER", "NONE"]):
			if event.value == "PRESS":
				if self.key == "mouselook":
					addonprefs.Mouselook = event.type
				if self.key == "left1":
					addonprefs.Left1 = event.type
				if self.key == "left2":
					addonprefs.Left2 = event.type
				if self.key == "left3":
					addonprefs.Left3 = event.type
				if self.key == "right1":
					addonprefs.Right1 = event.type
				if self.key == "right2":
					addonprefs.Right2 = event.type
				if self.key == "right3":
					addonprefs.Right3 = event.type
				if self.key == "forward1":
					addonprefs.Forward1 = event.type
				if self.key == "forward2":
					addonprefs.Forward2 = event.type
				if self.key == "forward3":
					addonprefs.Forward3 = event.type
				if self.key == "back1":
					addonprefs.Back1 = event.type
				if self.key == "back2":
					addonprefs.Back2 = event.type
				if self.key == "back3":
					addonprefs.Back3 = event.type
				if self.key == "up1":
					addonprefs.Up1 = event.type
				if self.key == "up2":
					addonprefs.Up2 = event.type
				if self.key == "up3":
					addonprefs.Up3 = event.type
				if self.key == "down1":
					addonprefs.Down1 = event.type
				if self.key == "down2":
					addonprefs.Down2 = event.type
				if self.key == "down3":
					addonprefs.Down3 = event.type
				isset = 1
		
		if isset:
			bpy.context.region.tag_redraw()
			return {"FINISHED"}
		else:
			return {"RUNNING_MODAL"}


class FPSFlyPanel(bpy.types.Panel):
	bl_label = "FPSFly"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	def draw(self, context):
		
		scn = bpy.context.scene
		
		self.layout.prop(scn, "Toggle")


class FPSFlyAddonPreferences(bpy.types.AddonPreferences):

	bl_idname = "space_view3d_fpsfly"
	
	
	Mouselook = bpy.props.StringProperty(
			name = "Mouselook Button/Key", 
			description = "Key binding for mouselook",
			default = "RIGHTMOUSE")

	Left1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for strafing left",
			default = "A")

	Left2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for strafing left",
			default = "NOT SET")

	Left3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for strafing left",
			default = "NOT SET")

	Right1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for strafing right",
			default = "D")

	Right2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for strafing right",
			default = "NOT SET")

	Right3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for strafing right",
			default = "NOT SET")

	Forward1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving forward",
			default = "W")

	Forward2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving forward",
			default = "NOT SET")

	Forward3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving forward",
			default = "NOT SET")

	Back1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving back",
			default = "S")

	Back2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving back",
			default = "NOT SET")

	Back3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving back",
			default = "NOT SET")

	Up1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving up",
			default = "E")

	Up2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving up",
			default = "SPACE")

	Up3 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 3 for moving up",
			default = "NOT SET")

	Down1 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 1 for moving down",
			default = "Q")

	Down2 = bpy.props.StringProperty(
			name = "", 
			description = "Key binding 2 for moving down",
			default = "C")

	Down3 = bpy.props.StringProperty(
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
		row.prop(self, "Mouselook")
		row.operator("fpsfly.setkey", text="Set").key="mouselook" 		
		split = self.layout.split(0.1)
		split.label(text="Left Key")
		row = split.row()
		row.prop(self, "Left1")
		row.operator("fpsfly.setkey", text="Set").key="left1" 
		row.prop(self, "Left2")
		row.operator("fpsfly.setkey", text="Set").key="left2" 
		row.prop(self, "Left3")
		row.operator("fpsfly.setkey", text="Set").key="left3" 
		split = self.layout.split(0.1)
		split.label(text="Right Key")
		row = split.row()
		row.prop(self, "Right1")
		row.operator("fpsfly.setkey", text="Set").key="right1" 
		row.prop(self, "Right2")
		row.operator("fpsfly.setkey", text="Set").key="right2" 
		row.prop(self, "Right3")
		row.operator("fpsfly.setkey", text="Set").key="right3" 
		split = self.layout.split(0.1)
		split.label(text="Forward Key")
		row = split.row()
		row.prop(self, "Forward1")
		row.operator("fpsfly.setkey", text="Set").key="forward1" 
		row.prop(self, "Forward2")
		row.operator("fpsfly.setkey", text="Set").key="forward2" 
		row.prop(self, "Forward3")
		row.operator("fpsfly.setkey", text="Set").key="forward3" 
		split = self.layout.split(0.1)
		split.label(text="Back Key")
		row = split.row()
		row.prop(self, "Back1")
		row.operator("fpsfly.setkey", text="Set").key="back1" 
		row.prop(self, "Back2")
		row.operator("fpsfly.setkey", text="Set").key="back2" 
		row.prop(self, "Back3")
		row.operator("fpsfly.setkey", text="Set").key="back3" 
		split = self.layout.split(0.1)
		split.label(text="Up Key")
		row = split.row()
		row.prop(self, "Up1")
		row.operator("fpsfly.setkey", text="Set").key="up1" 
		row.prop(self, "Up2")
		row.operator("fpsfly.setkey", text="Set").key="up2" 
		row.prop(self, "Up3")
		row.operator("fpsfly.setkey", text="Set").key="up3" 
		split = self.layout.split(0.1)
		split.label(text="Down Key")
		row = split.row()
		row.prop(self, "Down1")
		row.operator("fpsfly.setkey", text="Set").key="down1" 
		row.prop(self, "Down2")
		row.operator("fpsfly.setkey", text="Set").key="down2" 
		row.prop(self, "Down3")
		row.operator("fpsfly.setkey", text="Set").key="down3" 



class FPSFlyStart(bpy.types.Operator):
	bl_idname = "view3d.fpsfly"
	bl_label = "Start FPSFly"
	bl_description = "FPS viewport navigation"
	bl_options = {"REGISTER"}

	def invoke(self, context, event):
	
		global addonprefs, oldkeyboard
	
		scn = bpy.context.scene

		addonprefs = bpy.context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
		context.window_manager.modal_handler_add(self)
		
		oldkeyboard = addonprefs.Keyboard
		bpy.app.handlers.scene_update_post.append(sceneupdate_handler)

		# initial state
		self.mouse_x_orig = event.mouse_x
		self.mouse_y_orig = event.mouse_y

		return {"RUNNING_MODAL"}

	def modal(self, context, event):
	
		global navon, leftnav, rightnav, forwardnav, backnav, upnav, downnav
		global movetimer, leave, acton
		global rv3d, region
		
		
		scn = bpy.context.scene
		
		for region in bpy.context.area.regions:
			if region.type == "UI":
				regionui = region

		if not(navon):
			if event.type in ["F"]:
				if event.shift and event.ctrl and not(event.alt) and event.value == "PRESS":
					navon = 1
					scn.Toggle = 1
					regionui.tag_redraw()
					rv3d = bpy.context.space_data.region_3d
					scn.PreSelOff = 1
					bpy.context.region.tag_redraw()
					self.cursor_hide(context)
					return {"RUNNING_MODAL"}
			if scn.Toggle and not(navon):
				navon = 1
				rv3d = bpy.context.space_data.region_3d
				scn.PreSelOff = 1
				bpy.context.region.tag_redraw()
				self.cursor_hide(context)
				return {"RUNNING_MODAL"}
			
		if not(navon):
			return {"PASS_THROUGH"}
		
		mx = event.mouse_x
		my = event.mouse_y
		for a in bpy.context.screen.areas:
			if not(a.type == "VIEW_3D"):
				continue
			for r in a.regions:
				if not(r.type == "WINDOW"):
					continue
				if mx > r.x and my > r.y and mx < r.x + r.width and my < r.y + r.height:
					for sp in a.spaces:
						if sp.type == "VIEW_3D":
							region = r
							rv3d = sp.region_3d
					break
		if not(rv3d.is_perspective):
			navon = 0
			scn.Toggle = 0
			return {"RUNNING_MODAL"}
		
		off = 0
		if event.type in ["F"]:
			if event.shift and event.ctrl and not(event.alt) and event.value == "PRESS":
				off = 1
		if off or event.type in ["ESC"] or not(scn.Toggle):
			self.cursor_reset(context)
			self.cursor_restore(context)

			navon = 0
			scn.Toggle = 0
			regionui.tag_redraw()
			region.tag_redraw()
			scn.PreSelOff = 0
			leftnav = 0
			rightnav = 0
			forwardnav = 0
			backnav = 0
			upnav = 0
			downnav = 0
			acton = 0
			return {"RUNNING_MODAL"}
			
		if event.type in ["WHEELUPMOUSE"]:
			addonprefs.Speed *= 1.5
		if event.type in ["WHEELDOWNMOUSE"]:
			addonprefs.Speed *= 0.8
			if addonprefs.Speed == 0:
				addonprefs.Speed = 2
			
		if event.type in [addonprefs.Mouselook]:
			if event.value == "PRESS" and addonprefs.ActPass:
				acton = 1
			else:
				acton = 0
		if addonprefs.ActPass == 0:
			acton = 1
				
		if event.type in ["MOUSEMOVE", "LEFTMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"]:
			if event.type in ["MOUSEMOVE"]:
				context.window.cursor_warp(self.mouse_x_orig, self.mouse_y_orig)
			if acton and event.type in ["MOUSEMOVE"] and rv3d:
				if addonprefs.YMirror:
					ymult = -1
				else:
					ymult = 1
				smult = (addonprefs.MSens / 10) + 0.1
				dx = mx - self.mouse_x_orig
				dy = my - self.mouse_y_orig
				cmat = rv3d.view_matrix.inverted()
				dxmat = Matrix.Rotation(math.radians(-dx*smult / 5), 3, "Z")
				cmat3 = cmat.copy().to_3x3()
				cmat3.rotate(dxmat)
				cmat4 = cmat3.to_4x4()
				cmat4.translation = cmat.translation
				rv3d.view_matrix = cmat4.inverted()
				rv3d.update()
				cmat = rv3d.view_matrix.inverted()
				dymat = Matrix.Rotation(math.radians(dy*ymult*smult / 5), 3, rv3d.view_matrix[0][:3])
				cmat3 = cmat.copy().to_3x3()
				cmat3.rotate(dymat)
				cmat4 = cmat3.to_4x4()
				cmat4.translation = cmat.translation
				rv3d.view_matrix = cmat4.inverted()
				rv3d.update()
			if mx > regionui.x or my < regionui.y:
				return {"PASS_THROUGH"}
			else:
				return {"RUNNING_MODAL"}
			
		if event.type in [addonprefs.Left1, addonprefs.Left2, addonprefs.Left3]:
			if event.value == "PRESS":
				leftnav = 1
			else:
				leftnav = 0
		elif event.type in [addonprefs.Right1, addonprefs.Right2, addonprefs.Right3]:
			if event.value == "PRESS":
				rightnav = 1
			else:
				rightnav = 0
		elif event.type in [addonprefs.Forward1, addonprefs.Forward2, addonprefs.Forward3]:
			if event.value == "PRESS":
				forwardnav = 1
			else:
				forwardnav = 0
		elif event.type in [addonprefs.Back1, addonprefs.Back2, addonprefs.Back3]:
			if event.value == "PRESS":
				backnav = 1
			else:
				backnav = 0
		elif event.type in [addonprefs.Up1, addonprefs.Up2, addonprefs.Up3]:
			if event.value == "PRESS":
				upnav = 1
			else:
				upnav = 0
		elif event.type in [addonprefs.Down1, addonprefs.Down2, addonprefs.Down3]:
			if event.value == "PRESS":
				downnav = 1
			else:
				downnav = 0

		return {"RUNNING_MODAL"}

	# utility functions
	def cursor_reset(self, context):
		context.window.cursor_warp(self.mouse_x_orig, self.mouse_y_orig)

	def cursor_hide(self, context):
		context.window.cursor_modal_set('NONE')

	def cursor_restore(self, context):
		context.window.cursor_modal_restore()

def register():

	global _handle, ready

	bpy.utils.register_module(__name__)
	_handle = bpy.types.SpaceView3D.draw_handler_add(redraw, (), "WINDOW", "POST_PIXEL")
	bpy.app.handlers.load_post.append(loadpost_handler)
	ready = 1


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
	
	
	

@persistent
def redraw():

	global started
	
	if ready:
		if not(started):
			started = 1
			bpy.ops.view3d.fpsfly("INVOKE_DEFAULT")
			
	if region and navon:
	
		if sys.platform == "linux":
			x = region.width / 2
			y = region.height / 2
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
		gluOrtho2D(0, region.width, 0, region.height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		blf.position(0, region.width/2 - 80, region.height - 20, 0)
		blf.size(0, 15, 72)
		blf.draw(0, "FPS navigation (ESC exits)")


		divi = 200
		def moveleft():
			bfvec = Vector(rv3d.view_matrix[0][:3])
			bfvec.length = addonprefs.Speed / divi
			rv3d.view_location -= bfvec
		def moveright():
			bfvec = Vector(rv3d.view_matrix[0][:3])
			bfvec.length = addonprefs.Speed / divi
			rv3d.view_location += bfvec
		def moveforward():
			bfvec = Vector(rv3d.view_matrix[2][:3])
			bfvec.length = addonprefs.Speed / divi
			rv3d.view_location -= bfvec
		def moveback():
			bfvec = Vector(rv3d.view_matrix[2][:3])
			bfvec.length = addonprefs.Speed / divi
			rv3d.view_location += bfvec
		def moveup():
			bfvec = Vector(rv3d.view_matrix[1][:3])
			bfvec.length = addonprefs.Speed / divi
			rv3d.view_location += bfvec
		def movedown():
			bfvec = Vector(rv3d.view_matrix[1][:3])
			bfvec.length = addonprefs.Speed / divi
			rv3d.view_location -= bfvec
		
		if leftnav:
			moveleft()
		if rightnav:
			moveright()
		if forwardnav:
			moveforward()
		if backnav:
			moveback()
		if upnav:
			moveup()
		if downnav:
			movedown()
		rv3d.update()
		
		rv3d.view_matrix = rv3d.view_matrix



		
def sceneupdate_handler(dummy):

	global oldkeyboard

	if not(addonprefs.Keyboard == oldkeyboard):
		if addonprefs.Keyboard == "QWERTY":
			addonprefs.Left1 = "A"
			addonprefs.Left2 = "NOT SET"
			addonprefs.Left3 = "NOT SET"
			addonprefs.Right1 = "D"
			addonprefs.Right2 = "NOT SET"
			addonprefs.Right3 = "NOT SET"
			addonprefs.Forward1 = "W"
			addonprefs.Forward2 = "NOT SET"
			addonprefs.Forward3 = "NOT SET"
			addonprefs.Back1 = "S"
			addonprefs.Back2 = "NOT SET"
			addonprefs.Back3 = "NOT SET"
			addonprefs.Up1 = "E"
			addonprefs.Up2 = "SPACE"
			addonprefs.Up3 = "NOT SET"
			addonprefs.Down1 = "Q"
			addonprefs.Down2 = "C"
			addonprefs.Down3 = "X"
		elif addonprefs.Keyboard == "AZERTY":
			addonprefs.Left1 = "Q"
			addonprefs.Left2 = "NOT SET"
			addonprefs.Left3 = "NOT SET"
			addonprefs.Right1 = "D"
			addonprefs.Right2 = "NOT SET"
			addonprefs.Right3 = "NOT SET"
			addonprefs.Forward1 = "Z"
			addonprefs.Forward2 = "NOT SET"
			addonprefs.Forward3 = "NOT SET"
			addonprefs.Back1 = "S"
			addonprefs.Back2 = "NOT SET"
			addonprefs.Back3 = "NOT SET"
			addonprefs.Up1 = "E"
			addonprefs.Up2 = "SPACE"
			addonprefs.Up3 = "NOT SET"
			addonprefs.Down1 = "A"
			addonprefs.Down2 = "C"
			addonprefs.Down3 = "X"
		oldkeyboard = addonprefs.Keyboard


@persistent
def loadpost_handler(dummy):

	global started, ready

	started = 0
	ready = 1


