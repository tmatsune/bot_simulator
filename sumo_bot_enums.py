from settings import * 

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
