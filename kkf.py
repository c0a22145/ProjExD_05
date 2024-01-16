import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

def draw_start_screen(screen, font, text, color):
        text_render = font.render(text, True, color)
        text_rect = text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_render, text_rect)


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


class Koukaton(pg.sprite.Sprite):
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
        super().__init__()
        self.hp = 100
        self.speed = 7.0
        self.damage = 0
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
    
    def setDamage(self, damege):
        self.damage = damege
    def getDamage(self):
        return self.damage
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
            self.rect.move_ip(-self.speed*sum_mv[0], (646-self.rect.bottom+self.speed*sum_mv[1]))
        screen.blit(self.image, self.rect)

        #hpの減算処理
        self.hp -= self.damage

class Status(pg.sprite.Sprite):
    """
    体力、必殺技のゲージ表示
    引数: 体力バーのx座標, 体力バーの減る方向
    """
    def __init__(self, x, bar_type):
        super().__init__()
        self.x = x
        self.w, self.h = 700, 40
        self.barx, self.bary = 700, 40
        self.bar_down = bar_type
        self.image = pg.Surface((self.w, self.h))
        self.image.set_colorkey((255, 255, 255))
        self.rect = pg.draw.rect(self.image, (0, 0, 0), (0, 0, self.w, self.h))
        self.damage = pg.draw.rect(self.image, (255, 0, 0), (2, 2, self.w-4, self.h-4))
        self.bar = pg.draw.rect(self.image, (0, 255, 0), (2, 2, self.barx-4, self.bary-4))
        self.rect.center = (self.x, 20)
        self.bar.center = self.rect.center
        self.damage.center = self.rect.center

    # hpバーの更新
    def update(self, hp):
        self.barx += hp * 7
        self.rect = pg.draw.rect(self.image, (0, 0, 0), (0, 0, self.w, self.h))
        self.damage = pg.draw.rect(self.image, (255, 0, 0), (2, 2, self.w-4, self.h-4))
        self.bar = pg.draw.rect(self.image, (0, 255, 0), (2+(700-self.barx), 2, self.barx-4, self.bary-4))
        self.rect.center = (self.x, 20)
        self.bar.center = self.rect.center
        self.damage.center = self.rect.center
    
class Attack(pg.sprite.Sprite):  #追加機能
    """
    攻撃に関するクラス
    """
    def __init__(self, Koukaton: Koukaton, kk_dire, kk_img):
        """
        パンチ画像Surfaceを生成する
        引数 bird：パンチを放つこうかとん
        """
        super().__init__()
        for k, v in kk_dire.items():
            if v == kk_img:
                print(f"{k},{v}")
                self.vx, self.vy = k
                break
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 4.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = Koukaton.rect.centery+Koukaton.rect.height*self.vy
        self.rect.centerx = Koukaton.rect.centerx+Koukaton.rect.width*self.vx #パンチの出る位置
        self.speed = 30 #パンチのスピード
        self.punch_distance = Koukaton.rect.centerx + self.speed*self.vx*10  #パンチの飛距離

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
        if  self.punch_distance < self.rect.centerx: #パンチの距離を超えると消滅する
            print("hoge")
            self.kill()
            

class start:
    """
    勝利条件に関するクラス
    """
    def __init__(self, koukaton):
        self.koukaton = koukaton
        self.timer = 60  # 初期時間
        self.reset_timer = 10  # リセットまでの時間について
        self.reset()
            
    def update(self, dt):
        """
        勝利条件の更新
        """
        # 設定した時間かこうかとんのhpが0になったときに勝利
        self.timer == dt
        if self.koukaton.hp <= 0:
            self.allow_input = False
            if self.reset_timer <= 0:
                self.reset()
            else:
                self.reset_timer -= dt

    
class Guard(pg.sprite.Sprite):
    """
    ガードに関するクラス
    """
    def __init__(self):
        super().__init__()
        self.guard_hp = 5

    def update(self, screen: pg.Surface,  koukaton: Koukaton):
        if self.guard_hp <= 0:  #ガードが不可能な場合
            koukaton.setSpeed(1.0)  #行動不可を解除
        else:
            if koukaton.getDamage() > 0:
                koukaton.setDamage(0)  #ダメージの無効化
                self.guard_hp -= 1  #ガード可能回数を減らす
            koukaton.setSpeed(0.0)  #こうかとんを移動不可にする
            pg.draw.circle(screen, (0, 255, 255), (koukaton.rect.centerx, koukaton.rect.centery), 40 * self.guard_hp)  #ガード表示
    

