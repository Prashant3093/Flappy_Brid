import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions (default windowed mode)
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Load fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# High score file
HIGH_SCORE_FILE = "high_score.txt"

# Load assets
BACKGROUND_DAY = pygame.image.load("flappy-bird-assets/sprites/background-day.png")
BACKGROUND_NIGHT = pygame.image.load("flappy-bird-assets/sprites/background-night.png")
MESSAGE_IMAGE = pygame.image.load("flappy-bird-assets/sprites/message.png")
GAMEOVER_IMAGE = pygame.image.load("flappy-bird-assets/sprites/gameover.png")
PIPE_IMAGE = pygame.image.load("flappy-bird-assets/sprites/pipe-green.png")

# Icons for night mode and volume
SUN_ICON = pygame.image.load("flappy-bird-assets/sprites/sun-icon.png")  # Day icon
MOON_ICON = pygame.image.load("flappy-bird-assets/sprites/moon-icon.png")  # Night icon
SPEAKER_ICON = pygame.image.load("flappy-bird-assets/sprites/speaker-icon.png")  # Speaker icon
MUTED_ICON = pygame.image.load("flappy-bird-assets/sprites/muted-icon.png")  # Muted speaker icon

# Scale down the icons to app icon size (e.g., 32x32 pixels)
ICON_SIZE = (32, 32)
SUN_ICON = pygame.transform.scale(SUN_ICON, ICON_SIZE)
MOON_ICON = pygame.transform.scale(MOON_ICON, ICON_SIZE)
SPEAKER_ICON = pygame.transform.scale(SPEAKER_ICON, ICON_SIZE)
MUTED_ICON = pygame.transform.scale(MUTED_ICON, ICON_SIZE)

# Bird animation frames
BIRD_FRAMES = [
    pygame.image.load("flappy-bird-assets/sprites/yellowbird-downflap.png"),
    pygame.image.load("flappy-bird-assets/sprites/yellowbird-midflap.png"),
    pygame.image.load("flappy-bird-assets/sprites/yellowbird-upflap.png")
]

# Scale bird frames
for i in range(len(BIRD_FRAMES)):
    BIRD_FRAMES[i] = pygame.transform.scale(BIRD_FRAMES[i], (40, 30))

# Load number images (0-9)
NUMBER_IMAGES = [pygame.image.load(f"flappy-bird-assets/sprites/{i}.png") for i in range(10)]

# Load sounds
FLAP_SOUND = pygame.mixer.Sound("flappy-bird-assets/audio/wing.wav")
HIT_SOUND = pygame.mixer.Sound("flappy-bird-assets/audio/hit.wav")
POINT_SOUND = pygame.mixer.Sound("flappy-bird-assets/audio/point.wav")

# Initial volume level (0.0 to 1.0)
VOLUME_LEVEL = 1.0
pygame.mixer.music.set_volume(VOLUME_LEVEL)


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))


class Bird:
    def __init__(self, screen_width, screen_height):
        self.x = 50
        self.y = screen_height // 2
        self.width = BIRD_FRAMES[0].get_width()
        self.height = BIRD_FRAMES[0].get_height()
        self.gravity = 0.5
        self.lift = -10
        self.velocity = 0
        self.frame_index = 0
        self.animation_speed = 8  # Frames per second for bird animation
        self.animation_timer = 0

    def draw(self, screen):
        # Animate bird by cycling through frames
        screen.blit(BIRD_FRAMES[self.frame_index], (self.x, self.y))

    def update(self, screen_height):
        self.velocity += self.gravity
        self.y += self.velocity

        # Prevent the bird from going off-screen
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height
            self.velocity = 0

        # Update bird animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(BIRD_FRAMES)
            self.animation_timer = 0

    def flap(self):
        FLAP_SOUND.play()
        self.velocity = self.lift


class Pipe:
    def __init__(self, x, screen_width, screen_height):
        self.x = x
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = PIPE_IMAGE.get_width()
        self.gap = 150
        self.top = random.randint(50, screen_height - self.gap - 50)
        self.bottom = self.top + self.gap
        self.speed = 3

    def draw(self, screen):
        # Scale pipe image to fit screen height
        scaled_pipe = pygame.transform.scale(PIPE_IMAGE, (self.width, self.screen_height))
        # Draw top pipe (flipped vertically)
        screen.blit(pygame.transform.flip(scaled_pipe, False, True), (self.x, self.top - self.screen_height))
        # Draw bottom pipe
        screen.blit(scaled_pipe, (self.x, self.bottom))

    def update(self):
        self.x -= self.speed

    def off_screen(self):
        return self.x + self.width < 0

    def collide(self, bird):
        if bird.y < self.top or bird.y + bird.height > self.bottom:
            if bird.x + bird.width > self.x and bird.x < self.x + self.width:
                return True
        return False


