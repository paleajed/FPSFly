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
	"version": (0, 3, 2),
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
from ctypes import *
#from ctypes.wintypes import BOOL
if sys.platform == "darwin":
	from Quartz.CoreGraphics import CGEventCreateMouseEvent
	from Quartz.CoreGraphics import CGEventPost
	from Quartz.CoreGraphics import kCGEventMouseMoved
	from Quartz.CoreGraphics import kCGMouseButtonLeft
	from Quartz.CoreGraphics import kCGHIDEventTap
	
class Rect(Structure):
	_fields_=[("left",c_long),("top",c_long),("right",c_long),("bottom",c_long)]
Window = Rect()

    
class Color(Structure):
	_fields_=[("pixel",c_ulong),("red",c_ushort),("green",c_ushort),("blue",c_ushort),("flags",c_char),("pad",c_char)]
black = Color()
black.red = 0
black.green = 0
black.blue = 0
if sys.platform == "linux":
	dll = cdll.LoadLibrary('libX11.so')

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
msync = 0
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




class SimpleMouseOperator(bpy.types.Operator):
	bl_idname = "wm.fps_mouse_position"
	bl_label = "Invoke Mouse Operator"

	def invoke(self, context, event):

		global mxcenter, mycenter

		mxcenter = event.mouse_x
		mycenter = event.mouse_y
		
		return {'FINISHED'}


class FPSFlyPanel(bpy.types.Panel):
	bl_label = "FPSFly"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	def draw(self, context):
		
		scn = bpy.context.scene
		
		self.layout.prop(scn, "Toggle")


class FPSFlyAddonPreferences(bpy.types.AddonPreferences):

	bl_idname = "space_view3d_fpsfly"
	
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



