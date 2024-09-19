
import random
import pygame


'''仙人掌'''
class Cactus(pygame.sprite.Sprite):
    def __init__(self, images, position=(600, 147), sizes=[(40, 40), (40, 40)], **kwargs):
        pygame.sprite.Sprite.__init__(self)
        # 导入图片
        self.images = []
        image = images[0]
        for i in range(3):
            self.images.append(pygame.transform.scale(image.subsurface((i*101, 0), (101, 101)), sizes[0]))
        image = images[1]
        for i in range(3):
            self.images.append(pygame.transform.scale(image.subsurface((i*68, 0), (68, 70)), sizes[1]))
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.bottom = position
        self.mask = pygame.mask.from_surface(self.image)
        # 定义一些必要的变量
        self.speed = -10
    '''画到屏幕上'''
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    '''更新'''
    def update(self):
        self.rect = self.rect.move([self.speed, 0])
        if self.rect.right < 0:
            self.kill()
    def remove(self):
        self.kill()

'''飞龙'''
class Ptera(pygame.sprite.Sprite):
    def __init__(self, image, position, size=(46, 40), **kwargs):
        pygame.sprite.Sprite.__init__(self)
        # 导入图片
        self.images = []
        for i in range(2):
            self.images.append(pygame.transform.scale(image.subsurface((i*92, 0), (92, 81)), size))
        self.image_idx = 0
        self.image = self.images[self.image_idx]
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.centery = position
        self.mask = pygame.mask.from_surface(self.image)
        # 定义一些必要的变量
        self.speed = -10
        self.refresh_rate = 10
        self.refresh_counter = 0
    '''画到屏幕上'''
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    '''更新'''
    def update(self):
        if self.refresh_counter % self.refresh_rate == 0:
            self.refresh_counter = 0
            self.image_idx = (self.image_idx + 1) % len(self.images)
            self.loadImage()
        self.rect = self.rect.move([self.speed, 0])
        if self.rect.right < 0:
            self.kill()
        self.refresh_counter += 1
    '''载入当前状态的图片'''
    def loadImage(self):
        self.image = self.images[self.image_idx]
        rect = self.image.get_rect()
        rect.left, rect.top = self.rect.left, self.rect.top
        self.rect = rect
        self.mask = pygame.mask.from_surface(self.image)
    def remove(self):
        self.kill()    
        
class obstacle_manager():
    def __init__(self, obstacle_class,obstacle_image,cfg):
        self.cfg = cfg
        self.obsticle = obstacle_class
        self.obsticle_image = obstacle_image
        self.obsticle_sprites_group = []
        for i in range(len(self.obsticle)):
            self.obsticle_sprites_group.append(pygame.sprite.Group())
        self.add_obstacle_timer = 0
    def add_obstacle(self):
        if self.add_obstacle_timer > random.randrange(50, 150):
                self.add_obstacle_timer = 0
                random_value = random.randrange(0, 10)
                if random_value >= 5 and random_value <= 7:
                    self.obsticle_sprites_group[0].add(self.obsticle[0](self.obsticle_image[0]))
                else:
                    position_ys = [self.cfg.SCREENSIZE[1]*0.82/2, self.cfg.SCREENSIZE[1]*0.75/2, self.cfg.SCREENSIZE[1]*0.60/2, self.cfg.SCREENSIZE[1]*0.20/2]
                    self.obsticle_sprites_group[0].add(self.obsticle[1](self.obsticle_image[1], position=(600, random.choice(position_ys)))) 
    
    def update(self):
        for i in range(len(self.obsticle_sprites_group)):
            for sprites in self.obsticle_sprites_group[i]:
                sprites.update()
        
    def draw(self,screen):
        for i in range(len(self.obsticle_sprites_group)):
            for sprites in self.obsticle_sprites_group[i]:
                sprites.draw(screen)
    
    def collide(self,dino,sounds):
        obs_coll = 0
        for i in range(len(self.obsticle_sprites_group)):
            for item in self.obsticle_sprites_group[i]:
                if pygame.sprite.collide_mask(dino, item):
                    #dino.die(sounds)
                    obs_coll += 1
                    item.remove() 
        return obs_coll
    def get_nearest_obstcle(self):
        nearest_obstacle = None
        for i in range(len(self.obsticle_sprites_group)):
            if len(self.obsticle_sprites_group[i])==0:
                continue
            for item in self.obsticle_sprites_group[i]:
                if item.rect.left < 84:
                    continue
                if nearest_obstacle is None:
                    nearest_obstacle = item
                else:
                    if item.rect.left < nearest_obstacle.rect.left: 
                            nearest_obstacle = item
        if nearest_obstacle == None:
            return   [1000,1000,0,0]
        else:
            return   [nearest_obstacle.rect.left-84, nearest_obstacle.rect.bottom, nearest_obstacle.rect.width, nearest_obstacle.rect.height]
    