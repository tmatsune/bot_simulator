from settings import * 
from ring_buffer import Ring_Buffer

 #------------------------------------------DRIVE SETTINGS----------------------------------------#
@dataclass
class Drive_Speeds:
    left: int
    right: int
    speed: int

class Drive_Dir(Enum):
    DRIVE_DIR_FORWARD = 0
    DRIVE_DIR_REVERSE = 1
    DRIVE_DIR_ROTATE_LEFT = 2
    DRIVE_DIR_ROTATE_RIGHT = 3
    DRIVE_DIR_ARCTURN_SHARP_LEFT = 4
    DRIVE_DIR_ARCTURN_SHARP_RIGHT = 5
    DRIVE_DIR_ARCTURN_MID_LEFT = 6
    DRIVE_DIR_ARCTURN_MID_RIGHT = 7
    DRIVE_DIR_ARCTURN_WIDE_LEFT = 8
    DRIVE_DIR_ARCTURN_WIDE_RIGHT = 9

class Drive_Speed(Enum):
    DRIVE_SPEED_SLOW = 0
    DRIVE_SPEED_MEDIUM = 1
    DRIVE_SPEED_FAST = 2
    DRIVE_SPEED_MAX = 3


drive_speeds = [
    [Drive_Speeds(0, 0, 1), Drive_Speeds(0, 0, 2), Drive_Speeds(0, 0, 3), Drive_Speeds(0, 0, 4)], #forward
    [Drive_Speeds(0, 0, -1), Drive_Speeds(0, 0, -2), Drive_Speeds(0, 0, -3), Drive_Speeds(0, 0, -4)], #reverse
    [Drive_Speeds(6, 0, 1), Drive_Speeds(6, 0, 2), Drive_Speeds(6, 0, 3), Drive_Speeds(6, 0, 4)], #left
    [Drive_Speeds(0, 6, 1), Drive_Speeds(0, 6, 2), Drive_Speeds(0, 6, 3), Drive_Speeds(0, 6, 4)], #right 
    [Drive_Speeds(14, 0, 1), Drive_Speeds(14, 0, 2), Drive_Speeds(14, 0, 3), Drive_Speeds(14, 0, 4)], #sharp left
    [Drive_Speeds(0, 14, 1), Drive_Speeds(0, 14, 2), Drive_Speeds(0, 14, 3), Drive_Speeds(0, 14, 4)], #sharp right 
    [Drive_Speeds(10, 0, 1), Drive_Speeds(10, 0, 2), Drive_Speeds(10, 0, 3), Drive_Speeds(10, 0, 4)], # mid left
    [Drive_Speeds(0, 10, 1), Drive_Speeds(0, 10, 2), Drive_Speeds(0, 10, 3), Drive_Speeds(0, 10, 4)], # mid right 
    [Drive_Speeds(4, 0, 1), Drive_Speeds(4, 0, 2), Drive_Speeds(4, 0, 3), Drive_Speeds(4, 0, 4)], #wide left
    [Drive_Speeds(0, 4, 1), Drive_Speeds(0, 4, 2), Drive_Speeds(0, 4, 3), Drive_Speeds(0, 4, 4)], #wide right 
]

# ------------------------------------------RETREAT SETTINGS----------------------------------------#


class Retreat_State_e(Enum):
    RETREAT_STATE_REVERSE = 0
    RETREAT_STATE_FORWARD = 1
    RETREAT_STATE_ROTATE_LEFT = 2
    RETREAT_STATE_ROTATE_RIGHT = 3
    RETREAT_STATE_ARCTURN_LEFT = 4
    RETREAT_STATE_ARCTURN_RIGHT = 5
    RETREAT_STATE_ALIGN_LEFT = 6
    RETREAT_STATE_ALIGN_RIGHT = 7

@dataclass
class Move:
    dir: Drive_Dir
    speed: Drive_Speed
    duration: float

@dataclass
class Retreat_Move:
    move_count: int
    moves: list[Move]


retreat_states = [
    Retreat_Move(1, [Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, .3]), # reverse
    Retreat_Move(1, [Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, .3]), # forward
    Retreat_Move(1, [Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_FAST, .15]), # retreat rotate left
    Retreat_Move(1, [Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_FAST, .15]), # retreat rotate right
    Retreat_Move(1, [Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, Drive_Speed.DRIVE_SPEED_MAX, .15]), # retreat arc rotate left
    Retreat_Move(1, [Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, .15]), # retreat arc rotate left
    Retreat_Move(3, 
                    [Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, .3,
                    Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, Drive_Speed.DRIVE_SPEED_MAX, .25,
                    Drive_Dir.DRIVE_DIR_ARCTURN_MID_LEFT, Drive_Speed.DRIVE_SPEED_MAX, .3],
                    ), # RETREAT_STATE_ALIGN_LEFT
    Retreat_Move(3, 
                    [Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, .3,
                    Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, .25,
                    Drive_Dir.DRIVE_DIR_ARCTURN_MID_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, .3],
                    ), # RETREAT_STATE_ALIGN_RIGHT
]


