from settings import * 

class Timer():
    def __init__(self, app) -> None:
        self.app = app
        self.time: int = 0
    def tick(self): self.time = pg.time.get_ticks()


class Sumo_Bot():
    def __init__(self, app, img, pos) -> None:
        self.app = app
        self.img = img
        self.pos: vec2 = pos
        self.angle: float = 0
        self.vel: vec2= vec2(0)
        self.speed = 10
        self.move = False
        self.move_back = False
        self.turns = [0,0]
        self.target: Enemy
        self.line_detected_bool = False
        self.enemy_in_front_bool = False
        self.line_sensors = [False, False, False, False]
        self.time: int = 0

    def render(self, surf):
        image = pg.transform.rotate(self.img, -self.angle)
        img_rect = image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)

    def update(self):
        if self.move:
             self.move_forward()
        if self.move_back:
             self.move_backward()
        if self.turns[0]:
             self.turn_left()
        if self.turns[1]:
             self.turn_right()
        self.angle %= 360

        self.line_sensor()
        self.raycast()
        
        self.timer()
    
    def check_circle_collision(self, circle1, circle2):
        dist = math.sqrt( math.pow(circle1[0] - circle2[0], 2) + math.pow(circle1[1] - circle2[1], 2) )
        if dist < circle1[2] + circle2[2]:
             return True
        return False

    def line_sensor(self):
        self.line_sensors = [False, False, False, False]
        sensor_detected = False
        for offset in [45, 135, 225, 315]:
            x_speed = math.cos(math.radians(self.angle + offset)) * 26
            y_speed = math.sin(math.radians(self.angle + offset)) * 26
            front = vec2(self.pos.x + x_speed, self.pos.y + y_speed)
            pg.draw.circle(self.app.display, RED, (front.x, front.y), 4)
            if not self.check_circle_collision([front.x, front.y, 4], [CENTER.x, CENTER.y, 200]):
                self.move = False
                self.line_detected_bool = True
                sensor_detected = True

        if sensor_detected: self.line_detected_bool = False
    
    def line_detected(self): return self.line_detected_bool
        
    def enemy_in_front(self): return self.enemy_in_front_bool

    def move_forward(self):
        x_speed = math.cos( math.radians( self.angle  ) ) 
        y_speed = math.sin( math.radians( self.angle  ) ) 
        speed = vec2(x_speed, y_speed) * self.speed
        self.pos += speed

    def move_backward(self):
        x_speed = math.cos( math.radians( 180 + self.angle ) ) 
        y_speed = math.sin( math.radians( 180 + self.angle ) ) 
        speed = vec2(x_speed, y_speed) * self.speed
        self.pos += speed

    def turn_left(self):
         self.angle -= 6

    def turn_right(self):
         self.angle += 6

    def distance(self, px1, px2, py1, py2):
        return math.sqrt(pow(px1 - px2, 2) + pow(py1 - py2, 2))

    def raycast(self):
        #angle = math.atan2(self.target.pos.y - self.pos.y, self.target.pos.x - self.pos.x) + .0001
        angle = math.radians( self.angle)  + .0001
        if angle < 0:
            angle += 2 * math.pi
        if angle > math.pi * 2:
            angle -= 2 * math.pi

        horiz_dist = float('inf')
        vert_dist = float('inf')

        player_pos = self.pos.copy()

        horiz_x, horiz_y, horiz_hit = self.check_horizontal(angle, player_pos)
        vert_x, vert_y, vert_hit = self.check_vertical(angle, player_pos)

        horiz_dist = self.distance( player_pos.x, horiz_x, player_pos.y, horiz_y)
        vert_dist = self.distance( player_pos.x, vert_x, player_pos.y, vert_y )
        end_x = 0
        end_y = 0

        if vert_dist < horiz_dist:
            end_x, end_y = vert_x, vert_y
        if horiz_dist < vert_dist:
            end_x, end_y = horiz_x, horiz_y

        if not horiz_hit and not vert_hit:
            tile_key = f'{int(end_x // CELL_SIZE)},{int(end_y // CELL_SIZE)}'
            self.line_of_sight = False
            self.enemy_in_front_bool = False
        else:
            self.line_of_sight = True
            self.enemy_in_front_bool = True

        pg.draw.line(self.app.display, RED, (self.pos.x, self.pos.y), (end_x, end_y), 1)

    def check_horizontal(self, ray_angle, player_pos):
        player_x = player_pos.x
        player_y = player_pos.y
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        a_tan = -1 / math.tan(ray_angle)
        dof = 16
        player_hit = False

        if ray_angle > PI:  # looking up
            ray_pos_y = int(player_y // CELL_SIZE) * CELL_SIZE - .0001
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = -CELL_SIZE
            x_offset = -y_offset * a_tan
        if ray_angle < PI:  # looking down
            ray_pos_y = int(player_y // CELL_SIZE) * CELL_SIZE + CELL_SIZE
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = CELL_SIZE
            x_offset = -y_offset * a_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos.x // CELL_SIZE)},{int(self.target.pos.y // CELL_SIZE)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CELL_SIZE),
                       int(ray_pos_y // CELL_SIZE))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 15 or ray_pos[1] < -1 or ray_pos[1] > 15:
                break
            #if str_ray_pos in self.app.tile_map.tiles: break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit

    def check_vertical(self, ray_angle, player_pos):
        player_x = player_pos.x
        player_y = player_pos.y
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        n_tan = -math.tan(ray_angle)
        dof = 16
        player_hit = False

        P2 = math.pi / 2
        P3 = (math.pi * 3) / 2

        if ray_angle > P2 and ray_angle < P3:  # looking left
            ray_pos_x = int(player_x // CELL_SIZE) * CELL_SIZE - .0001
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = -CELL_SIZE
            y_offset = -x_offset * n_tan
        if ray_angle < P2 or ray_angle > P3:  # looking right
            ray_pos_x = int(player_x // CELL_SIZE) * CELL_SIZE + CELL_SIZE
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = CELL_SIZE
            y_offset = -x_offset * n_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos.x // CELL_SIZE)},{int(self.target.pos.y // CELL_SIZE)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CELL_SIZE),
                       int(ray_pos_y // CELL_SIZE))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 20 or ray_pos[1] < -1 or ray_pos[1] > 20:
                break
            #if str_ray_pos in self.app.tile_map.tiles: break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit
    

#---------------------------------------------STATE MACHINE---------------------------------------------#

# ALL STATES
class State_e(Enum):
	STATE_WAIT = 1
	STATE_SEARCH = 2
	STATE_ATTACK = 3
	STATE_RETREAT = 4
	STATE_MANUAL = 5
        
# ALL EVENTS THAT CAN HAPPEN
class StateEvent(Enum):
	STATE_EVENT_TIMEOUT = 1
	STATE_EVENT_LINE = 2
	STATE_EVENT_ENEMY = 3
	STATE_EVENT_FINISHED = 4
	STATE_EVENT_COMMAND = 5
	STATE_EVENT_NONE = 6
        

'''
    state machine will hold overall state machine logic 
    hold difference transitions
    define transitions
    handle inputs, translate into events to cause transition
'''
class StateMachine(): # State machine logic
    def __init__(self) -> None:
        self.state_e: State_e = State_e.STATE_WAIT # CURRENT STATE
        self.state_machine_common_data: StateMachineCommonData # COMMON USED DATA
        # hold data for individual states
        self.wait_state: Wait_State
        self.search_state: Search_State
        self.attack_state: Attack_State
        self.retreat_state: Retreat_State
        self.manual_state: Manual_State

    def state_machine_run(self):
        pass
        
# data & definitions to be shared, between different states
class StateMachineCommonData():
    def __init__(self) -> None:
        self.state_machine_data: StateMachine
        self.enemy: Enemy

# -----------------------------------SCENE_TRANSITION----------------------------------#
class Scene_Transition():
     def __init__(self, from_state, state_event, to_state) -> None:
        self.from_state: State_e = from_state
        self.event_state: StateEvent = state_event
        self.to_state: State_e = to_state

state_transitions = [
    Scene_Transition(State_e.STATE_WAIT, StateEvent.STATE_EVENT_NONE, State_e.STATE_WAIT),
    Scene_Transition(State_e.STATE_WAIT, StateEvent.STATE_EVENT_LINE, State_e.STATE_WAIT),
    Scene_Transition(State_e.STATE_WAIT, StateEvent.STATE_EVENT_ENEMY, State_e.STATE_WAIT),
    Scene_Transition(State_e.STATE_WAIT, StateEvent.STATE_EVENT_COMMAND, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_SEARCH, StateEvent.STATE_EVENT_NONE, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_SEARCH, StateEvent.STATE_EVENT_TIMEOUT, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_SEARCH, StateEvent.STATE_EVENT_ENEMY, State_e.STATE_ATTACK),
    Scene_Transition(State_e.STATE_SEARCH, StateEvent.STATE_EVENT_LINE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_SEARCH, StateEvent.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_ATTACK, StateEvent.STATE_EVENT_ENEMY, State_e.STATE_ATTACK),
    Scene_Transition(State_e.STATE_ATTACK, StateEvent.STATE_EVENT_LINE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_ATTACK, StateEvent.STATE_EVENT_NONE, State_e.STATE_SEARCH), # Enemy lost
    Scene_Transition(State_e.STATE_ATTACK, StateEvent.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_ATTACK, StateEvent.STATE_EVENT_TIMEOUT, State_e.STATE_ATTACK),
    Scene_Transition(State_e.STATE_RETREAT, StateEvent.STATE_EVENT_LINE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, StateEvent.STATE_EVENT_FINISHED, State_e.STATE_SEARCH),
    Scene_Transition(State_e.STATE_RETREAT, StateEvent.STATE_EVENT_TIMEOUT, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, StateEvent.STATE_EVENT_ENEMY, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, StateEvent.STATE_EVENT_NONE, State_e.STATE_RETREAT),
    Scene_Transition(State_e.STATE_RETREAT, StateEvent.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, StateEvent.STATE_EVENT_COMMAND, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, StateEvent.STATE_EVENT_NONE, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, StateEvent.STATE_EVENT_LINE, State_e.STATE_MANUAL),
    Scene_Transition(State_e.STATE_MANUAL, StateEvent.STATE_EVENT_ENEMY, State_e.STATE_MANUAL),
] 

# ---------------------------------SEARCH STATE----------------------------------#
class Search_State_e(Enum):
    SEARCH_STATE_ROTATE = 1
    SEARCH_STATE_FORWARD = 2

class Search_State():
     def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e

# ---------------------------------ATTACK STATE----------------------------------#


class Attack_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e

# ----------------------------------WAIT STATE-----------------------------------#


class Wait_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e


# ----------------------------------RETREAT STATE------------------------------------#

class Retreat_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e

# ------------------------------------MANUAL STATE------------------------------------#


class Manual_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e

# ------------------------------------------------------------------------------------#


class Enemy():
    def __init__(self, app, img, pos) -> None:
        self.app = app
        self.img = img
        self.pos: vec2 = pos
        self.angle = 0

    def render(self, surf):
        image = pg.transform.rotate(self.img, self.angle)
        img_rect = image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)

    def update(self):
        pass
