from settings import * 
from utils import * 
from sumo_bot import * 

class App():
    def __init__(self) -> None:
        pg.init()
        self.game_name = 'DUNGEON GAME'
        self.screen: pg.display = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen.fill((0, 0, 0))
        self.display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.delta_time: float = 0
        self.clock: pg.time = pg.time.Clock()

        self.sumo_bot = Sumo_Bot(app=self, img=get_image("assets/images/bot.png", [32, 32]), pos=vec2(300, 300))
        self.enemy = Enemy(app=self, img=get_image("assets/images/enemy.png", [32, 32]), pos=vec2(300, 150))
        self.sumo_bot.target = self.enemy
        self.timer = Timer(self)

        self.stage = {"radius": 200}
        self.timer.start()

    def render(self):
        self.display.fill(GRAY)

        x = 0
        assert x == 0, "x should equal 0"

        pg.draw.circle(self.display, BLACK, (CENTER.x, CENTER.y), self.stage["radius"])
        pg.draw.circle(self.display, WHITE, (CENTER.x, CENTER.y), self.stage["radius"], 4)

        self.sumo_bot.render(self.display)
        self.sumo_bot.update()

        self.enemy.render(self.display)

        self.timer.tick()
        print(self.timer.time)

        #for r in range(ROWS):
            #for c in range(COLS):
                #pg.draw.rect(self.display, BLUE, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        self.screen.blit(self.display, (0,0))
        pg.display.flip()
        pg.display.update()

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_w:
                    self.sumo_bot.move = True
                if e.key == pg.K_s:
                    self.sumo_bot.move_back = True
                if e.key == pg.K_a:
                    self.sumo_bot.turns[0] = True
                if e.key == pg.K_d:
                    self.sumo_bot.turns[1] = True
                
                if e.key == pg.K_t:
                    self.timer.stop()
                if e.key == pg.K_r:
                    self.timer.reset()
                if e.key == pg.K_y:
                    self.timer.start()
                
                    

            if e.type == pg.KEYUP:
                if e.key == pg.K_w:
                    self.sumo_bot.move = False
                if e.key == pg.K_s:
                    self.sumo_bot.move_back = False
                if e.key == pg.K_a:
                    self.sumo_bot.turns[0] = False
                if e.key == pg.K_d:
                    self.sumo_bot.turns[1] = False

    def update(self):
        self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps()}')
        self.delta_time = self.clock.tick(FPS)
        self.delta_time /= 1000

    def run(self):
        while True:
            self.render()
            self.check_inputs()
            self.update()


if __name__ == '__main__':

    state = 0
    assert state == 0, "whoudl be 0"

    app = App() 
    app.run()