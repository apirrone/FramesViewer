import numpy as np
from OpenGL.GLUT import glutGetModifiers


class Inputs:
    def __init__(self):
        self.__inputs_state = {
            "prev_mouse_pos": np.array([0, 0]),
            "mouse_rel": np.array([0, 0]),
            "mouse_l_pressed": False,
            "mouse_m_pressed": False,
            "mouse_r_pressed": False,
            "ctrl_pressed": False,
            "wheel_up": False,
            "wheel_down": False,
            "key_pressed": None,
        }

    # Callbacks
    def mouse_click(self, button, mode, x, y):
        if mode == 0:
            self.__inputs_state["prev_mouse_pos"] = np.array([x, y])
        else:
            self.__inputs_state["prev_mouse_pos"] = np.array([0, 0])

        if button == 0:
            if mode == 0:
                self.__inputs_state["mouse_l_pressed"] = True
            elif mode == 1:
                self.__inputs_state["mouse_l_pressed"] = False

        if button == 1:
            if mode == 0:
                self.__inputs_state["mouse_m_pressed"] = True
            elif mode == 1:
                self.__inputs_state["mouse_m_pressed"] = False

        if button == 2:
            if mode == 0:
                self.__inputs_state["mouse_r_pressed"] = True
            elif mode == 1:
                self.__inputs_state["mouse_r_pressed"] = False

        if button == 3:
            self.__inputs_state["wheel_up"] = True
            self.__inputs_state["wheel_down"] = False
        elif button == 4:
            self.__inputs_state["wheel_down"] = True
            self.__inputs_state["wheel_up"] = False

        if glutGetModifiers() == 2:
            self.__inputs_state["ctrl_pressed"] = True
        else:
            self.__inputs_state["ctrl_pressed"] = False

    def mouse_motion(self, x, y):
        mouse_pos = np.array([x, y])
        self.__inputs_state["mouse_rel"] = (
            mouse_pos - self.__inputs_state["prev_mouse_pos"]
        )
        self.__inputs_state["prev_mouse_pos"] = mouse_pos.copy()

    def keyboard(self, key, x, y):
        self.__inputs_state["key_pressed"] = key

    # Getters and setters
    def get_inputs_state(self):
        return self.__inputs_state

    def get_mouse_rel(self):
        return self.__inputs_state["mouse_rel"]

    def set_mouse_rel(self, val):
        self.__inputs_state["mouse_rel"] = val

    def get_key_pressed(self):
        ret = self.__inputs_state["key_pressed"]
        self.__inputs_state["key_pressed"] = None
        return ret

    def mouse_l_pressed(self):
        return self.__inputs_state["mouse_l_pressed"]

    def mouse_m_pressed(self):
        return self.__inputs_state["mouse_m_pressed"]

    def mouse_r_pressed(self):
        return self.__inputs_state["mouse_r_pressed"]

    def ctrl_pressed(self):
        return self.__inputs_state["ctrl_pressed"]

    def wheel_up(self):
        ret = self.__inputs_state["wheel_up"]
        if self.__inputs_state["wheel_up"]:
            self.__inputs_state["wheel_up"] = False

        return ret

    def wheel_down(self):
        ret = self.__inputs_state["wheel_down"]
        if self.__inputs_state["wheel_down"]:
            self.__inputs_state["wheel_down"] = False

        return ret
