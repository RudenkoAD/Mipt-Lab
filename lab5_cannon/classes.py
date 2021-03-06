import math
from random import randint
import pygame
from constants import *


"""Menu Classes"""
class Button(pygame.sprite.Sprite):
    def __init__(self, text, rect):
        super().__init__()
        self.rect = rect
        self.image = pygame.transform.scale(pygame.image.load('resources/button.png').convert(), self.rect.size)
        self.hover_image = pygame.transform.scale(pygame.image.load('resources/button_hover.png').convert(), self.rect.size)
        self.image.set_colorkey(BLACK)
        self.hover_image.set_colorkey(BLACK)
        self.text = CLF.render(text, 0, GREY)
        self.image.blit(self.text, self.text.get_rect(center=(self.rect.size[0]/2, self.rect.size[1]/2)))
        self.hover_image.blit(self.text, self.text.get_rect(center=(self.rect.size[0]/2, self.rect.size[1]/2)))

    def get_click(self, event):
        return self.rect.collidepoint(event.pos[0], event.pos[1])

    def draw(self, screen):

        if self.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)


"""Game Classes"""
class Ball(pygame.sprite.Sprite):
    def __init__(self, x=20, y=450):
        """
        Конструктор класса ball
        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        r = 10
        self.r = 10
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('resources/ball.png').convert(), (2*r, 2*r))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.mask = pygame.mask.from_surface(self.image)
        self.vx = 0
        self.vy = 0
        self.live = 30

    def update(self, screen, tiles, *args):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        Метод высчитывает столкновения с препятствиями tiles и отражает мяч от них, удаляя wood_tiles
        #TODO вынести обсчёт разрушения клеток в отдельное место
        """

        self.rect = self.rect.move(self.vx, 0)

        tiles_hit_list = pygame.sprite.spritecollide(self, tiles, dokill=False)
        if tiles_hit_list:
            for tile in tiles_hit_list:
                if tile.destructible:
                    tile.kill()
                if self.vx >= 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
            self.vx = -self.vx

        self.rect = self.rect.move(0, int(self.vy))

        tiles_hit_list = pygame.sprite.spritecollide(self, tiles, dokill=False)
        if tiles_hit_list:
            for tile in tiles_hit_list:
                if isinstance(tile, WoodTile):
                    tile.kill()
                if self.vy >= 0:
                    self.rect.bottom = tile.rect.top
                else:
                    self.rect.top = tile.rect.bottom
            self.vy = -self.vy*BOUNCE_COEFFICENT

        self.vy += 0.5
        self.vx = self.vx * FRICTION_COEFFICIENT

    def draw(self, screen):
        """рисовка мяча на экране"""
        screen.blit(self.image, self.rect)

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с объектом target.
        предполагается что оба объекта - круги.

        Args:
            obj: Обьект, с которым проверяется столкновение, обязан иметь аттрибут rect
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if math.hypot(self.rect.center[0] - obj.rect.center[0], self.rect.center[1] - obj.rect.center[1]) <= self.r + obj.r:
            return True
        return False


