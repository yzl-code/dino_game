
import os
import random
import pygame
#from utils import QuitGame
from base import PygameBaseGame
from multiprocessing import Pool

#from modules.agent.agent import *
from modules.sprites.scene import *
from modules.sprites.obstacle import *
from modules.sprites.dinosaur import *
from modules.sprites.weapon import *
from modules.interfaces.endinterface import GameEndInterface
from modules.interfaces.startinterface import GameStartInterface
import sys
def QuitGame(use_pygame=True):
    if use_pygame: pygame.quit()
    sys.exit()
import numpy as np
import pickle
np.random.seed(42)
from gen_network import *

class Config():
  
    rootdir = os.path.split(os.path.abspath(__file__))[0]
  
    FPS = 60 
   
    TITLE = 'game'
    
    BACKGROUND_COLOR = (235, 235, 235)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    # 屏幕大小
    SCREENSIZE = (600, 300)
    # 游戏图片路径
    IMAGE_PATHS_DICT = {
        'cacti': [os.path.join(rootdir, 'resources/images/cacti-big.png'), os.path.join(rootdir, 'resources/images/cacti-small.png')],
        'cloud': os.path.join(rootdir, 'resources/images/cloud.png'),
        'dino': [os.path.join(rootdir, 'resources/images/dino.png'), os.path.join(rootdir, 'resources/images/dino_ducking.png')],
        'gameover': os.path.join(rootdir, 'resources/images/gameover.png'),
        'ground': os.path.join(rootdir, 'resources/images/ground.png'),
        'numbers': os.path.join(rootdir, 'resources/images/numbers.png'),
        'ptera': os.path.join(rootdir, 'resources/images/ptera.png'),
        'replay': os.path.join(rootdir, 'resources/images/replay.png'),
        'knife': os.path.join(rootdir, 'resources/images/knife.png'),
        'gun': os.path.join(rootdir, 'resources/images/gun.png')
        
    }
  
    SOUND_PATHS_DICT = {
        'die': os.path.join(rootdir, 'resources/audios/die.wav'),
        'jump': os.path.join(rootdir, 'resources/audios/jump.wav'),
        'point': os.path.join(rootdir, 'resources/audios/point.wav')
    }
    

    

