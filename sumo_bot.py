from settings import * 
from sumo_bot_enums import * 
from ring_buffer import *

class Timer():
    def __init__(self, app) -> None:
        self.app = app
        self.time: int = 0
        self.on = False
        self.timeout: int = 0
    def tick(self):  
        if self.on: 
            self.time += self.app.delta_time
        if self.time >= self.timeout:
            return True
        return False
    
    def reset(self): self.time = 0
    def start(self, timeout): 
        self.timeout = timeout
        self.on = True
    def stop(self): self.on = False

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
        self.drive_setting: Drive_Speeds = drive_speeds[2][2]
        self.target: Enemy_Struct
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
        
    def check_circle_collision(self, circle1, circle2):
        dist = math.sqrt( math.pow(circle1[0] - circle2[0], 2) + math.pow(circle1[1] - circle2[1], 2) )
        if dist < circle1[2] + circle2[2]:
             return True
        return False

    def line_sensor(self):
        self.line_sensors = [False, False, False, False]
        sensor_detected = False
        count = 0
        for offset in [45, 135, 225, 315]:
            x_speed = math.cos(math.radians(self.angle + offset)) * 26
            y_speed = math.sin(math.radians(self.angle + offset)) * 26
            front = vec2(self.pos.x + x_speed, self.pos.y + y_speed)
            pg.draw.circle(self.app.display, RED, (front.x, front.y), 4)
            if not self.check_circle_collision([front.x, front.y, 4], [CENTER.x, CENTER.y, 200]):
                self.move = False
                self.line_detected_bool = True
                sensor_detected = True
                self.line_sensors[count] = True
                count += 1


        if sensor_detected: self.line_detected_bool = False
    
    def line_detected(self): return self.line_detected_bool
        
    def enemy_in_front(self): return self.enemy_in_front_bool

    def move_forward(self):
        x_speed = math.cos( math.radians( self.angle  ) ) 
        y_speed = math.sin( math.radians( self.angle  ) ) 
        speed = vec2(x_speed, y_speed) * self.drive_setting.speed * 2
        self.pos += speed

    def move_backward(self):
        x_speed = math.cos( math.radians( 180 + self.angle ) ) 
        y_speed = math.sin( math.radians( 180 + self.angle ) ) 
        speed = vec2(x_speed, y_speed) * self.drive_setting.speed * 2
        self.pos += speed

    def turn_left(self):
         self.angle -= self.drive_setting.left

    def turn_right(self):
         self.angle += self.drive_setting.right

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
    
    def drive_set(self, direction: Drive_Dir, speed: Drive_Speed):
        drive_setting = drive_speeds[direction][speed]
        self.drive_setting = drive_setting

    def drive_stop(self):
        pass
    

#---------------------------------------------STATE MACHINE---------------------------------------------#

# ALL STATES
class State_e(Enum):
	STATE_WAIT = 0
	STATE_SEARCH = 1
	STATE_ATTACK = 2
	STATE_RETREAT = 3
	STATE_MANUAL = 4
        
# ALL EVENTS THAT CAN HAPPEN
class StateEvent(Enum):
	STATE_EVENT_TIMEOUT = 0
	STATE_EVENT_LINE = 1
	STATE_EVENT_ENEMY = 2
	STATE_EVENT_FINISHED = 3
	STATE_EVENT_COMMAND = 4
	STATE_EVENT_NONE = 5
        
# -----------------------------------SCENE_TRANSITION----------------------------------#
class Scene_Transition():
     def __init__(self, from_state, state_event, to_state) -> None:
        self.from_state: State_e = from_state # state where transition comes from 
        self.event_state: StateEvent = state_event # event causing transition
        self.to_state: State_e = to_state # state transition going to 

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


# ----------------------------------------STATE MACHINE--------------------------------------#
'''
    state machine will hold overall state machine logic 
    hold difference transitions
    define transitions
    handle inputs, translate into events to cause transition

    NOTE: 
    Internal Event: events that can be posted within states themselves
    E.G: 
        if in retreat state, there will be point where all retreat moves have been executed, 
        when this happend it will only be known within retreat state
        need way to post event from withing state themselves
'''