def main():
    pg.display.set_caption("大戦争スマッシュこうかとんファイターズ")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    attacks_1 = pg.sprite.Group()
    attacks_2 = pg.sprite.Group()

    play_1 = Koukaton(1, 2, (300, 500))
    play_2 = Koukaton(2, 2, (1300, 500))

    tmr = 0
    clock = pg.time.Clock()
    guard_1 = Guard()
    guard_2 = Guard()

    statuses = pg.sprite.Group()
    p1_stat = Status(350, 1)
    p2_stat = Status(WIDTH-350, -1)
    statuses.add(p1_stat)
    statuses.add(p2_stat)
    pg.init()
    #koukaton = Koukaton() # クラスからオブジェクト生成
    vict_condition = start(play_1)
    hyper_font = pg.font.Font(None, 50)  # 残り時間用のフォント
    hyper_color = (0, 0, 255)  # 残り時間の表示色
    fonto = pg.font.Font(None, 200)  # ゲームオーバーの文字を生成
    txt = fonto.render("Time UP", True, (255, 0, 0))
    start_screen_font = pg.font.Font(None, 200)
    start_screen_color = (200, 50, 100)  # 紫色の文字
    lnvalid_screen_color = (255, 0, 0)  # 赤色の文字

    # スタート画面についての部分
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        screen.blit(bg_img, [0, 0])

        keys = pg.key.get_pressed()

        if keys[pg.K_1]: # 「１」を押すとメインコード部分が読み込み開始
            draw_start_screen(screen, start_screen_font, "Game start", start_screen_color)
            pg.display.flip()
            pg.time.delay(2000)  # 表示を少し待つ
            break
        else: # 「１」が押されるまでの画面表示
            draw_start_screen(screen, start_screen_font, "Are you ready?", lnvalid_screen_color)
            pg.display.flip()
    tmr = 0
    clock.tick(50)
    # ここまでがスタート画面です。

    # メインコード部分
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                print("retrun")
                statuses.update(-10)
            if event.type == pg.KEYDOWN and event.key == pg.K_e:
                attacks_1.add(Attack(play_1, play_1.imgs, play_1.image))  #通常のビーム
            if event.type == pg.KEYDOWN and event.key == pg.K_u:
                attacks_2.add(Attack(play_2, play_2.imgs, play_2.image))  #通常のビーム
            
        #メイン処理
        screen.blit(bg_img, [0, 0])
        
        #メイン処理
        ###キーボード処理###
        key_lst = pg.key.get_pressed()
            
        #todo当たり判定処理
        if len(pg.sprite.spritecollide(play_2, attacks_1, True)) != 0:
                play_2.setDamage(10)
        if len(pg.sprite.spritecollide(play_1, attacks_2, True)) != 0:
                play_1.setDamage(10)
                
        
        if key_lst[pg.K_q]:
            guard_1.update(screen, play_1)
        else:                
            guard_1 = Guard()
        if key_lst[pg.K_o]:
            guard_2.update(screen, play_2)
        else:   
            guard_2 = Guard()

        if play_1.getDamage() != 0:
            p1_stat.update(-10)
        if play_2.getDamage() != 0:
            p2_stat.update(-10)

        play_1.update(key_lst, screen)
        play_2.update(key_lst, screen)
        attacks_1.update()
        attacks_1.draw(screen)
        attacks_2.update()
        attacks_2.draw(screen)
        statuses.draw(screen)
        play_1.setSpeed(7.0)
        play_2.setSpeed(7.0)

        
#        pg.display.update()

        play_1.setDamage(0)
        play_2.setDamage(0)
        
        tmr += 1
        clock.tick(50)

        dt = 30 - tmr/50 # ゲームの経過時間を計算

        # キー入力の処理 HPが減るかの確認用
        keys = pg.key.get_pressed() # キーボードの状態をゲットする

        

        if dt >= 0: # 時間が0になるまでの時間を右下に表示
            hyper_text = hyper_font.render(f"Time: {int(dt)}", True, hyper_color)
            hyper_pos = (WIDTH - hyper_text.get_width() - 10, HEIGHT - hyper_text.get_height() - 10)
            screen.blit(hyper_text, hyper_pos)  # 残り時間を表示
        elif dt <= 0: # 時間が0になった時に「Time UP」と表示
            txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(txt, txt_rect)  # Time UPを画面中央に表示
            pg.display.update()
            pg.time.delay(2000)
            return
        if play_1.getHp() <= 0:
            txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            draw_start_screen(screen, start_screen_font, "Finish!!!2P Win", lnvalid_screen_color)  # Finissh!!!を画面中央に表示
            pg.display.update()
            pg.time.delay(2000)
            return   
        if play_2.getHp() <= 0:
            txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            draw_start_screen(screen, start_screen_font, "Finish!!!1P Win", lnvalid_screen_color)  # Finissh!!!を画面中央に表示
            pg.display.update()
            pg.time.delay(2000)
            return 
        
        # 勝利条件の更新
        vict_condition.update(dt)

        # 画面の描画
        pg.display.flip()

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
