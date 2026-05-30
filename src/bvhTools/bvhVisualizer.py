import pyray as rl
from bvhTools.bvhManipulation import standSkeletonOnFloor
from bvhTools.bvhDataTypes import BVHData
import math
import time

def _changeCameraMode(mode):
    if(mode=="Free"): return "Still"
    if(mode=="Still"): return "Follow"
    if(mode=="Follow"): return "Free"

def _changeCurrentBvh(currentBvh, maxBvh):
    currentBvh += 1
    if(currentBvh > maxBvh): currentBvh = 0
    return currentBvh

def _precomputeLabels(bvh):
    labels = []
    for joint in bvh.skeleton.joints:
        jointName = joint if not "EndSite" in joint else ""
        size = rl.measure_text(jointName, 10)
        label = rl.load_render_texture(size, 10)
        rl.begin_texture_mode(label)
        rl.clear_background(rl.BLANK)
        rl.draw_text(jointName, 0, 0, 10, rl.BLACK)
        rl.end_texture_mode()
        labels.append(label)
    return labels

def showBvhAnimation(bvhData: BVHData) -> None:
    if(not isinstance(bvhData, BVHData) and not (isinstance(bvhData, list) and all(isinstance(b, BVHData) for b in bvhData))):
        print(f"\033[1;33mWARNING\033[0m: You must provide either a single BVHData object or a list of BVHData objects.")
        return
    if(isinstance(bvhData, BVHData)):
        bvhData = [bvhData]
    # Camera + Misc Control variables
    CAMERA_MODE = "Free" # Free, Follow, Still
    CAMERA_OBJECTIVE_ZOOM = 10.0
    CAMERA_OBJECTIVE_HEIGHT = 1.0
    CAMERA_OBJECTIVE_ANGLE = 45.0
    CURRENT_BVH = 0
    MAX_BVH = len(bvhData)-1
    SHOW_AXES = rl.ffi.new('bool *', True)
    SHOW_GRID = rl.ffi.new('bool *', True)
    # Animation Control variables
    IS_PLAYING  = True

    # Visualization variables
    COLOR1 = rl.Color(220, 86, 68, 255)
    COLOR2 = rl.Color(68, 160, 220, 255)
    COLOR3 = rl.Color(68, 220, 125, 255)
    COLOR4 = rl.Color(220, 153, 68, 255)
    COLOR5 = rl.Color(147, 68, 220, 255)
    COLOR6 = rl.Color(220, 216, 68, 255)
    COLORS = [COLOR1, COLOR2, COLOR3, COLOR4, COLOR5, COLOR6]
    if(len(bvhData)>len(COLORS)): # If there are more BVHs, generate random colors
        for i in range(len(bvhData)-len(COLORS)):
            COLORS.append(rl.Color(int.from_bytes(rl.get_random_value(0, 255).to_bytes(4, 'little'), 'little'), int.from_bytes(rl.get_random_value(0, 255).to_bytes(4, 'little'), 'little'), int.from_bytes(rl.get_random_value(0, 255).to_bytes(4, 'little'), 'little'), 255))
    RADIUSES = []
    SHOW_LABELS = []
    CURRENT_FRAME = rl.ffi.new('float *', 0.0)
    MAX_FRAME = 0
    SHOW_UI = True
    
    screen_width = 1920
    screen_height = 1080
    rl.set_config_flags(rl.FLAG_WINDOW_RESIZABLE)
    rl.init_window(screen_width, screen_height, "BVH Visualizer")

    rl.begin_drawing()
    rl.clear_background(rl.RAYWHITE)
    rl.draw_text("Loading BVH files...", 860, 540, 24, rl.BLACK)
    rl.end_drawing()
    
    camera = rl.Camera3D(
        rl.Vector3(4.0, 4.0, 4.0),   # position
        rl.Vector3(0.0, 1.0, 0.0),   # target
        rl.Vector3(0.0, 1.0, 0.0),   # up
        45.0,                        # fovy
        rl.CAMERA_PERSPECTIVE        # projection
    )

    bvhList = [standSkeletonOnFloor(bvh, "LeftToe", "RightToe") for bvh in bvhData]
    fkList = [[bvh.getFKAtFrameNormalized(x, "height") for x in range(bvh.motion.numFrames)] for bvh in bvhList]
    MAX_FRAME = max(bvh.motion.numFrames for bvh in bvhList)
    RADIUSES = [rl.ffi.new('float *', 0.1) for bvh in bvhList]
    SHOW_LABELS = [rl.ffi.new('bool *', False) for bvh in bvhList]
    LABELS = [_precomputeLabels(bvh) for bvh in bvhList]
    
    rl.set_target_fps(int(bvhList[0].motion.getFPS()))

    while not rl.window_should_close():
        screen_width = rl.get_screen_width()
        screen_height = rl.get_screen_height()

        if(CAMERA_MODE == "Free"):
            rl.update_camera(camera, rl.CAMERA_FREE)
        elif(CAMERA_MODE == "Follow"):
            CAMERA_OBJECTIVE_ZOOM -= rl.get_mouse_wheel_move() * 0.4
            angle = (rl.is_key_down(rl.KEY_A) - rl.is_key_down(rl.KEY_D)) * 2.0
            CAMERA_OBJECTIVE_ANGLE += angle
            height = (rl.is_key_down(rl.KEY_W) - rl.is_key_down(rl.KEY_S)) * 0.1
            CAMERA_OBJECTIVE_HEIGHT += height
            rl.update_camera(camera, rl.CAMERA_CUSTOM)
            target = fkList[CURRENT_BVH][min(bvhList[CURRENT_BVH].motion.numFrames-1, int(CURRENT_FRAME[0]))][bvhList[CURRENT_BVH].skeleton.root.name][1]
            target = rl.Vector3(target[0], target[1], target[2])
            camera.position = rl.vector3_add(target, rl.vector3_scale(rl.Vector3(math.sin(math.radians(CAMERA_OBJECTIVE_ANGLE)), CAMERA_OBJECTIVE_HEIGHT, math.cos(math.radians(CAMERA_OBJECTIVE_ANGLE))), CAMERA_OBJECTIVE_ZOOM))
            camera.target = target
        elif(CAMERA_MODE == "Still"):
            pass

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode_3d(camera)

        if(SHOW_GRID[0]):
            rl.draw_grid(100, 1.0)

        if(SHOW_AXES[0]):
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 0.0), rl.Vector3(1.0, 0.0, 0.0), rl.RED)
            rl.draw_line_3d(rl.Vector3(1.0, 0.0, 0.0), rl.Vector3(0.7, 0.0, 0.3), rl.RED)
            rl.draw_line_3d(rl.Vector3(1.0, 0.0, 0.0), rl.Vector3(0.7, 0.0, -0.3), rl.RED)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 0.0), rl.Vector3(0.0, 1.0, 0.0), rl.BLUE)
            rl.draw_line_3d(rl.Vector3(0.0, 1.0, 0.0), rl.Vector3(0.0, 0.7, 0.3), rl.BLUE)
            rl.draw_line_3d(rl.Vector3(0.0, 1.0, 0.0), rl.Vector3(0.0, 0.7, -0.3), rl.BLUE)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 0.0), rl.Vector3(0.0, 0.0, 1.0), rl.GREEN)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 1.0), rl.Vector3(0.3, 0.0, 0.7), rl.GREEN)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 1.0), rl.Vector3(-0.3, 0.0, 0.7), rl.GREEN)

        for index, (bvh, fk) in enumerate(zip(bvhList, fkList)):
            for jointIndex, joint in enumerate(bvh.skeleton.joints.values()):
                if(len(joint.children)>0):
                    p1 = fk[min(bvh.motion.numFrames-1, int(CURRENT_FRAME[0]))][joint.name][1]
                    if(SHOW_LABELS[index][0]):
                        tex = LABELS[index][jointIndex-1].texture
                        labelPos = rl.vector3_add(rl.Vector3(p2[0], p2[1], p2[2]), rl.vector3_scale((rl.vector3_subtract(rl.Vector3(p2[0], p2[1], p2[2]), camera.position)), -0.1))
                        rl.draw_billboard_rec(camera, tex, rl.Rectangle(0, 0, tex.width, -tex.height), labelPos, rl.Vector2(tex.width * 0.01, tex.height * 0.01), rl.WHITE)
                    for child in joint.children:
                        p2 = fk[min(bvh.motion.numFrames-1, int(CURRENT_FRAME[0]))][child.name][1]
                        rl.draw_capsule(rl.Vector3(p1[0], p1[1], p1[2]), rl.Vector3(p2[0], p2[1], p2[2]), RADIUSES[index][0], 10, 5, COLORS[index])
                        rl.draw_capsule_wires(rl.Vector3(p1[0], p1[1], p1[2]), rl.Vector3(p2[0], p2[1], p2[2]), RADIUSES[index][0], 5, 5, rl.BLACK)

        rl.end_mode_3d()
        if(rl.is_key_pressed(rl.KEY_ENTER)):
            CURRENT_BVH = _changeCurrentBvh(CURRENT_BVH, MAX_BVH)

        if(rl.is_key_pressed(rl.KEY_H)):
            SHOW_UI = not SHOW_UI

        if(rl.is_key_pressed(rl.KEY_C)):
            t = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime())
            rl.take_screenshot(f"screenshot_{t}.png")

        if(SHOW_UI):
            # --- CAMERA CONTROLS UI ---
            rl.gui_panel(rl.Rectangle(10, 10, 200, 190), "Camera Controls")
            if(CAMERA_MODE == "Free"):
                if(rl.gui_button(rl.Rectangle(20, 40, 180, 20), "Camera: Free [TAB]") or rl.is_key_pressed(rl.KEY_TAB)):
                    CAMERA_MODE = _changeCameraMode(CAMERA_MODE)
                rl.gui_label(rl.Rectangle(20, 70, 180, 20), "Control with mouse + WASD")
            elif(CAMERA_MODE == "Follow"):
                if(rl.gui_button(rl.Rectangle(20, 40, 180, 20), "Camera: Follow [TAB]") or rl.is_key_pressed(rl.KEY_TAB)):
                    CAMERA_MODE = _changeCameraMode(CAMERA_MODE)
                if(rl.gui_button(rl.Rectangle(20, 70, 180, 20), f"Current BVH: {CURRENT_BVH} [ENTER]")):
                    CURRENT_BVH = _changeCurrentBvh(CURRENT_BVH, MAX_BVH)
                rl.gui_label(rl.Rectangle(20, 100, 180, 20), "A, D: rotate the camera")
                rl.gui_label(rl.Rectangle(20, 130, 180, 20), "W, S: go up and down")
                rl.gui_label(rl.Rectangle(20, 160, 180, 20), "Mouse Wheel: zoom")
            elif(CAMERA_MODE == "Still"):
                if(rl.gui_button(rl.Rectangle(20, 40, 180, 20), "Camera: Still [TAB]") or rl.is_key_pressed(rl.KEY_TAB)):
                    CAMERA_MODE = _changeCameraMode(CAMERA_MODE)
            # --- MISC CONTROLS UI --- 
            rl.gui_panel(rl.Rectangle(10, 230, 200, 400), f"Character {CURRENT_BVH} Controls")
            rl.gui_color_picker(rl.Rectangle(20, 260, 150, 150), "Color", COLORS[CURRENT_BVH])
            rl.gui_label(rl.Rectangle(20, 430, 180, 20), "Capsule radius")
            rl.gui_slider_bar(rl.Rectangle(50, 450, 130, 20), "0.001", "0.2", RADIUSES[CURRENT_BVH], 0.001, 0.2)
            rl.gui_check_box(rl.Rectangle(20, 480, 20, 20), "Show labels", SHOW_LABELS[CURRENT_BVH])

            # INFORMATION CONTROL
            rl.gui_panel(rl.Rectangle(screen_width - 210, 10, 200, 150), "Information")
            rl.gui_label(rl.Rectangle(screen_width - 200, 40, 180, 20), f"Current BVH: {CURRENT_BVH}")
            rl.gui_label(rl.Rectangle(screen_width - 200, 70, 180, 20), f"FPS: {bvhList[CURRENT_BVH].motion.getFPS():.4f}")
            rl.gui_label(rl.Rectangle(screen_width - 200, 100, 180, 20), f"Frame Time: {bvhList[CURRENT_BVH].motion.frameTime:.4f}")
            rl.gui_label(rl.Rectangle(screen_width - 200, 130, 180, 20), f"Frames: {bvhList[CURRENT_BVH].motion.numFrames}")
            
            # OTHER CONTROLS
            rl.gui_panel(rl.Rectangle(screen_width - 210, 180, 200, 150), "Other controls")
            rl.gui_label(rl.Rectangle(screen_width - 200, 210, 180, 20), "Show/hide GUI [h]")
            rl.gui_label(rl.Rectangle(screen_width - 200, 240, 180, 20), "Take screenshot [c]")
            rl.gui_check_box(rl.Rectangle(screen_width - 200, 270, 20, 20), "Show Axes", SHOW_AXES)
            rl.gui_check_box(rl.Rectangle(screen_width - 200, 300, 20, 20), "Show Grid", SHOW_GRID)
            
            # --- ANIMATION CONTROLS UI ---
            rl.gui_panel(rl.Rectangle(150, screen_height - 150, screen_width - 300, 100), "Animation Controls")
            rl.gui_slider_bar(rl.Rectangle(190, screen_height - 110, screen_width - 370, 20), f"{int(CURRENT_FRAME[0])}", f"{MAX_FRAME}", CURRENT_FRAME, 0, MAX_FRAME)
            if(rl.gui_button(rl.Rectangle(int(screen_width / 2) - 140, screen_height - 80, 80, 20), "<<")):
                IS_PLAYING = False
                if(CURRENT_FRAME[0] > 0):
                    CURRENT_FRAME[0] -= 1
                else:
                    CURRENT_FRAME[0] = MAX_FRAME - 1
            if(rl.gui_button(rl.Rectangle(int(screen_width / 2) + 60, screen_height - 80, 80, 20), ">>")):
                IS_PLAYING = False
                if(CURRENT_FRAME[0] < MAX_FRAME - 1):
                    CURRENT_FRAME[0] += 1
                else:
                    CURRENT_FRAME[0] = 0
            if IS_PLAYING:
                if(rl.gui_button(rl.Rectangle(int(screen_width / 2) - 40, screen_height - 80, 80, 20), "Pause")): IS_PLAYING = not IS_PLAYING
            else:
                if(rl.gui_button(rl.Rectangle(int(screen_width / 2) - 40, screen_height - 80, 80, 20), "Play")): IS_PLAYING = not IS_PLAYING

        if(IS_PLAYING): CURRENT_FRAME[0] +=1
        if(int(CURRENT_FRAME[0]) >= MAX_FRAME): CURRENT_FRAME[0] = 0
        rl.end_drawing()

    rl.close_window()