'''
/* A state machine implemented as a set of enums and functions. The states are linked through
 * transitions, which are triggered by events.
 *
 * Flow:
 *    1. Process input
 *        - Check input (e.g. sensors, timer, internal event...)
 *        - Return event
 *    2. Process event
 *        - State/Change state
 *        - Run state function
 *    3. Repeat
 *
 * The flow is continuous (never blocks), which avoids the need for event synchronization
 * mechanisms, since the input can be processed repeatedly at the beginning of each iteration
 * instead. No input is still treated as an event (STATE_EVENT_NONE), but treated as a NOOP
 * when processed. Of course, this means that the code inside the state machine can't block.
 */
'''

class StateMachine():  # State machine logic
    def __init__(self, user) -> None:
        self.user: Sumo_Bot = user
        self.state_e: State_e = State_e.STATE_WAIT  # CURRENT STATE
        self.state_machine_common_data: StateMachineCommonData  # COMMON USED DATA
        # hold data for individual states
        self.wait_state: Wait_State
        self.search_state: Search_State
        self.attack_state: Attack_State
        self.retreat_state: Retreat_State
        self.manual_state: Manual_State
        self.internal_event: StateEvent
        
        self.input_history: Ring_Buffer
    
    def state_machine_init(self):
        self.state_e = State_e.STATE_WAIT
        self.state_machine_common_data.state_machine_data = self
        self.state_machine_common_data.enemy.position = Enemy_Pos.ENEMY_POS_NONE
        self.state_machine_common_data.enemy.range = Enemy_Range.ENEMY_RANGE_NONE
        self.state_machine_common_data.line = Line_Pos.LINE_NONE

        # Set common data for all states 
        self.wait_state.state_machine_common_data = self.state_machine_common_data
        self.search_state.state_machine_common_data = self.state_machine_common_data
        self.attack_state.state_machine_common_data = self.state_machine_common_data
        self.retreat_state.state_machine_common_data = self.state_machine_common_data
        self.manual_state.state_machine_common_data = self.state_machine_common_data

        input_history = Ring_Buffer()
        input_history.ring_buffer_init(6)
        self.input_history = input_history
        self.state_machine_common_data.input_history = self.input_history

        # init 3 states
        self.search_state.search_init()
        self.attack_state.attack_init()
        self.retreat_state.retreat_init()

    def state_machine_run(self):

        next_event: StateEvent = self.process_input()
        self.process_event(next_event=next_event)

    # functinon that will cause transition to another state if particular event has happened
    # will run in the state_machine_run function, take input to find next state
    def process_input(self):
        # TODO save data to history
        # TODO get_input(line, enemy, CMD
        '''
        if remote_command:
            return STATE_EVENT_COMMAND
        elif internal remote:
            return internal event
        elif timeout:
            return STATE_EVENT_TIMEOUT
        elif line detected:
            return STATE_EVENT_LINE
        elif enmy detected:
            return STATE_EVENT_ENEMY
        '''
        return StateEvent.STATE_EVENT_NONE

    # take event, go through state transition table and find corresponding transition
    def process_event(self, next_event: StateEvent):
        for i in range(len(state_transitions)):
            if self.state_e == state_transitions[i].from_state and next_event == state_transitions[i].event_state:
                self.state_enter(state_transitions[i].from_state, next_event, state_transitions[i].to_state)
                return 

    # actually enter state
    def state_enter(self, from_state: State_e, event: StateEvent, to_state: State_e):
        if from_state != to_state:
            self.state_machine_common_data.timer.reset()
            self.state_e = to_state

        if to_state == State_e.STATE_WAIT:
            self.state_wait_enter(self.wait_state, from_state, event)
        elif to_state == State_e.STATE_ATTACK:
            self.state_attack_enter(self.attack_state, from_state, event)
        elif to_state == State_e.STATE_RETREAT:
            self.state_retreat_enter(self.retreat_state, from_state, event)
        elif to_state == State_e.STATE_SEARCH:
            self.state_search_enter(self.search_state, from_state, event)
        elif to_state == State_e.STATE_MANUAL:
            self.state_manual_enter(self.manual_state, from_state, event)
        else:
            return 

    def state_wait_enter(self, wait_state, from_state: State_e, event: StateEvent ):
        assert from_state == State_e.STATE_WAIT, "should only come wait state"
        pass
    def state_search_enter(self, search_state, from_state: State_e, event: StateEvent):
        pass
    def state_attack_enter(self, attack_state, from_state: State_e, event: StateEvent):
        pass
    def state_retreat_enter(self, retreat_state, from_state: State_e, event: StateEvent):
        pass
    def state_manual_enter(self, manual_state, from_state: State_e, event: StateEvent):
        pass

    def has_internal_event(self): # check if current state has internal state or is in internal state
        return self.internal_event != StateEvent.STATE_EVENT_NONE
    
    def take_internal_event(self): # set internal event to NONE and return prev internal state
        event: StateEvent = self.internal_event
        self.internal_event = StateEvent.STATE_EVENT_NONE
        return event

    def post_internal_event(self, event: StateEvent): # set internal state to state machine
        self.internal_event = event


