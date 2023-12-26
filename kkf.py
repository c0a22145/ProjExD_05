import math
import os
import random
import sys
import time
from typing import Any
import pygame as pg

WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or 646 < obj.bottom:  # 縦方向のはみ出し判定　地面を元いる位置に設定
        tate = False
    return yoko, tate


class Koukaton:
    delta1 = {  # 1p側押下キーと移動量の辞書
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }
    delta2 = {  # 2p側押下キーと移動量の辞書
        pg.K_i: (0, -1),
        pg.K_k: (0, +1),
        pg.K_j: (-1, 0),
        pg.K_l: (+1, 0),
    }
    def __init__(self, player:int, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.hp = 100
        self.speed = 7.0
        self.player = player
        self.base_center = 0
        self.squat_flag = False
        self.jump_flag = False
        self.vel = 0
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 4.0)
        img1 = pg.transform.flip(img0, True, False)  # 右向きこうかとん
        img2 = pg.transform.scale(img0, (img0.get_width(), img0.get_height()/2))
        if self.player == 1:  # プレイヤーによって画像の向きを設定
            self.dire = (+1, 0)
        else:
            self.dire = (-1, 0)
        self.imgs = {
            (+1, 0): img0,  # 右
            (-1, 0): img1,  # 左
            (0, +1): img2,  # しゃがみ
            (0, -1): img0,  # ジャンプ
        }
        
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.base_center = self.rect.center
        
    def setHp(self, hp):
        self.hp = hp
    def getHp(self):
        return self.hp
    
    def setSpeed(self, speed):
        self.speed = speed
    def getSpeed(self):
        return self.speed
    
    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        grav = 0.05
        v0 = -20
        sum_mv = [0, 0]
        if self.player == 1:  # 1p(右)側の移動処理
            for k, mv in __class__.delta1.items():
                if key_lst[k]:
                    # self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                    sum_mv[0] += mv[0]
                    # if self.jump_flag == False:
                    sum_mv[1] += mv[1]
                    # else:
                    #     sum_mv[1] += v0 + grav * self.timer ** 2
        else:  # 2p(左)側の移動処理
            for k, mv in __class__.delta2.items():
                if key_lst[k]:
                    # self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                    sum_mv[0] += mv[0]
                    # if self.jump_flag == False:
                    sum_mv[1] += mv[1]
                    # else:
                    #     sum_mv[1] += v0 + grav * self.timer ** 2
            
        self.dire = tuple(sum_mv)         
        if (self.dire in self.imgs) or (self.dire in self.imgs):
                if self.image != self.imgs[self.dire]:
                    self.image = self.imgs[self.dire]

        if self.dire != (0, 0):
            if sum_mv == [0, 1] and self.squat_flag == False:  # しゃがんだ時
                x,y = self.rect.center  # 今のこうかとんのcenterを取得
                self.rect = self.image.get_rect()  # こうかとんのrectを上書き
                self.rect.center = (x, y+self.image.get_height()/2)  # こうかとんのcenterを上書き
                self.squat_flag = True
            if sum_mv[1] != 1 and self.squat_flag:  # 下方向以外の入力がされしゃがみ状態の時
                x,y = self.rect.center  # 今のこうかとんのcenterを取得
                self.rect = self.image.get_rect()  # こうかとんのrectを上書き
                self.rect.center = (x, y-self.image.get_height()/4)  # こうかとんのcenterを上書き
                self.squat_flag = False
        if sum_mv[1] == -1 and self.jump_flag == False:  # ジャンプしたとき
            self.jump_flag = True
            self.timer = 0
            sum_mv[1] = v0
        if self.jump_flag:
            self.timer += 1
            sum_mv[1] +=  grav * self.timer ** 2
            if self.rect.bottom > 646:
                self.timer = 0
                self.rect.centery = 500
                sum_mv[1] = 1
                self.jump_flag = False

        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):  #画面外に行かないように
            print(sum_mv[1], self.rect.centery)
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("大戦争スマッシュこうかとんファイターズ")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")

    play_1 = Koukaton(1, 2, (300, 500))
    play_2 = Koukaton(2, 2, (1300, 500))

    tmr = 0
    clock = pg.time.Clock()

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT: return

        screen.blit(bg_img, [0, 0])
        #メイン処理

        play_1.update(key_lst, screen)
        play_2.update(key_lst, screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)
            

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

    