def showOnionSkinAnimation(bvhData: BVHData) -> None:
    if(not isinstance(bvhData, BVHData) and not (isinstance(bvhData, list) and all(isinstance(b, BVHData) for b in bvhData))):
        print(f"\033[1;33mWARNING\033[0m: You must provide either a single BVHData object or a list of BVHData objects.")
        return
    if(isinstance(bvhData, BVHData)):
        bvhData = [bvhData]
    # Camera + Misc Control variables
    CAMERA_MODE = "Free" # Free, Follow, Still
    CAMERA_OBJECTIVE_ZOOM = 10.0
    CAMERA_OBJECTIVE_HEIGHT = 1.0
    CAMERA_OBJECTIVE_ANGLE = 45.0
    CURRENT_BVH = 0
    MAX_BVH = len(bvhData)-1
    SHOW_AXES = rl.ffi.new('bool *', True)
    SHOW_GRID = rl.ffi.new('bool *', True)

    # Visualization variables
    COLOR1 = rl.Color(220, 86, 68, 10)
    COLOR2 = rl.Color(68, 160, 220, 10)
    COLOR3 = rl.Color(68, 220, 125, 10)
    COLOR4 = rl.Color(220, 153, 68, 10)
    COLOR5 = rl.Color(147, 68, 220, 10)
    COLOR6 = rl.Color(220, 216, 68, 10)
    COLORS = [COLOR1, COLOR2, COLOR3, COLOR4, COLOR5, COLOR6]
    ALPHAS = [rl.ffi.new('float *', 10.0) for bvh in bvhData]
    if(len(bvhData)>len(COLORS)): # If there are more BVHs, generate random colors
        for i in range(len(bvhData)-len(COLORS)):
            COLORS.append(rl.Color(int.from_bytes(rl.get_random_value(0, 10).to_bytes(4, 'little'), 'little'), int.from_bytes(rl.get_random_value(0, 10).to_bytes(4, 'little'), 'little'), int.from_bytes(rl.get_random_value(0, 10).to_bytes(4, 'little'), 'little'), 10))
    RADIUSES = []
    SHOW_WIREFRAME = []
    SHOW_UI = True
    
    screen_width = 1920
    screen_height = 1080
    rl.set_config_flags(rl.FLAG_WINDOW_RESIZABLE)
    rl.init_window(screen_width, screen_height, "BVH Onion Skin Visualizer")

    rl.begin_drawing()
    rl.clear_background(rl.RAYWHITE)
    rl.draw_text("Loading BVH files...", 860, 540, 24, rl.BLACK)
    rl.end_drawing()
    
    camera = rl.Camera3D(
        rl.Vector3(4.0, 4.0, 4.0),   # position
        rl.Vector3(0.0, 1.0, 0.0),   # target
        rl.Vector3(0.0, 1.0, 0.0),   # up
        45.0,                        # fovy
        rl.CAMERA_PERSPECTIVE        # projection
    )

    bvhList = [standSkeletonOnFloor(bvh, "LeftToe", "RightToe") for bvh in bvhData]
    fkList = [[bvh.getFKAtFrameNormalized(x, "height") for x in range(bvh.motion.numFrames)] for bvh in bvhList]
    SHOW_WIREFRAME = [rl.ffi.new('bool *', False) for bvh in bvhList]
    RADIUSES = [rl.ffi.new('float *', 0.1) for bvh in bvhList]
    
    rl.set_target_fps(30)

    while not rl.window_should_close():
        screen_width = rl.get_screen_width()
        screen_height = rl.get_screen_height()

        if(CAMERA_MODE == "Free"):
            rl.update_camera(camera, rl.CAMERA_FREE)
        elif(CAMERA_MODE == "Follow"):
            CAMERA_OBJECTIVE_ZOOM -= rl.get_mouse_wheel_move() * 0.4
            angle = (rl.is_key_down(rl.KEY_A) - rl.is_key_down(rl.KEY_D)) * 2.0
            CAMERA_OBJECTIVE_ANGLE += angle
            height = (rl.is_key_down(rl.KEY_W) - rl.is_key_down(rl.KEY_S)) * 0.1
            CAMERA_OBJECTIVE_HEIGHT += height
            rl.update_camera(camera, rl.CAMERA_CUSTOM)
            target = fkList[CURRENT_BVH][0][bvhList[CURRENT_BVH].skeleton.root.name][1]
            target = rl.Vector3(target[0], target[1], target[2])
            camera.position = rl.vector3_add(target, rl.vector3_scale(rl.Vector3(math.sin(math.radians(CAMERA_OBJECTIVE_ANGLE)), CAMERA_OBJECTIVE_HEIGHT, math.cos(math.radians(CAMERA_OBJECTIVE_ANGLE))), CAMERA_OBJECTIVE_ZOOM))
            camera.target = target
        elif(CAMERA_MODE == "Still"):
            pass

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode_3d(camera)

        if(SHOW_GRID[0]):
            rl.draw_grid(100, 1.0)

        if(SHOW_AXES[0]):
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 0.0), rl.Vector3(1.0, 0.0, 0.0), rl.RED)
            rl.draw_line_3d(rl.Vector3(1.0, 0.0, 0.0), rl.Vector3(0.7, 0.0, 0.3), rl.RED)
            rl.draw_line_3d(rl.Vector3(1.0, 0.0, 0.0), rl.Vector3(0.7, 0.0, -0.3), rl.RED)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 0.0), rl.Vector3(0.0, 1.0, 0.0), rl.BLUE)
            rl.draw_line_3d(rl.Vector3(0.0, 1.0, 0.0), rl.Vector3(0.0, 0.7, 0.3), rl.BLUE)
            rl.draw_line_3d(rl.Vector3(0.0, 1.0, 0.0), rl.Vector3(0.0, 0.7, -0.3), rl.BLUE)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 0.0), rl.Vector3(0.0, 0.0, 1.0), rl.GREEN)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 1.0), rl.Vector3(0.3, 0.0, 0.7), rl.GREEN)
            rl.draw_line_3d(rl.Vector3(0.0, 0.0, 1.0), rl.Vector3(-0.3, 0.0, 0.7), rl.GREEN)
        
        rl.rl_disable_depth_mask()   # disables depth writing
        for index, (bvh, fk) in enumerate(zip(bvhList, fkList)):
            for frame in range(len(fk)):
                for jointIndex, joint in enumerate(bvh.skeleton.joints.values()):
                    if(len(joint.children)>0):
                        p1 = fk[frame][joint.name][1]
                        for child in joint.children:
                            p2 = fk[frame][child.name][1]
                            rl.draw_capsule(rl.Vector3(p1[0], p1[1], p1[2]), rl.Vector3(p2[0], p2[1], p2[2]), RADIUSES[index][0], 10, 5, COLORS[index])
                            if(SHOW_WIREFRAME[index][0]):
                                wireColor = rl.Color(0, 0, 0, int(ALPHAS[CURRENT_BVH][0]))
                                rl.draw_capsule_wires(rl.Vector3(p1[0], p1[1], p1[2]), rl.Vector3(p2[0], p2[1], p2[2]), RADIUSES[index][0], 5, 5, wireColor)
        rl.rl_enable_depth_mask()

        rl.end_mode_3d()
        if(rl.is_key_pressed(rl.KEY_ENTER)):
            CURRENT_BVH = _changeCurrentBvh(CURRENT_BVH, MAX_BVH)

        if(rl.is_key_pressed(rl.KEY_H)):
            SHOW_UI = not SHOW_UI

        if(rl.is_key_pressed(rl.KEY_C)):
            t = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime())
            rl.take_screenshot(f"screenshot_{t}.png")

        if(SHOW_UI):
            # --- CAMERA CONTROLS UI ---
            rl.gui_panel(rl.Rectangle(10, 10, 200, 190), "Camera Controls")
            if(CAMERA_MODE == "Free"):
                if(rl.gui_button(rl.Rectangle(20, 40, 180, 20), "Camera: Free [TAB]") or rl.is_key_pressed(rl.KEY_TAB)):
                    CAMERA_MODE = _changeCameraMode(CAMERA_MODE)
                rl.gui_label(rl.Rectangle(20, 70, 180, 20), "Control with mouse + WASD")
            elif(CAMERA_MODE == "Follow"):
                if(rl.gui_button(rl.Rectangle(20, 40, 180, 20), "Camera: Follow [TAB]") or rl.is_key_pressed(rl.KEY_TAB)):
                    CAMERA_MODE = _changeCameraMode(CAMERA_MODE)
                if(rl.gui_button(rl.Rectangle(20, 70, 180, 20), f"Current BVH: {CURRENT_BVH} [ENTER]")):
                    CURRENT_BVH = _changeCurrentBvh(CURRENT_BVH, MAX_BVH)
                rl.gui_label(rl.Rectangle(20, 100, 180, 20), "A, D: rotate the camera")
                rl.gui_label(rl.Rectangle(20, 130, 180, 20), "W, S: go up and down")
                rl.gui_label(rl.Rectangle(20, 160, 180, 20), "Mouse Wheel: zoom")
            elif(CAMERA_MODE == "Still"):
                if(rl.gui_button(rl.Rectangle(20, 40, 180, 20), "Camera: Still [TAB]") or rl.is_key_pressed(rl.KEY_TAB)):
                    CAMERA_MODE = _changeCameraMode(CAMERA_MODE)
            # --- MISC CONTROLS UI --- 
            rl.gui_panel(rl.Rectangle(10, 230, 200, 400), f"Character {CURRENT_BVH} Controls")
            rl.gui_color_picker(rl.Rectangle(20, 260, 150, 150), "Color", COLORS[CURRENT_BVH])
            rl.gui_label(rl.Rectangle(20, 430, 180, 20), "Transparency")
            rl.gui_slider_bar(rl.Rectangle(50, 450, 130, 20), "0", "255", ALPHAS[CURRENT_BVH], 0, 255)
            COLORS[CURRENT_BVH].a = int(ALPHAS[CURRENT_BVH][0])
            rl.gui_label(rl.Rectangle(20, 480, 180, 20), "Capsule radius")
            rl.gui_slider_bar(rl.Rectangle(50, 510, 130, 20), "0.001", "0.2", RADIUSES[CURRENT_BVH], 0.001, 0.2)
            rl.gui_check_box(rl.Rectangle(20, 540, 20, 20), "Show Wireframe", SHOW_WIREFRAME[CURRENT_BVH])

            # INFORMATION CONTROL
            rl.gui_panel(rl.Rectangle(screen_width - 210, 10, 200, 150), "Information")
            rl.gui_label(rl.Rectangle(screen_width - 200, 40, 180, 20), f"Current BVH: {CURRENT_BVH}")
            rl.gui_label(rl.Rectangle(screen_width - 200, 70, 180, 20), f"FPS: {bvhList[CURRENT_BVH].motion.getFPS():.4f}")
            rl.gui_label(rl.Rectangle(screen_width - 200, 100, 180, 20), f"Frame Time: {bvhList[CURRENT_BVH].motion.frameTime:.4f}")
            rl.gui_label(rl.Rectangle(screen_width - 200, 130, 180, 20), f"Frames: {bvhList[CURRENT_BVH].motion.numFrames}")
            
            # OTHER CONTROLS
            rl.gui_panel(rl.Rectangle(screen_width - 210, 180, 200, 150), "Other controls")
            rl.gui_label(rl.Rectangle(screen_width - 200, 210, 180, 20), "Show/hide GUI [h]")
            rl.gui_label(rl.Rectangle(screen_width - 200, 240, 180, 20), "Take screenshot [c]")
            rl.gui_check_box(rl.Rectangle(screen_width - 200, 270, 20, 20), "Show Axes", SHOW_AXES)
            rl.gui_check_box(rl.Rectangle(screen_width - 200, 300, 20, 20), "Show Grid", SHOW_GRID)
            
            # --- ANIMATION CONTROLS UI ---
            rl.gui_panel(rl.Rectangle(150, screen_height - 150, screen_width - 300, 100), "Animation Controls")

        rl.end_drawing()

    rl.close_window()