class FPSFlyStart(bpy.types.Operator):
	bl_idname = "view3d.fpsfly"
	bl_label = "Start FPSFly"
	bl_description = "FPS viewport navigation"
	bl_options = {"REGISTER"}
	
	def invoke(self, context, event):
	
		global addonprefs
	
		scn = bpy.context.scene

		addonprefs = bpy.context.user_preferences.addons["space_view3d_fpsfly"].preferences
		
		context.window_manager.modal_handler_add(self)
		
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
	
		global navon, leftnav, rightnav, forwardnav, backnav, upnav, downnav
		global movetimer, leave, msync, acton
		global rv3d, region
		
		scn = bpy.context.scene
		
		for region in bpy.context.area.regions:
			if region.type == "UI":
				regionui = region
				
		if msync:
			msync = 0
			bpy.ops.wm.fps_mouse_position("INVOKE_DEFAULT")
			
		def hidemouse():
		
			global Xdisplay, Xwindow, prevcursor, bitmap
			global msync, xcenter, ycenter
		
			msync = 1
			if sys.platform == "linux":
				xcenter = 400
				ycenter = 400
				Xdisplay = dll.XOpenDisplay(None)
				Xwindow = dll.XDefaultRootWindow(Xdisplay)
				dll.XWarpPointer(Xdisplay, None, Xwindow, 0, 0, 0, 0, xcenter, ycenter)
				dll.XSync(Xdisplay, True)
				pyarr = [0,0,0,0,0,0,0,0]
				arr = (c_int * len(pyarr))(*pyarr)
				bitmap = dll.XCreateBitmapFromData(Xdisplay, Xwindow, arr, 8, 8)
				invicursor = dll.XCreatePixmapCursor(Xdisplay, bitmap, bitmap, byref(black), byref(black), 0, 0)		
				dll.XDefineCursor(Xdisplay, Xwindow, invicursor)
				dll.XFreeCursor(Xdisplay, invicursor)
				dll.XSync(Xdisplay, True)
			elif sys.platform == "win32":
				wind = windll.user32.GetActiveWindow()
				windll.user32.GetWindowRect(wind, byref(Window))
				xcenter = int(Window.left + region.x + region.width/2)
				ycenter = int(Window.bottom - region.y - region.height/2)
				print (xcenter, ycenter)
				windll.user32.SetCursorPos(xcenter, ycenter)
			elif sys.platform == "darwin":
				xcenter = 400
				ycenter = 400
				mouseevent = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (xcenter, ycenter), kCGMouseButtonLeft)
				CGEventPost(kCGHIDEventTap, mouseevent)
				
		if not(navon):
			if event.type in ["F"]:
				if event.shift and event.ctrl and not(event.alt) and event.value == "PRESS":
					navon = 1
					scn.Toggle = 1
					regionui.tag_redraw()
					rv3d = bpy.context.space_data.region_3d
					scn.PreSelOff = 1
					bpy.context.region.tag_redraw()
					hidemouse()
					return {'RUNNING_MODAL'}
			if scn.Toggle and not(navon):
				navon = 1
				rv3d = bpy.context.space_data.region_3d
				scn.PreSelOff = 1
				bpy.context.region.tag_redraw()
				hidemouse()
				return {'RUNNING_MODAL'}
			
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
			return {'RUNNING_MODAL'}
		
		off = 0
		if event.type in ["F"]:
			if event.shift and event.ctrl and not(event.alt) and event.value == "PRESS":
				off = 1
		if off or event.type in ["ESC"] or not(scn.Toggle):
			if sys.platform == "linux":
				dll.XWarpPointer(Xdisplay, None, Xwindow, 0, 0, 0, 0, xcenter, ycenter)
				cursor = dll.XCreateFontCursor(Xdisplay, c_long(68))
				dll.XDefineCursor(Xdisplay, Xwindow, cursor)
				dll.XFreeCursor(Xdisplay, cursor)
				dll.XCloseDisplay(Xdisplay)
			elif sys.platform == "win32":
				windll.user32.SetCursorPos(xcenter, ycenter)
			elif sys.platform == "darwin":
				mouseevent = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (xcenter, ycenter), kCGMouseButtonLeft)
				CGEventPost(kCGHIDEventTap, mouseevent)

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
			return {'RUNNING_MODAL'}
			
		if event.type in ["WHEELUPMOUSE"]:
			addonprefs.Speed *= 1.5
		if event.type in ["WHEELDOWNMOUSE"]:
			addonprefs.Speed *= 0.8
			if addonprefs.Speed == 0:
				addonprefs.Speed = 2
			
		if event.type in ["RIGHTMOUSE"]:
			if event.value == "PRESS" and addonprefs.ActPass:
				acton = 1
			else:
				acton = 0
		if addonprefs.ActPass == 0:
			acton = 1
				
		if event.type in ["MOUSEMOVE", "LEFTMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"]:
			if event.type in ["MOUSEMOVE"]:
				if mx == mxcenter and my == mycenter:
					return {'RUNNING_MODAL'}
				if sys.platform == "linux":
					dll.XWarpPointer(Xdisplay, None, Xwindow, 0, 0, 0, 0, xcenter, ycenter)
					dll.XSync(Xdisplay, True)
				elif sys.platform == "win32":
					windll.user32.SetCursorPos(xcenter, ycenter)
				elif sys.platform == "darwin":
					mouseevent = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (xcenter, ycenter), kCGMouseButtonLeft)
					CGEventPost(kCGHIDEventTap, mouseevent)
			if acton and event.type in ["MOUSEMOVE"] and rv3d:
				if addonprefs.YMirror:
					ymult = -1
				else:
					ymult = 1
				smult = (addonprefs.MSens / 10) + 0.1
				dx = mx - mxcenter
				dy = my - mycenter
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
				return {'RUNNING_MODAL'}
			
		if event.type in [lkey[addonprefs.Keyboard]]:
			if event.value == "PRESS":
				leftnav = 1
			else:
				leftnav = 0
		elif event.type in [rkey[addonprefs.Keyboard]]:
			if event.value == "PRESS":
				rightnav = 1
			else:
				rightnav = 0
		elif event.type in [fkey[addonprefs.Keyboard]]:
			if event.value == "PRESS":
				forwardnav = 1
			else:
				forwardnav = 0
		elif event.type in [bkey[addonprefs.Keyboard]]:
			if event.value == "PRESS":
				backnav = 1
			else:
				backnav = 0
		elif event.type in ukey[addonprefs.Keyboard]:
			if event.value == "PRESS":
				upnav = 1
			else:
				upnav = 0
		elif event.type in dkey[addonprefs.Keyboard]:
			if event.value == "PRESS":
				downnav = 1
			else:
				downnav = 0
				
			

		return {'RUNNING_MODAL'}

	

def register():

	global _handle, ready

	bpy.utils.register_module(__name__)
	_handle = bpy.types.SpaceView3D.draw_handler_add(redraw, (), 'WINDOW', 'POST_PIXEL')
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

		
@persistent
def loadpost_handler(dummy):

	global started, ready

	started = 0
	ready = 1