# holds everything that needs to be accessable within all individual states
class StateMachineCommonData():
    def __init__(self) -> None:
        self.state_machine_data: StateMachine # state machine
        self.enemy: Enemy_Struct # struct
        self.timer: Timer # struct 
        self.line: Line_Pos # enum
        self.input_history: Ring_Buffer

# ---------------------------------SEARCH STATE----------------------------------#
# Function: Drive around until enemy is found or line is detected
class Search_State_e(Enum): #internal states for search state
    SEARCH_STATE_ROTATE = 1
    SEARCH_STATE_FORWARD = 2

class Search_State():
     def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e
        self.internal_state: Search_State_e
        self.rotate_timeout = 1
        self.forward_timeout = 3

     def search_init(self):
         self.state_e = Search_State_e.SEARCH_STATE_ROTATE
     
     # swtich statement to 
     def search_enter(self, from_state: State_e, event: StateEvent):

        if from_state == State_e.STATE_WAIT:
            assert event == StateEvent.STATE_EVENT_COMMAND, "only event should be remote command"
            self.run_search()
        elif from_state == State_e.STATE_RETREAT or from_state == State_e.STATE_ATTACK:
            # CHECK EVENT TRIGGEREING TRANSITION & COMING FROM STATE
            if event == StateEvent.STATE_EVENT_NONE:
                assert from_state == State_e.STATE_ATTACK, "should only come from attack state"
                self.run_search()
            elif event == StateEvent.STATE_EVENT_TIMEOUT:
                pass
            elif event == StateEvent.STATE_EVENT_COMMAND:
                pass
            elif event == StateEvent.STATE_EVENT_FINISHED:
                assert from_state == State_e.STATE_RETREAT, "should only finish if came retreat state has finished"
                if self.internal_state == Search_State_e.SEARCH_STATE_FORWARD: # prevent state moving back and forth
                    self.internal_state = Search_State_e.SEARCH_STATE_ROTATE 
                self.run_search()
            elif event == StateEvent.STATE_EVENT_ENEMY:
                assert 0, "should never enter this state if event is enemy"
            elif event == StateEvent.STATE_EVENT_LINE:
                assert 0, "should never enter this state if event is NONE"

        elif from_state == State_e.STATE_SEARCH:
            if event == StateEvent.STATE_EVENT_NONE:
                # dont do antything, to keep state machine itertaing
                pass
            elif event == StateEvent.STATE_EVENT_TIMEOUT: # only other possible event, switch between internal states
                if self.internal_state == Search_State_e.SEARCH_STATE_FORWARD:
                    self.internal_state = Search_State_e.SEARCH_STATE_ROTATE    
                elif self.internal_state == Search_State_e.SEARCH_STATE_ROTATE:
                    self.internal_state = Search_State_e.SEARCH_STATE_FORWARD
                self.run_search()
            else:  # REST OF THESE STATES SHOULD NEVER HAPPEN
                assert 0, self.EVENT_ERROR(event, from_state)

        elif from_state == State_e.STATE_MANUAL:
            pass

     def run_search(self):
        if self.internal_state == Search_State_e.SEARCH_STATE_FORWARD:
            self.state_machine_common_data.timer.start(self.forward_timeout)
            self.state_machine_common_data.state_machine_data.user.drive_set()

        elif self.internal_state == Search_State_e.SEARCH_STATE_ROTATE:
            self.state_machine_common_data.timer.start(self.rotate_timeout)


     def EVENT_ERROR(self, event: StateEvent, from_state: State_e):
        return f'event: {event} should not happen from {from_state}'

# ---------------------------------ATTACK STATE----------------------------------#

#function : drive toward detected enemy
class Attack_State_e(Enum): # three internal states
    ATTACK_STATE_FORWARD = 0
    ATTACK_STATE_LEFT = 1
    ATTACK_STATE_RIGHT = 2
    
