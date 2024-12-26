import pygame
import os
import random
import numpy as np
from PIL import Image


# 定义常量类
class Constants:
    TILE_SIZE = (100, 100)
    BOARD_SIZE = 8
    MARGIN = 10
    SCREEN_SIZE = (880, 495)


# 定义卡片类
class Card:
    def __init__(self, image_surface, unique_id):
        self.image_surface = image_surface
        self.is_matched = False
        self.id = unique_id

    def draw(self, screen, x, y):
        screen.blit(self.image_surface, (x, y))


class MemoryGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        pygame.display.set_caption("找你坤")
        self.screen = pygame.display.set_mode(Constants.SCREEN_SIZE)
        self.load_assets()
        self.init_game()
        self.game_started = False

    def load_assets(self):
        # 获取当前文件所在的目录
        base_path = os.path.dirname(os.path.abspath(__file__))

        # 加载并调整所有图片大小
        self.image_paths = [os.path.join(base_path, 'resource/images', f'image{i}.jpg') for i in range(1, 17)]
        self.images_surfaces = []
        for path in self.image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            img_array = self.load_resize_and_rotate_image(path, Constants.TILE_SIZE)
            img_surface = self.numpy_to_surface(img_array)
            self.images_surfaces.append(img_surface)

        # 加载并调整背景图片大小
        background_path = os.path.join(base_path, 'resource/images/background.png')
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"Background image not found: {background_path}")
        original_background_image = pygame.image.load(background_path).convert()
        screen_width, screen_height = Constants.SCREEN_SIZE
        img_width, img_height = original_background_image.get_size()
        ratio = min(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        self.background_image = pygame.transform.scale(original_background_image, (new_width, new_height))

    # 加载多个音效文件到列表中
    @staticmethod
    def load_sounds(directory, extensions=('wav', 'ogg')):
        sounds = []
        sound_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
        for filename in os.listdir(sound_directory):
            if any(filename.lower().endswith(ext) for ext in extensions):
                sound_path = os.path.join(sound_directory, filename)
                sounds.append(pygame.mixer.Sound(sound_path))
        return sounds

    # 加载一个音效
    def load_sound(self, sound_file_path):
        try:
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sound_file_path)
            return pygame.mixer.Sound(full_path)
        except pygame.error as e:
            print(f"无法加载音效文件{sound_file_path}:{e}")
            return None

    # 播放一个指定音效
    def play_sound(self, sound):
        if sound:
            sound.play()

    # 定义一个函数来随机播放音效
    def play_random_sound(self, sounds):
        if not sounds:
            print("没有可用的音效文件")
            return
        # 随机选择一个音效
        selected_sound = random.choice(sounds)
        # 播放音效
        selected_sound.play()

    # 绘制背景
    def draw_background(self):
        self.screen.blit(self.background_image, ((Constants.SCREEN_SIZE[0] - self.background_image.get_width()) // 2,
                                                 (Constants.SCREEN_SIZE[1] - self.background_image.get_height()) // 2))

    def draw_button(self, button_text, button_color, text_color, x, y, width, height, action=None):
        font = pygame.font.Font(None, 48)
        text_surface = font.render(button_text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        # pygame.draw.rect(self.screen, button_color, [x, y, width, height])
        self.screen.blit(text_surface, text_rect)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + width and y < mouse[1] < y + height:
            if click[0] == 1 and action:
                action()

    def init_game(self):
        """
        初始化游戏板，并为相同图案的卡片分配相同的唯一ID。
        """
        self.game_board = [[None for _ in range(Constants.BOARD_SIZE)] for _ in range(Constants.BOARD_SIZE)]
        unique_id = 0
        id_mapping = {}
        all_images = [self.flip_image_horizontally(img) for img in self.images_surfaces] * 2
        random.shuffle(all_images)

        for img in all_images:
            if img not in id_mapping:
                id_mapping[img] = unique_id
                unique_id += 1

        for i in range(Constants.BOARD_SIZE):
            for j in range(Constants.BOARD_SIZE):
                if all_images:
                    img = all_images.pop()
                    card = Card(img, id_mapping[img])
                    self.game_board[i][j] = card
        self.selected_positions = []

    def reset_game(self):
        self.load_assets()
        self.init_game()
        self.selected_positions.clear()
        self.game_started = False

    def is_game_over(self):
        for row in self.game_board:
            for card in row:
                if card and not card.is_matched:
                    return False
        return True

    def flip_image_horizontally(self, image_surface):
        return pygame.transform.flip(image_surface, True, False)

    @staticmethod
    def load_resize_and_rotate_image(image_path, target_size):
        """加载图像，调整大小并旋转90度"""
        with Image.open(image_path) as img:
            img.thumbnail(target_size)
            img = img.rotate(90, expand=True)
            img = img.convert('RGB')
            return np.array(img)

    @staticmethod
    def numpy_to_surface(numpy_array):
        """将Numpy数组转换为Pygame Surface对象"""
        return pygame.surfarray.make_surface(numpy_array)

    def is_within_bounds(self, row, col):
        """检查给定的行和列是否在 game_board 的范围内"""
        return 0 <= row < Constants.BOARD_SIZE and 0 <= col < Constants.BOARD_SIZE

    def draw_images(self):
        for row in range(Constants.BOARD_SIZE):
            for col in range(Constants.BOARD_SIZE):
                card = self.game_board[row][col]
                if card:
                    x = col * (Constants.TILE_SIZE[0] + Constants.MARGIN)
                    y = row * (Constants.TILE_SIZE[1] + Constants.MARGIN)
                    card.draw(self.screen, x, y)
        pygame.display.flip()

    def check_match(self, pos1, pos2):
        """检查两个位置上的卡片是否匹配（通过比较ID）"""
        card1 = self.game_board[pos1[0]][pos1[1]]
        card2 = self.game_board[pos2[0]][pos2[1]]
        return card1 and card2 and card1.id == card2.id

    def main_loop(self):
        sound_directory = 'resource/sounds/wav'
        sound_ji = self.load_sound('resource/sounds/鸡.wav')
        sounds = self.load_sounds(sound_directory)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_started:
                        # 检查是否点击了开始按钮
                        button_width, button_height = 200, 100
                        button_x = (Constants.SCREEN_SIZE[0] - button_width) // 2
                        button_y = (Constants.SCREEN_SIZE[1] - button_height) // 2
                        self.draw_button("Start Game", (0, 255, 0), (255, 255, 255), button_x, button_y, button_width,
                                         button_height,
                                         action=lambda: setattr(self, 'game_started', True))
                    elif self.is_game_over():
                        button_width, button_height = 200, 100
                        button_x = (Constants.SCREEN_SIZE[0] - button_width) // 2
                        button_y = (Constants.SCREEN_SIZE[1] - button_height) // 2
                        self.draw_button("Play Again", (0, 255, 0), (255, 255, 255), button_x, button_y, button_width,
                                         button_height,
                                         action=self.reset_game)
                    elif len(self.selected_positions) < 2:
                        mouse_x, mouse_y = event.pos
                        col = mouse_x // (Constants.TILE_SIZE[0] + Constants.MARGIN)
                        row = mouse_y // (Constants.TILE_SIZE[1] + Constants.MARGIN)
                        if self.is_within_bounds(row, col) and self.game_board[row][col]:
                            if len(self.selected_positions) == 1 and (row, col) == self.selected_positions[0]:
                                print("不能选择同一张图片两次！")
                                self.play_sound(sound_ji)
                                continue
                            self.selected_positions.append((row, col))
                            if len(self.selected_positions) == 2:
                                if self.check_match(*self.selected_positions):
                                    print("Match found!")
                                    self.play_random_sound(sounds)
                                    for pos in self.selected_positions:
                                        self.game_board[pos[0]][pos[1]].is_matched = True
                                        # 将匹配成功的卡片从游戏板上移除
                                        self.game_board[pos[0]][pos[1]] = None
                                else:
                                    print("No match.")
                                    self.play_sound(sound_ji)
                                self.selected_positions.clear()
            self.screen.fill((0, 0, 0))
            self.draw_background()
            if not self.game_started:
                # 绘制开始按钮和背景
                button_width, button_height = 200, 100
                button_x = (Constants.SCREEN_SIZE[0] - button_width) // 2
                button_y = (Constants.SCREEN_SIZE[1] - button_height) // 2
                self.draw_button("Start Game", (0, 255, 0), (255, 255, 255), button_x, button_y, button_width,
                                 button_height)
            elif self.is_game_over():
                button_width, button_height = 200, 100
                button_x = (Constants.SCREEN_SIZE[0] - button_width) // 2
                button_y = (Constants.SCREEN_SIZE[1] - button_height) // 2
                self.draw_button("Play Again", (0, 255, 0), (255, 255, 255), button_x, button_y, button_width,
                                 button_height)
            else:
                # 绘制游戏元素
                self.draw_images()
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    game = MemoryGame()
    game.main_loop()