class Gun:
    def __init__(self):
        """
        конструктор пушки игрока
        f2_power - сила заряда пушки, от 10 до 100
        f2_on - заряжается ли пушка
        self.an - угол наклона пистолета от прямой x = const против часовой стрелки
        self.color - цвет пистолета, #TODO заменить на картинку
        self.x, self.y - координаты по x b y #TODO заменить на rect
        """
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = 20
        self.y = 450

    def fire2_start(self):
        """
        начало зарядки мяча на выстрел
        """
        self.f2_on = 1

    def fire2_end(self, event):
        """
        Выстрел мячом.
        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        self.an = math.atan2((-event.pos[1]+self.y), (event.pos[0]-self.x))
        self.update()
        new_ball = Ball(round(self.x + self.f2_power * math.cos(self.an)), round(self.y - self.f2_power * math.sin(self.an)))
        new_ball.vx = self.f2_power * math.cos(self.an)*BALL_SPEED_COEFFICENT
        new_ball.vy = - self.f2_power * math.sin(self.an)*BALL_SPEED_COEFFICENT
        self.f2_on = 0
        self.color = GREY
        return new_ball

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши.
        меняет цвет и угол наклона
        """
        self.an = math.atan2((-event.pos[1]+self.y), (event.pos[0]-self.x))
        self.power_up(event)
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def power_up(self, event):
        """
        увеличивает силу заряда, меняет цвет на красный при зарядке
        вызывается собственной функцией targetting
        """
        self.f2_power = 20 * (math.exp(math.hypot(self.x - event.pos[0], self.y - event.pos[1])/500)-1)

    def update(self):
        """обновляет картину, угол и силу пушки"""
        self.image = pygame.surface.Surface((self.f2_power, 5))
        self.image.fill(self.color)
        pygame.draw.rect(self.image, BLACK, (0, 0, self.f2_power, 5), 1)
        self.rot_image = pygame.transform.rotate(self.image, math.degrees(self.an))
        self.rot_image.set_colorkey(BLACK)
        if self.an > 0:
            self.rot_rect = self.rot_image.get_rect(bottomleft=(self.x, self.y))
        else:
            self.rot_rect = self.rot_image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.rot_image, self.rot_rect)


class Target(pygame.sprite.Sprite):
    def __init__(self, r, pos):
        """базовый конструктор классса target"""
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.r = r
        self.image = pygame.transform.scale(pygame.image.load('resources/target.png').convert(), (2 * r, 2 * r))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        pass

    def draw(self, screen):
        """вывод себя на экран"""
        screen.blit(self.image, self.rect)

    def hit(self):
        """Попадание шарика в цель."""
        pass


class CrawlTarget(Target):
    def __init__(self, r, pos):
        super().__init__(r, pos)
        self.vx = 0
        self.vy = 0

    def update(self, screen, *args):
        self.rect = self.rect.move(self.vx, self.vy)
        self.vx += randint(-1, 1)
        self.vy += randint(-1, 1)

        if self.rect.right >= screen.get_width():
            self.rect.right = screen.get_width()
            self.vx = -self.vx
        if self.rect.bottom >= screen.get_height():
            self.rect.bottom = screen.get_height()
            self.vy = -self.vy
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = -self.vy
        if self.rect.left <= 0:
            self.rect.left = 0
            self.vx = -self.vx

        self.vx = self.vx * CRAWLTARGET_FRICTION
        self.vy = self.vy * CRAWLTARGET_FRICTION


class PathTarget(Target):
    def __init__(self, r, pos1, pos2):
        super().__init__(r, pos1)
        self.pathtime = 2
        self.time = 0
        self.pos1 = pos1
        self.pos2 = pos2

    def update(self, *args):
        self.time += 1/FPS
        self.rect.center = (
            self.pos2[0]*self.time/self.pathtime + self.pos1[0]*(self.pathtime - self.time)/self.pathtime,
            self.pos2[1]*self.time/self.pathtime + self.pos1[1]*(self.pathtime - self.time)/self.pathtime
        )
        if self.time >= self.pathtime:
            self.rect.center = self.pos2
            self.time = 0
            self.pos1, self.pos2 = self.pos2, self.pos1

    def draw(self, screen):
        """вывод себя на экран"""
        pygame.draw.line(screen, BLACK, self.pos1, self.pos2, 2)
        screen.blit(self.image, self.rect)


class StationaryTarget(Target):
    def __init__(self, r, pos):
        super().__init__(r, pos)


class Tile(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def draw(self, screen, *args):
        screen.blit(self.image, self.rect)


class WoodTile(Tile):
    '''a destructible wood tile'''
    def __init__(self, pos):
        super().__init__()
        self.destructible = True
        self.image = pygame.transform.scale(pygame.image.load('resources/box.png').convert(), (40, 40))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect(center=pos)


class IronTile(Tile):
    '''an indestructible iron tile'''
    def __init__(self, pos):
        super().__init__()
        self.destructible = False
        self.image = pygame.transform.scale(pygame.image.load('resources/ironbox.png').convert(), (40, 40))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect(center=pos)