class Attack_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e
        self.attack_state_e: Attack_State_e

        self.attack_timeout = 5

    def attack_init(self):
        pass

    def attack_enter(self, from_state: State_e, event: StateEvent):
        prev_attack: Attack_State_e = self.attack_state_e
        self.attack_state_e = self.next_attack_state()

        if from_state == State_e.STATE_SEARCH:
            if event == StateEvent.STATE_EVENT_ENEMY: # only way to get attack from search is if enemy detected
                self.run_attack()
            else: # no other events shoould from search
                assert 0, EVENT_ERROR(event, from_state, State_e.STATE_ATTACK)

        elif from_state == State_e.STATE_ATTACK:
            if event == StateEvent.STATE_EVENT_ENEMY:
                if prev_attack != self.attack_state_e:
                    self.run_attack()
            elif event == StateEvent.STATE_EVENT_TIMEOUT:
                assert 0, "might change strategy"
            else:  # no other events shoould from attack
                assert 0, EVENT_ERROR(event, from_state, State_e.STATE_ATTACK)

        elif from_state == State_e.STATE_WAIT:
            assert 0, f'{State_e.STATE_ATTACK}, Should not come form wait state, go search first'
        elif from_state == State_e.STATE_RETREAT:
            assert 0, f'{State_e.STATE_ATTACK}, Should not come form retreat state, go search first'
        elif from_state == State_e.STATE_MANUAL:
            assert 0, f'{State_e.STATE_ATTACK}, Should not come form manual state, go search first'

    def next_attack_state(self) -> Attack_State_e:
        if self.enemy_at_front(self.state_machine_common_data.enemy):
            return Attack_State_e.ATTACK_STATE_FORWARD
        elif self.enemy_at_left(self.state_machine_common_data.enemy):
            return Attack_State_e.ATTACK_STATE_LEFT
        elif self.enemy_at_right(self.state_machine_common_data.enemy):
            return Attack_State_e.ATTACK_STATE_RIGHT
        else:
            assert 0, "enemy should be in view"

    def run_attack(self):
        if self.attack_state_e == Attack_State_e.ATTACK_STATE_FORWARD:
            self.state_machine_common_data.state_machine_data.user.drive_set(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_FAST)
        elif self.attack_state_e == Attack_State_e.ATTACK_STATE_LEFT:
            self.state_machine_common_data.state_machine_data.user.drive_set(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_LEFT, Drive_Speed.DRIVE_SPEED_FAST)
        elif self.attack_state_e == Attack_State_e.ATTACK_STATE_RIGHT:
            self.state_machine_common_data.state_machine_data.user.drive_set(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_RIGHT, Drive_Speed.DRIVE_SPEED_FAST)
        self.state_machine_common_data.timer.start(self.attack_timeout)

    def enemy_at_front(self, enemy):
        # TODO check if enemy in front
        pass
    def enemy_at_left(self, enemy):
        # TODO check if enemy on left
        pass
    def enemy_at_right(self, enemy):
        # TODO check if enemy on right
        pass

# ----------------------------------RETREAT STATE------------------------------------#