# --------------------------------------------LINE SETTINGS-------------------------------------------#

class Line_Pos:
    LINE_NONE = 0
    LINE_FRONT = 1
    LINE_BACK = 2
    LINE_LEFT = 3
    LINE_RIGHT = 4
    LINE_FRONT_LEFT = 5
    LINE_FRONT_RIGHT = 6
    LINE_BACK_LEFT = 7
    LINE_BACK_RIGHT = 8
    LINE_DIAGONAL_LEFT = 9
    LINE_DIAGONAL_RIGHT = 10

# --------------------------------------------IR_COMMAND SETTINGS-------------------------------------------#

class IR_Command(Enum):
    IR_CMD_0 = 0x98,
    IR_CMD_1 = 0xA2,
    IR_CMD_2 = 0x62,
    IR_CMD_3 = 0xE2,
    IR_CMD_4 = 0x22,
    IR_CMD_5 = 0x02,
    IR_CMD_6 = 0xC2,
    IR_CMD_7 = 0xE0,
    IR_CMD_8 = 0xA8,
    IR_CMD_9 = 0x90,
    IR_CMD_STAR = 0x68,
    IR_CMD_HASH = 0xB0,
    IR_CMD_UP = 0x18,
    IR_CMD_DOWN = 0x4A,
    IR_CMD_LEFT = 0x10,
    IR_CMD_RIGHT = 0x5A,
    IR_CMD_OK = 0x38,
    IR_CMD_NONE = 0xFF

# ---------------------------------------ENEMY---------------------------------------#


class Enemy_Pos(Enum):
    ENEMY_POS_NONE = 0
    ENEMY_POS_FRONT_LEFT = 1
    ENEMY_POS_FRONT = 2
    ENEMY_POS_FRONT_RIGHT = 3
    ENEMY_POS_LEFT = 4
    ENEMY_POS_RIGHT = 5
    ENEMY_POS_FRONT_AND_FRONT_LEFT = 6
    ENEMY_POS_FRONT_AND_FRONT_RIGHT = 7
    ENEMY_POS_FRONT_ALL = 8
    ENEMY_POS_IMPOSSIBLE = 9


class Enemy_Range(Enum):
    ENEMY_RANGE_NONE = 0
    ENEMY_RANGE_CLOSE = 1
    ENEMY_RANGE_MID = 2
    ENEMY_RANGE_FAR = 3


class Enemy():
    def __init__(self, app, img, pos) -> None:
        self.app = app
        self.img = img
        self.pos: vec2 = pos
        self.angle = 0
        self.position: Enemy_Pos
        self.range: Enemy_Range

    def enemy_init(self):
        pass

    def render(self, surf):
        image = pg.transform.rotate(self.img, self.angle)
        img_rect = image.get_rect(center=(self.pos.x, self.pos.y))
        surf.blit(image, img_rect)

    def update(self):
        pass

@dataclass
class Enemy_Struct():
    position: Enemy_Pos
    range: Enemy_Range

def enemy_at_left(enemy: Enemy):
    return enemy.position == Enemy_Pos.ENEMY_POS_LEFT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_LEFT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_LEFT
def enemy_at_right(enemy: Enemy):
    return enemy.position == Enemy_Pos.ENEMY_POS_RIGHT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_RIGHT \
        or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_AND_FRONT_RIGHT

def enemy_at_front(enemy: Enemy):
    return enemy.position == Enemy_Pos.ENEMY_POS_FRONT or enemy.position == Enemy_Pos.ENEMY_POS_FRONT_ALL

# --------------------------------------------RING_BUFFER_HISTORY-------------------------------------------#


@dataclass
class Input():
    enemy: Enemy
    line: Line_Pos

def input_equal(a: Input, b: Input):
    return a.enemy.range == b.enemy.range and a.enemy.position == b.enemy.position and a.line == b.line

def input_history_save(history: Ring_Buffer, input: Input):
    # skip if nothing is detected
    if input.enemy.position == Enemy_Pos.ENEMY_POS_NONE and input.line == Line_Pos.LINE_NONE:
        return 
    # skip if identical input
    if not history.ring_buffer_empty():
        prev_input = history.ring_buffer_peek()
        if input_equal(prev_input, input):
            return 
    history.ring_buffer_put(input)

def input_history_last_directed_enemy(history: Ring_Buffer) -> Enemy: 
    # loop through saves inputs too look for enemy detection
    for i in range(history.num_entries):
        input: Input = history.ring_buffer_get()
        if enemy_at_left(input.enemy) or enemy_at_right(input.enemy):
            return input.enemy
    return Enemy_Struct(Enemy_Pos.ENEMY_POS_NONE, Enemy_Range.ENEMY_RANGE_NONE)