class dino_game(PygameBaseGame):
    game_type = 'trexrush'
    def __init__(self, **kwargs):
        self.cfg = Config()
        super(dino_game, self).__init__(config=self.cfg, **kwargs)
        self.run_ai = False
        
    
    def run(self,run_ai =False, individual = None):
        self.run_ai = run_ai
     
        highest_score, flag = 0, True
        basic_score = 10000
        while flag:
           
            screen, resource_loader, cfg = self.screen, self.resource_loader, self.cfg
            
            if not self.run_ai:
                GameStartInterface(screen, resource_loader.sounds, cfg, resource_loader)
            
            score = 0
            score_board = Scoreboard(resource_loader.images['numbers'], position=(534, 15), bg_color=cfg.BACKGROUND_COLOR)
            highest_score = highest_score
            highest_score_board = Scoreboard(resource_loader.images['numbers'], position=(435, 15), bg_color=cfg.BACKGROUND_COLOR, is_highest=True)
            game_score_board = Scoreboard(resource_loader.images['numbers'], position=(336, 15), bg_color=cfg.BACKGROUND_COLOR)
            
            dino = Dinosaur(resource_loader.images['dino'])
            ground = Ground(resource_loader.images['ground'], position=(0, cfg.SCREENSIZE[1]/2))
            sub = SUB(resource_loader.images['knife'],resource_loader.images['gun'])
            
            obstacle_class = obstacle_manager(obstacle_class = [Cactus,Ptera],obstacle_image = [resource_loader.images['cacti'],resource_loader.images['ptera']],cfg = self.cfg)
            weapon_class = Weapon_manager(Weapon_class =[knife,gun],Weapon_image =[resource_loader.images['knife'],resource_loader.images['gun']] ,cfg = self.cfg)

            cloud_sprites_group = pygame.sprite.Group()
            
            
            add_obstacle_timer = 0
            score_timer = 0
         
            clock = pygame.time.Clock()
            while True:
                if not self.run_ai:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            QuitGame()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                                dino.jump(resource_loader.sounds)
                            elif event.key == pygame.K_DOWN:
                                dino.duck()
                            elif event.key == pygame.K_a:
                                weapon_class.use_weapon(dino,0)
                            elif event.key == pygame.K_d:
                                weapon_class.use_weapon(dino,1)
                                
                        elif event.type == pygame.KEYUP:
                            if event.key == pygame.K_DOWN:
                                dino.unduck()
                            elif event.key == pygame.K_a:
                                weapon_class.use_weapon(dino,3)  
                                
                else:
                    
                    for event in pygame.event.get():
                         if event.type == pygame.QUIT:
                            QuitGame()

            
                    near_obsticle = obstacle_class.get_nearest_obstcle()
                    near_weapon = weapon_class.get_nearest_weapon()
                    weapon_index = weapon_class.weapon_index
                    use_weapon_index = weapon_class.use_weapon_index
                   
                    
                    
                        
                    input = near_obsticle + near_weapon+ weapon_index+use_weapon_index 
                    inputs = np.array(input)
                    if inputs[0] != 1000:
                        action = self.decide_action(individual, inputs)
                        if action[0] > 0.55:
                            dino.jump(resource_loader.sounds)
                        elif action[1] >= 0.55:
                            dino.duck()
                        else:
                            dino.unduck()
                            
                        if action[2] > 0.55:
                            weapon_class.use_weapon(dino,0)
                        elif action[3] >= 0.55:
                             weapon_class.use_weapon(dino,1)
                        else:
                             weapon_class.use_weapon(dino,2)
        
                obstacle_class.add_obstacle()
                weapon_class.add_Weapon()
                    
                
                screen.fill(cfg.BACKGROUND_COLOR)
                
                if len(cloud_sprites_group) < 5 and random.randrange(0, 300) == 10:
                    cloud_sprites_group.add(Cloud(resource_loader.images['cloud'], position=(cfg.SCREENSIZE[0], random.randrange(30, 75))))
                
                obstacle_class.add_obstacle_timer += 1
                
               
                dino.update()
                ground.update()
                sub.update()
                
                obstacle_class.update()
                cloud_sprites_group.update()
                weapon_class.update()
                score_timer += 1
               
                if score_timer > (cfg.FPS//12):
                    score_timer = 0
                    score += 1
                    score = min(score, 99999)
                    if score > highest_score:
                        highest_score = score
                    if score % 100 == 0:
                        resource_loader.sounds['point'].play()
                    """ if score % 1000 == 0:
                        ground.speed -= 1
                        for item in cloud_sprites_group:
                            item.speed -= 1 """
                        
                weapon_get_score = weapon_class.dino_get_detect_collide(dino)          
                weapon_use_score = weapon_class.weapon_obstacle_collide(dino,obstacle_class)#障碍物与武器碰撞
                obsticle_collide_score = obstacle_class.collide(dino,resource_loader.sounds)
                
                basic_score = basic_score+10*weapon_get_score+50*weapon_use_score-200*obsticle_collide_score
                
                dino.draw(screen)
                ground.draw(screen)
                cloud_sprites_group.draw(screen)
                obstacle_class.draw(screen)
                weapon_class.draw(screen)
                weapon_class.weapon_update(screen)
                
                
                score_board.set(score)
                highest_score_board.set(highest_score)
                game_score_board.set(basic_score)
                
                score_board.draw(screen)
                highest_score_board.draw(screen)
                game_score_board.draw(screen)
                
                
                
                sub.draw(screen,weapon_class.weapon_index)
                # --更新屏幕
                pygame.display.update()
                clock.tick(cfg.FPS)
                # --游戏是否结束
                if dino.is_dead:
                    break
                score += 1
                if score > highest_score:
                    highest_score = score
                
                if score>=1500:
                    break
          
            if not self.run_ai:
                flag = GameEndInterface(screen, cfg, resource_loader)
            else:
                print(basic_score)
                return basic_score

    
    def get_inputs(self, dino, obstacle_class):
        
        inputs = np.zeros(5) 
        return inputs
    
    def decide_action(self, individual, inputs):
       
        return individual.predict(inputs)
    



if __name__ == '__main__':
    input_size = 12  
    hidden_layers = [12]  
    output_size = 4  
    """ ga = GA(dino_game(),population_size=100, mutation_rate=0.01, input_size=input_size, hidden_layers=hidden_layers, output_size=output_size)
    ga.run(generations=100)  遗传算法,运行遗传算法时注释掉后面的运行这部分就可以"""
    dino = dino_game() 
    dino.run() 
    #修改了游戏机制，目前的游戏机制：恐龙移动一定距离(1500)，躲避障碍物加分，拾取武器加分，用武器摧毁障碍物加分 ,恐龙碰撞障碍物减分
    #A键 D键使用武器  方向键up 跳跃 方向键down 趴下