class Retreat_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e
        self.internal_state: Retreat_State_e
        self.move_idx: int = 0
        self.retreat_moves = [Retreat_State_e.RETREAT_STATE_REVERSE]

    def retreat_init(self):
        self.internal_state = Retreat_State_e.RETREAT_STATE_REVERSE
        self.move_idx = 0

    def retreat_enter(self, from_state: State_e, event: StateEvent):
        if from_state == State_e.STATE_SEARCH or from_state == State_e.STATE_ATTACK: 
            if event == StateEvent.STATE_EVENT_LINE: # only possible way to come from attack state is if line is detected
                self.run_retreat()
            else:
                assert 0, EVENT_ERROR(event, from_state, State_e.STATE_RETREAT)

        elif from_state == State_e.STATE_RETREAT:
            if event == StateEvent.STATE_EVENT_LINE: # line has already been detected, start over
                self.run_retreat()
            elif event == StateEvent.STATE_EVENT_TIMEOUT: # done with curernt move, incrememnt to next move
                self.move_idx += 1
                if self.retreat_state_done(): # leave current internal state
                    # posted state finished since retreat state is the only state that know done with current state
                    self.state_machine_common_data.state_machine_data.post_internal_event(StateEvent.STATE_EVENT_FINISHED)
                else:
                    self.start_retreat_move()
            elif event == StateEvent.STATE_EVENT_NONE:
                pass
            elif event == StateEvent.STATE_EVENT_ENEMY: # ignore enemy when retreating
                pass
            else:
                assert 0, EVENT_ERROR(event, from_state, State_e.STATE_RETREAT)

        elif from_state == State_e.STATE_WAIT:
            assert 0,STATE_ERROR(from_state, State_e.STATE_RETREAT)
        elif from_state == State_e.STATE_MANUAL:
            assert 0, STATE_ERROR(from_state, State_e.STATE_RETREAT)

    def run_retreat(self):
        self.move_idx = 0
        self.internal_state = self.next_retreat_state()
        self.start_retreat_move()

    def next_retreat_state(self): # decide which retreat state to choose based on where line was detected
        line_pos = self.state_machine_common_data.line
        if line_pos == Line_Pos.LINE_FRONT_LEFT:
            # TODO set retreat state based on input
            pass 
        elif line_pos == Line_Pos.LINE_FRONT_RIGHT:
            # TODO set retreat state based on input
            pass
        elif line_pos == Line_Pos.LINE_BACK_LEFT:
            # TODO set retreat state based on input
            pass
        elif line_pos == Line_Pos.LINE_BACK_RIGHT:
            # TODO set retreat state based on input
            pass
        elif line_pos == Line_Pos.LINE_FRONT:
            # TODO set retreat state based on input
            pass
        elif line_pos == Line_Pos.LINE_BACK:
            return Retreat_State_e.RETREAT_STATE_FORWARD
        
        elif line_pos == Line_Pos.LINE_LEFT:
            return Retreat_State_e.RETREAT_STATE_ARCTURN_RIGHT
        elif line_pos == Line_Pos.LINE_RIGHT:
            return Retreat_State_e.RETREAT_STATE_ARCTURN_LEFT
        elif line_pos == Line_Pos.LINE_DIAGONAL_LEFT:
            assert 0, "can happen, no implementaion yet"
        elif line_pos == Line_Pos.LINE_DIAGONAL_RIGHT:
            assert 0, "can happen, no implementaion yet"
        elif line_pos == Line_Pos.LINE_NONE:
            assert 0, "should never be called"
        return Retreat_State_e.RETREAT_STATE_REVERSE

    def start_retreat_move(self):
        assert self.move_idx < len(self.retreat_moves), "moves index has to be less than length of retreat moves list"
        move: Move = retreat_states[self.internal_state].moves[self.move_idx]
        self.state_machine_common_data.timer.start(move.duration)
        self.state_machine_common_data.state_machine_data.user.drive_set(move.dir, move.speed)

    def retreat_state_done(self):
        return self.move_idx == len(self.retreat_moves)

# ----------------------------------WAIT STATE-----------------------------------#


class Wait_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e


# ------------------------------------MANUAL STATE------------------------------------#


class Manual_State():
    def __init__(self) -> None:
        self.state_machine_common_data: StateMachineCommonData
        self.state_e: State_e = State_e.STATE_MANUAL

    def manual_enter(self, from_state: State_e, event: StateEvent):
        if event != StateEvent.STATE_EVENT_COMMAND:
            return 

# ------------------------------------------------------------------------------------#


#-------------------------------------COMMON FUNCS-------------------------------------#

def EVENT_ERROR(event: StateEvent, from_state: State_e, current_state: State_e):
    return f'event: {event} should not happen from {from_state}, goint into {current_state}'

def STATE_ERROR(from_state: State_e, to_state: State_e):
    return f'going into {to_state}, should not come from {from_state}'


# ------------------------------------------------------------------------------------#
'''
        if event == StateEvent.STATE_EVENT_NONE:
            pass
        elif event == StateEvent.STATE_EVENT_ENEMY:
            pass
        elif event == StateEvent.STATE_EVENT_LINE:
            pass
        elif event == StateEvent.STATE_EVENT_FINISHED:
            pass
        elif event == StateEvent.STATE_EVENT_TIMEOUT:
            pass
        elif event == StateEvent.STATE_EVENT_COMMAND:
            pass
                

        if from_state == State_e.STATE_WAIT:
            pass
        elif from_state == State_e.STATE_ATTACK:
            pass
        elif from_state == State_e.STATE_RETREAT:
            pass
        elif from_state == State_e.STATE_SEARCH:
            pass
        elif from_state == State_e.STATE_MANUAL:
            pass
            
'''