def draw_text(text, font, color, x, y, screen):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_score(score, screen, screen_width, screen_height):
    # Convert score to string and get individual digits
    score_digits = [int(digit) for digit in str(score)]
    
    # Calculate the total width of the score
    total_width = sum(NUMBER_IMAGES[digit].get_width() for digit in score_digits)
    
    # Calculate the starting x position to align the score horizontally
    x_position = screen_width // 2 - total_width // 2  # Center horizontally
    
    # Adjust the y position to move the score higher
    y_position = screen_height // 2 - 100  # Move the score 100 pixels higher

    # Draw each digit
    for digit in score_digits:
        screen.blit(NUMBER_IMAGES[digit], (x_position, y_position - NUMBER_IMAGES[digit].get_height() // 2))
        x_position += NUMBER_IMAGES[digit].get_width()


def show_start_screen(screen, screen_width, screen_height, night_mode, volume_level, muted):
    # Scale background image to fit screen
    background = pygame.transform.scale(BACKGROUND_NIGHT if night_mode else BACKGROUND_DAY, (screen_width, screen_height))
    screen.blit(background, (0, 0))
    message_x = screen_width // 2 - MESSAGE_IMAGE.get_width() // 2
    message_y = screen_height // 2 - MESSAGE_IMAGE.get_height() // 2
    screen.blit(MESSAGE_IMAGE, (message_x, message_y))

    # Draw Start Button
    start_button = pygame.Rect(screen_width // 2 - 100, screen_height - 210, 200, 50)
    pygame.draw.rect(screen, GRAY, start_button)
    draw_text("Start", font, BLACK, start_button.x + 60, start_button.y + 10, screen)

    # Draw Night Mode Button (Icon-based)
    night_mode_button = pygame.Rect(screen_width // 2 - 50, screen_height - 160, ICON_SIZE[0], ICON_SIZE[1])
    screen.blit(MOON_ICON if night_mode else SUN_ICON, (night_mode_button.x, night_mode_button.y))

    # Draw Volume Button (Icon-based)
    volume_button = pygame.Rect(screen_width // 2 + 50, screen_height - 160, ICON_SIZE[0], ICON_SIZE[1])
    screen.blit(MUTED_ICON if muted else SPEAKER_ICON, (volume_button.x, volume_button.y))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check if Start button is clicked
                if start_button.collidepoint(mouse_x, mouse_y):
                    waiting = False
                # Check if Night Mode button is clicked
                if night_mode_button.collidepoint(mouse_x, mouse_y):
                    night_mode = not night_mode
                    return night_mode, volume_level, muted
                # Check if Volume button is clicked
                if volume_button.collidepoint(mouse_x, mouse_y):
                    muted = not muted  # Toggle mute state
                    if muted:
                        pygame.mixer.music.set_volume(0.0)
                        FLAP_SOUND.set_volume(0.0)
                        HIT_SOUND.set_volume(0.0)
                        POINT_SOUND.set_volume(0.0)
                    else:
                        pygame.mixer.music.set_volume(volume_level)
                        FLAP_SOUND.set_volume(volume_level)
                        HIT_SOUND.set_volume(volume_level)
                        POINT_SOUND.set_volume(volume_level)
                    # Redraw the screen to reflect the updated mute state
                    show_start_screen(screen, screen_width, screen_height, night_mode, volume_level, muted)
    return night_mode, volume_level, muted


def show_game_over_screen(screen, screen_width, screen_height, score, high_score, night_mode):
    # Scale background image to fit screen
    background = pygame.transform.scale(BACKGROUND_NIGHT if night_mode else BACKGROUND_DAY, (screen_width, screen_height))
    screen.blit(background, (0, 0))
    
    # Draw game over image
    gameover_x = screen_width // 2 - GAMEOVER_IMAGE.get_width() // 2
    gameover_y = screen_height // 2 - GAMEOVER_IMAGE.get_height() // 2
    screen.blit(GAMEOVER_IMAGE, (gameover_x, gameover_y))
    
    # Draw score and high score text
    draw_text(f"Score: {score}", font, BLACK, screen_width // 2 - 60, screen_height // 2 + 100, screen)
    draw_text(f"High Score: {high_score}", font, BLACK, screen_width // 2 - 90, screen_height // 2 + 140, screen)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False


def main():
    global screen  # Make screen accessible for fullscreen toggling
    high_score = load_high_score()

    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Flappy Bird")

    # Clock to control the frame rate
    clock = pygame.time.Clock()

    fullscreen = False  # Track fullscreen state
    night_mode = False  # Track night mode state
    volume_level = 1.0  # Track volume level
    muted = False       # Track mute state

    while True:  # Outer loop to allow restarting the game
        # Get current screen dimensions
        screen_width, screen_height = screen.get_width(), screen.get_height()

        # Show start screen with options
        night_mode, volume_level, muted = show_start_screen(screen, screen_width, screen_height, night_mode, volume_level, muted)

        bird = Bird(screen_width, screen_height)
        pipes = [Pipe(screen_width, screen_width, screen_height)]
        score = 0

        running = True
        game_over = False
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.flap()
                    if event.key == pygame.K_f:  # Toggle fullscreen with 'F' key
                        fullscreen = not fullscreen
                        if fullscreen:
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                        # Update screen dimensions after toggling fullscreen
                        screen_width, screen_height = screen.get_width(), screen.get_height()

            # Update bird
            bird.update(screen_height)

            # Update pipes
            for pipe in pipes:
                pipe.update()
                if pipe.off_screen():
                    pipes.remove(pipe)
                    pipes.append(Pipe(screen_width, screen_width, screen_height))
                    score += 1  # Increase score when a pipe is passed
                    POINT_SOUND.play()

                if pipe.collide(bird):
                    HIT_SOUND.play()
                    game_over = True
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

            # Check if bird hits the ground
            if bird.y + bird.height >= screen_height:
                HIT_SOUND.play()
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

            # Draw everything
            # Scale background image to fit screen
            background = pygame.transform.scale(BACKGROUND_NIGHT if night_mode else BACKGROUND_DAY, (screen_width, screen_height))
            screen.blit(background, (0, 0))  # Draw the background
            bird.draw(screen)
            for pipe in pipes:
                pipe.draw(screen)

            # Draw the score higher on the screen
            draw_score(score, screen, screen_width, screen_height)

            if game_over:
                # Show game over screen
                show_game_over_screen(screen, screen_width, screen_height, score, high_score, night_mode)
                break  # Exit the inner loop to restart the game

            # Update display
            pygame.display.flip()

            # Control frame rate
            clock.tick(30)


if __name__ == "__main__":
    main()