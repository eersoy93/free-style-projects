import pygame
import sys
import math
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# Platform generation constants
MIN_PLATFORM_WIDTH = 80
MAX_PLATFORM_WIDTH = 200
MIN_PLATFORM_HEIGHT = 15
MAX_PLATFORM_HEIGHT = 25
MIN_PLATFORM_GAP = 100
MAX_PLATFORM_GAP = 200

# Add new constants for improvements
PARTICLE_COUNT = 20
POWER_UP_SPAWN_CHANCE = 0.3

# Add new colors for improvements
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.animation_frame = 0
        self.animation_speed = 0.3
        self.is_jumping = False
        self.is_walking = False
        
        # Power-up effects
        self.speed_boost = False
        self.speed_boost_end = 0
        self.jump_boost = False
        self.jump_boost_end = 0
        self.invincible_power = False
        self.invincible_power_end = 0
        self.magnet_power = False
        self.magnet_power_end = 0
        
        # Mario colors
        self.hat_color = (255, 0, 0)      # Red hat
        self.shirt_color = (255, 0, 0)    # Red shirt
        self.overalls_color = (0, 0, 255) # Blue overalls
        self.skin_color = (255, 220, 177) # Skin tone
        self.mustache_color = (139, 69, 19) # Brown mustache
        self.shoe_color = (139, 69, 19)   # Brown shoes
        
    def update(self, platforms):
        current_time = pygame.time.get_ticks()
        
        # Update power-up effects
        if self.speed_boost and current_time > self.speed_boost_end:
            self.speed_boost = False
        if self.jump_boost and current_time > self.jump_boost_end:
            self.jump_boost = False
        if self.invincible_power and current_time > self.invincible_power_end:
            self.invincible_power = False
        if self.magnet_power and current_time > self.magnet_power_end:
            self.magnet_power = False
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Reset walking state
        self.is_walking = False
        
        # Determine speed based on power-ups
        current_speed = PLAYER_SPEED * 1.5 if self.speed_boost else PLAYER_SPEED
        
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -current_speed
            self.facing_right = False
            self.is_walking = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = current_speed
            self.facing_right = True
            self.is_walking = True
        else:
            self.vel_x = 0
            
        # Jumping with power-up enhancement
        jump_strength = JUMP_STRENGTH * 1.3 if self.jump_boost else JUMP_STRENGTH
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = jump_strength
            self.on_ground = False
            self.is_jumping = True
            
        # Update animation
        if self.is_walking and self.on_ground:
            self.animation_frame += self.animation_speed
        elif not self.on_ground:
            self.is_jumping = True
        else:
            self.animation_frame = 0
            self.is_jumping = False
            
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Store old position for collision resolution
        old_x = self.x
        old_y = self.y
        
        # Update horizontal position first
        self.x += self.vel_x
        
        # Check horizontal collisions
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            
            if player_rect.colliderect(platform_rect):
                # Horizontal collision - push player out
                if self.vel_x > 0:  # Moving right
                    self.x = platform.x - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = platform.x + platform.width
                self.vel_x = 0
                break
        
        # Update vertical position
        self.y += self.vel_y
        
        # Check vertical collisions
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            
            if player_rect.colliderect(platform_rect):
                if self.vel_y > 0:  # Falling down - landing on platform
                    # Only land on platform if player was above it
                    if old_y + self.height <= platform.y + 5:  # Small tolerance
                        self.y = platform.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                        self.is_jumping = False
                elif self.vel_y < 0:  # Moving up - hitting platform from below
                    # Only hit from below if player was below it
                    if old_y >= platform.y + platform.height - 5:  # Small tolerance
                        self.y = platform.y + platform.height
                        self.vel_y = 0
                break
                    
        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Ground collision (bottom of screen)
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True
            self.is_jumping = False
    
    def apply_power_up(self, power_type, duration):
        current_time = pygame.time.get_ticks()
        
        if power_type == 'speed':
            self.speed_boost = True
            self.speed_boost_end = current_time + duration
        elif power_type == 'jump':
            self.jump_boost = True
            self.jump_boost_end = current_time + duration
        elif power_type == 'invincible':
            self.invincible_power = True
            self.invincible_power_end = current_time + duration
        elif power_type == 'magnet':
            self.magnet_power = True
            self.magnet_power_end = current_time + duration
    
    def draw(self, screen):
        # Add glow effect for power-ups
        if self.invincible_power:
            # Draw invincible glow
            for i in range(3):
                glow_color = (255, 255, 0, 100 - i * 30)  # Yellow glow
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.x + self.width//2), int(self.y + self.height//2)), 
                                 self.width//2 + i * 3)
        
        if self.speed_boost:
            # Draw speed trails
            for i in range(3):
                trail_x = self.x - (i + 1) * 5 * (1 if self.facing_right else -1)
                trail_alpha = 100 - i * 30
                # Simple trail effect (you could make this more sophisticated)
                pygame.draw.circle(screen, ORANGE, 
                                 (int(trail_x + self.width//2), int(self.y + self.height//2)), 
                                 3 - i)
        
        # Draw normal player
        if self.is_jumping:
            self.draw_jumping(screen)
        elif self.is_walking:
            self.draw_walking(screen)
        else:
            self.draw_standing(screen)
    
    def draw_standing(self, screen):
        """Draw Mario in standing pose"""
        # Body base
        body_x = self.x + 4
        body_y = self.y + 8
        body_width = self.width - 8
        body_height = self.height - 8
        
        # Draw overalls (blue)
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + 2, body_y + 8, body_width - 4, body_height - 12))
        
        # Draw shirt (red) - upper body
        pygame.draw.rect(screen, self.shirt_color, 
                        (body_x + 4, body_y + 4, body_width - 8, 8))
        
        # Draw head (skin color)
        head_radius = 8
        head_x = int(self.x + self.width // 2)
        head_y = int(self.y + head_radius + 2)
        pygame.draw.circle(screen, self.skin_color, (head_x, head_y), head_radius)
        
        # Draw hat (red)
        hat_points = [
            (head_x - 10, head_y - 4),
            (head_x + 10, head_y - 4),
            (head_x + 8, head_y - 12),
            (head_x - 8, head_y - 12)
        ]
        pygame.draw.polygon(screen, self.hat_color, hat_points)
        
        # Hat brim
        pygame.draw.ellipse(screen, self.hat_color, 
                          (head_x - 12, head_y - 6, 24, 8))
        
        # Hat emblem (M)
        pygame.draw.circle(screen, WHITE, (head_x, head_y - 8), 4)
        pygame.draw.circle(screen, self.hat_color, (head_x, head_y - 8), 3)
        
        # Draw mustache
        mustache_points = [
            (head_x - 6, head_y + 2),
            (head_x - 2, head_y + 4),
            (head_x + 2, head_y + 4),
            (head_x + 6, head_y + 2)
        ]
        pygame.draw.polygon(screen, self.mustache_color, mustache_points)
        
        # Draw nose
        pygame.draw.circle(screen, (255, 200, 150), (head_x, head_y + 1), 2)
        
        # Draw eyes
        eye_offset = 4 if self.facing_right else -4
        pygame.draw.circle(screen, WHITE, (head_x - 3, head_y - 2), 2)
        pygame.draw.circle(screen, WHITE, (head_x + 3, head_y - 2), 2)
        pygame.draw.circle(screen, BLACK, (head_x - 3 + (1 if self.facing_right else -1), head_y - 2), 1)
        pygame.draw.circle(screen, BLACK, (head_x + 3 + (1 if self.facing_right else -1), head_y - 2), 1)
        
        # Draw arms
        arm_y = body_y + 6
        if self.facing_right:
            # Right arm forward
            pygame.draw.circle(screen, self.skin_color, (body_x + body_width + 2, arm_y), 3)
            pygame.draw.circle(screen, self.skin_color, (body_x - 2, arm_y + 2), 3)
        else:
            # Left arm forward
            pygame.draw.circle(screen, self.skin_color, (body_x - 2, arm_y), 3)
            pygame.draw.circle(screen, self.skin_color, (body_x + body_width + 2, arm_y + 2), 3)
        
        # Draw gloves (white circles on hands)
        if self.facing_right:
            pygame.draw.circle(screen, WHITE, (body_x + body_width + 2, arm_y), 2)
            pygame.draw.circle(screen, WHITE, (body_x - 2, arm_y + 2), 2)
        else:
            pygame.draw.circle(screen, WHITE, (body_x - 2, arm_y), 2)
            pygame.draw.circle(screen, WHITE, (body_x + body_width + 2, arm_y + 2), 2)
        
        # Draw legs
        leg_width = 4
        leg_height = 8
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + 2, body_y + body_height - 4, leg_width, leg_height))
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + body_width - 6, body_y + body_height - 4, leg_width, leg_height))
        
        # Draw shoes
        shoe_width = 8
        shoe_height = 4
        pygame.draw.ellipse(screen, self.shoe_color, 
                          (body_x, self.y + self.height - shoe_height, shoe_width, shoe_height))
        pygame.draw.ellipse(screen, self.shoe_color, 
                          (body_x + body_width - shoe_width, self.y + self.height - shoe_height, 
                           shoe_width, shoe_height))
        
        # Draw overalls straps
        pygame.draw.line(screen, self.overalls_color, 
                        (body_x + 6, body_y + 4), (body_x + 4, body_y + 12), 2)
        pygame.draw.line(screen, self.overalls_color, 
                        (body_x + body_width - 6, body_y + 4), (body_x + body_width - 4, body_y + 12), 2)
        
        # Draw buttons on overalls
        pygame.draw.circle(screen, YELLOW, (body_x + 6, body_y + 8), 1)
        pygame.draw.circle(screen, YELLOW, (body_x + body_width - 6, body_y + 8), 1)
    
    def draw_walking(self, screen):
        """Draw Mario in walking animation"""
        # Walking animation with leg movement
        leg_offset = int(math.sin(self.animation_frame * 4) * 2)
        arm_swing = int(math.sin(self.animation_frame * 4) * 1)
        
        # Body base
        body_x = self.x + 4
        body_y = self.y + 8 + abs(leg_offset) // 2  # Slight bounce
        body_width = self.width - 8
        body_height = self.height - 8
        
        # Draw overalls (blue)
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + 2, body_y + 8, body_width - 4, body_height - 12))
        
        # Draw shirt (red) - upper body
        pygame.draw.rect(screen, self.shirt_color, 
                        (body_x + 4, body_y + 4, body_width - 8, 8))
        
        # Draw head (skin color) - slight head bob
        head_radius = 8
        head_x = int(self.x + self.width // 2)
        head_y = int(body_y + head_radius - 6 + abs(leg_offset) // 4)
        pygame.draw.circle(screen, self.skin_color, (head_x, head_y), head_radius)
        
        # Draw hat (red)
        hat_points = [
            (head_x - 10, head_y - 4),
            (head_x + 10, head_y - 4),
            (head_x + 8, head_y - 12),
            (head_x - 8, head_y - 12)
        ]
        pygame.draw.polygon(screen, self.hat_color, hat_points)
        
        # Hat brim
        pygame.draw.ellipse(screen, self.hat_color, 
                          (head_x - 12, head_y - 6, 24, 8))
        
        # Hat emblem (M)
        pygame.draw.circle(screen, WHITE, (head_x, head_y - 8), 4)
        pygame.draw.circle(screen, self.hat_color, (head_x, head_y - 8), 3)
        
        # Draw mustache
        mustache_points = [
            (head_x - 6, head_y + 2),
            (head_x - 2, head_y + 4),
            (head_x + 2, head_y + 4),
            (head_x + 6, head_y + 2)
        ]
        pygame.draw.polygon(screen, self.mustache_color, mustache_points)
        
        # Draw nose
        pygame.draw.circle(screen, (255, 200, 150), (head_x, head_y + 1), 2)
        
        # Draw eyes
        pygame.draw.circle(screen, WHITE, (head_x - 3, head_y - 2), 2)
        pygame.draw.circle(screen, WHITE, (head_x + 3, head_y - 2), 2)
        pygame.draw.circle(screen, BLACK, (head_x - 3 + (1 if self.facing_right else -1), head_y - 2), 1)
        pygame.draw.circle(screen, BLACK, (head_x + 3 + (1 if self.facing_right else -1), head_y - 2), 1)
        
        # Draw arms with swinging motion
        arm_y = body_y + 6
        if self.facing_right:
            pygame.draw.circle(screen, self.skin_color, (body_x + body_width + 2, arm_y + arm_swing), 3)
            pygame.draw.circle(screen, self.skin_color, (body_x - 2, arm_y - arm_swing), 3)
            # Gloves
            pygame.draw.circle(screen, WHITE, (body_x + body_width + 2, arm_y + arm_swing), 2)
            pygame.draw.circle(screen, WHITE, (body_x - 2, arm_y - arm_swing), 2)
        else:
            pygame.draw.circle(screen, self.skin_color, (body_x - 2, arm_y + arm_swing), 3)
            pygame.draw.circle(screen, self.skin_color, (body_x + body_width + 2, arm_y - arm_swing), 3)
            # Gloves
            pygame.draw.circle(screen, WHITE, (body_x - 2, arm_y + arm_swing), 2)
            pygame.draw.circle(screen, WHITE, (body_x + body_width + 2, arm_y - arm_swing), 2)
        
        # Draw legs with walking animation
        leg_width = 4
        leg_height = 8
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + 2, body_y + body_height - 4, leg_width, leg_height + leg_offset))
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + body_width - 6, body_y + body_height - 4, leg_width, leg_height - leg_offset))
        
        # Draw shoes with walking animation
        shoe_width = 8
        shoe_height = 4
        pygame.draw.ellipse(screen, self.shoe_color, 
                          (body_x, self.y + self.height - shoe_height + leg_offset, shoe_width, shoe_height))
        pygame.draw.ellipse(screen, self.shoe_color, 
                          (body_x + body_width - shoe_width - 1, self.y + self.height - shoe_height - leg_offset, 
                           shoe_width, shoe_height))
        
        # Draw overalls straps
        pygame.draw.line(screen, self.overalls_color, 
                        (body_x + 6, body_y + 4), (body_x + 4, body_y + 12), 2)
        pygame.draw.line(screen, self.overalls_color, 
                        (body_x + body_width - 6, body_y + 4), (body_x + body_width - 4, body_y + 12), 2)
        
        # Draw buttons on overalls
        pygame.draw.circle(screen, YELLOW, (body_x + 6, body_y + 8), 1)
        pygame.draw.circle(screen, YELLOW, (body_x + body_width - 6, body_y + 8), 1)
    
    def draw_jumping(self, screen):
        """Draw Mario in jumping pose"""
        # Body base
        body_x = self.x + 4
        body_y = self.y + 8
        body_width = self.width - 8
        body_height = self.height - 8
        
        # Draw overalls (blue)
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + 2, body_y + 8, body_width - 4, body_height - 12))
        
        # Draw shirt (red) - upper body
        pygame.draw.rect(screen, self.shirt_color, 
                        (body_x + 4, body_y + 4, body_width - 8, 8))
        
        # Draw head (skin color)
        head_radius = 8
        head_x = int(self.x + self.width // 2)
        head_y = int(self.y + head_radius + 2)
        pygame.draw.circle(screen, self.skin_color, (head_x, head_y), head_radius)
        
        # Draw hat (red)
        hat_points = [
            (head_x - 10, head_y - 4),
            (head_x + 10, head_y - 4),
            (head_x + 8, head_y - 12),
            (head_x - 8, head_y - 12)
        ]
        pygame.draw.polygon(screen, self.hat_color, hat_points)
        
        # Hat brim
        pygame.draw.ellipse(screen, self.hat_color, 
                          (head_x - 12, head_y - 6, 24, 8))
        
        # Hat emblem (M)
        pygame.draw.circle(screen, WHITE, (head_x, head_y - 8), 4)
        pygame.draw.circle(screen, self.hat_color, (head_x, head_y - 8), 3)
        
        # Draw mustache
        mustache_points = [
            (head_x - 6, head_y + 2),
            (head_x - 2, head_y + 4),
            (head_x + 2, head_y + 4),
            (head_x + 6, head_y + 2)
        ]
        pygame.draw.polygon(screen, self.mustache_color, mustache_points)
        
        # Draw nose
        pygame.draw.circle(screen, (255, 200, 150), (head_x, head_y + 1), 2)
        
        # Draw eyes (excited expression)
        pygame.draw.circle(screen, WHITE, (head_x - 3, head_y - 2), 2)
        pygame.draw.circle(screen, WHITE, (head_x + 3, head_y - 2), 2)
        pygame.draw.circle(screen, BLACK, (head_x - 3, head_y - 3), 1)  # Eyes looking up
        pygame.draw.circle(screen, BLACK, (head_x + 3, head_y - 3), 1)
        
        # Draw arms raised up (jumping pose)
        arm_y = body_y + 2
        if self.facing_right:
            pygame.draw.circle(screen, self.skin_color, (body_x + body_width + 4, arm_y - 4), 3)
            pygame.draw.circle(screen, self.skin_color, (body_x - 4, arm_y - 2), 3)
            # Gloves
            pygame.draw.circle(screen, WHITE, (body_x + body_width + 4, arm_y - 4), 2)
            pygame.draw.circle(screen, WHITE, (body_x - 4, arm_y - 2), 2)
        else:
            pygame.draw.circle(screen, self.skin_color, (body_x - 4, arm_y - 4), 3)
            pygame.draw.circle(screen, self.skin_color, (body_x + body_width + 4, arm_y - 2), 3)
            # Gloves
            pygame.draw.circle(screen, WHITE, (body_x - 4, arm_y - 4), 2)
            pygame.draw.circle(screen, WHITE, (body_x + body_width + 4, arm_y - 2), 2)
        
        # Draw legs bent (jumping pose)
        leg_width = 4
        leg_height = 6  # Shorter legs when jumping
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + 3, body_y + body_height - 2, leg_width, leg_height))
        pygame.draw.rect(screen, self.overalls_color, 
                        (body_x + body_width - 7, body_y + body_height - 2, leg_width, leg_height))
        
        # Draw shoes (slightly angled for jumping)
        shoe_width = 8
        shoe_height = 4
        pygame.draw.ellipse(screen, self.shoe_color, 
                          (body_x + 1, self.y + self.height - shoe_height + 2, shoe_width, shoe_height))
        pygame.draw.ellipse(screen, self.shoe_color, 
                          (body_x + body_width - shoe_width - 1, self.y + self.height - shoe_height + 2, 
                           shoe_width, shoe_height))
        
        # Draw overalls straps
        pygame.draw.line(screen, self.overalls_color, 
                        (body_x + 6, body_y + 4), (body_x + 4, body_y + 12), 2)
        pygame.draw.line(screen, self.overalls_color, 
                        (body_x + body_width - 6, body_y + 4), (body_x + body_width - 4, body_y + 12), 2)
        
        # Draw buttons on overalls
        pygame.draw.circle(screen, YELLOW, (body_x + 6, body_y + 8), 1)
        pygame.draw.circle(screen, YELLOW, (body_x + body_width - 6, body_y + 8), 1)

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.platform_type = random.choice(['brick', 'stone', 'grass', 'metal'])
        
    def draw(self, screen):
        if self.platform_type == 'brick':
            self.draw_brick_platform(screen)
        elif self.platform_type == 'stone':
            self.draw_stone_platform(screen)
        elif self.platform_type == 'grass':
            self.draw_grass_platform(screen)
        elif self.platform_type == 'metal':
            self.draw_metal_platform(screen)
    
    def draw_brick_platform(self, screen):
        # Base brick color with gradient
        brick_colors = [
            (139, 69, 19),   # Dark brown
            (160, 82, 45),   # Medium brown
            (205, 133, 63),  # Light brown
            (222, 184, 135)  # Very light brown
        ]
        
        # Draw main platform with gradient effect
        for i in range(self.height):
            color_index = min(i // (self.height // 4 + 1), len(brick_colors) - 1)
            color = brick_colors[color_index]
            pygame.draw.rect(screen, color, (self.x, self.y + i, self.width, 1))
        
        # Draw individual bricks
        brick_width = 32
        brick_height = 16
        
        for row in range(0, self.height, brick_height):
            for col in range(0, self.width, brick_width):
                # Offset every other row for realistic brick pattern
                offset = (brick_width // 2) if (row // brick_height) % 2 == 1 else 0
                brick_x = self.x + col + offset
                brick_y = self.y + row
                
                # Don't draw partial bricks outside platform
                if brick_x + brick_width > self.x + self.width:
                    continue
                    
                # Draw brick outline
                pygame.draw.rect(screen, (101, 67, 33), 
                               (brick_x, brick_y, brick_width, brick_height), 2)
                
                # Add highlight on top and left
                pygame.draw.line(screen, (255, 228, 196), 
                               (brick_x + 1, brick_y + 1), 
                               (brick_x + brick_width - 2, brick_y + 1), 1)
                pygame.draw.line(screen, (255, 228, 196), 
                               (brick_x + 1, brick_y + 1), 
                               (brick_x + 1, brick_y + brick_height - 2), 1)
    
    def draw_stone_platform(self, screen):
        # Stone gray gradient
        stone_colors = [
            (105, 105, 105),  # Dim gray
            (128, 128, 128),  # Gray
            (169, 169, 169),  # Dark gray
            (192, 192, 192)   # Silver
        ]
        
        # Draw gradient background
        for i in range(self.height):
            color_index = min(i // (self.height // 4 + 1), len(stone_colors) - 1)
            color = stone_colors[color_index]
            pygame.draw.rect(screen, color, (self.x, self.y + i, self.width, 1))
        
        # Draw stone blocks
        block_size = 24
        for row in range(0, self.height, block_size):
            for col in range(0, self.width, block_size):
                block_x = self.x + col
                block_y = self.y + row
                
                if block_x + block_size > self.x + self.width:
                    continue
                
                # Draw block with 3D effect
                pygame.draw.rect(screen, (169, 169, 169), 
                               (block_x, block_y, block_size, block_size))
                pygame.draw.rect(screen, (105, 105, 105), 
                               (block_x, block_y, block_size, block_size), 2)
                
                # Highlight
                pygame.draw.line(screen, (211, 211, 211), 
                               (block_x + 1, block_y + 1), 
                               (block_x + block_size - 2, block_y + 1), 1)
                pygame.draw.line(screen, (211, 211, 211), 
                               (block_x + 1, block_y + 1), 
                               (block_x + 1, block_y + block_size - 2), 1)
                
                # Add some texture dots
                for _ in range(3):
                    dot_x = block_x + random.randint(3, block_size - 3)
                    dot_y = block_y + random.randint(3, block_size - 3)
                    pygame.draw.circle(screen, (128, 128, 128), (dot_x, dot_y), 1)
    
    def draw_grass_platform(self, screen):
        # Draw dirt base
        dirt_color = (101, 67, 33)
        pygame.draw.rect(screen, dirt_color, (self.x, self.y + 4, self.width, self.height - 4))
        
        # Draw grass top
        grass_color = (34, 139, 34)
        pygame.draw.rect(screen, grass_color, (self.x, self.y, self.width, 8))
        
        # Add grass blades
        for i in range(0, self.width, 4):
            grass_x = self.x + i + random.randint(-1, 1)
            grass_height = random.randint(3, 6)
            
            # Draw grass blade
            pygame.draw.line(screen, (0, 128, 0), 
                           (grass_x, self.y), 
                           (grass_x, self.y - grass_height), 2)
            
            # Add lighter green highlight
            pygame.draw.line(screen, (50, 205, 50), 
                           (grass_x - 1, self.y), 
                           (grass_x - 1, self.y - grass_height + 1), 1)
        
        # Add some flowers
        if self.width > 60:
            for _ in range(self.width // 80):
                flower_x = self.x + random.randint(10, self.width - 10)
                flower_y = self.y - 2
                
                # Draw flower
                flower_colors = [(255, 192, 203), (255, 255, 0), (255, 165, 0)]
                flower_color = random.choice(flower_colors)
                pygame.draw.circle(screen, flower_color, (flower_x, flower_y), 2)
                pygame.draw.circle(screen, (255, 255, 255), (flower_x, flower_y), 1)
    
    def draw_metal_platform(self, screen):
        # Metal gradient
        metal_colors = [
            (169, 169, 169),  # Dark gray
            (192, 192, 192),  # Silver
            (211, 211, 211),  # Light gray
            (220, 220, 220)   # Very light gray
        ]
        
        # Draw gradient background
        for i in range(self.height):
            color_index = min(i // (self.height // 4 + 1), len(metal_colors) - 1)
            color = metal_colors[color_index]
            pygame.draw.rect(screen, color, (self.x, self.y + i, self.width, 1))
        
        # Draw metal panels
        panel_width = 40
        for col in range(0, self.width, panel_width):
            panel_x = self.x + col
            
            if panel_x + panel_width > self.x + self.width:
                continue
            
            # Draw panel outline
            pygame.draw.rect(screen, (105, 105, 105), 
                           (panel_x, self.y, panel_width, self.height), 2)
            
            # Add rivets
            rivet_positions = [
                (panel_x + 5, self.y + 5),
                (panel_x + panel_width - 5, self.y + 5),
                (panel_x + 5, self.y + self.height - 5),
                (panel_x + panel_width - 5, self.y + self.height - 5)
            ]
            
            for rivet_x, rivet_y in rivet_positions:
                if rivet_y >= self.y and rivet_y <= self.y + self.height:
                    pygame.draw.circle(screen, (105, 105, 105), (rivet_x, rivet_y), 2)
                    pygame.draw.circle(screen, (169, 169, 169), (rivet_x, rivet_y), 1)
        
        # Add metallic shine effect
        shine_y = self.y + self.height // 3
        pygame.draw.line(screen, (255, 255, 255), 
                        (self.x, shine_y), 
                        (self.x + self.width, shine_y), 1)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.vel_x = -2
        self.vel_y = 0
        self.alive = True
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.enemy_type = random.choice(['goomba', 'koopa', 'spiky', 'ghost'])
        self.on_ground = False  # Add ground tracking for enemies
        
        # Set properties based on enemy type
        if self.enemy_type == 'goomba':
            self.color = (139, 69, 19)  # Brown
            self.width = 24
            self.height = 24
            self.vel_x = random.choice([-1.5, 1.5])
        elif self.enemy_type == 'koopa':
            self.color = (0, 128, 0)  # Green
            self.width = 26
            self.height = 28
            self.vel_x = random.choice([-2, 2])
        elif self.enemy_type == 'spiky':
            self.color = (128, 0, 128)  # Purple
            self.width = 22
            self.height = 22
            self.vel_x = random.choice([-1, 1])
        elif self.enemy_type == 'ghost':
            self.color = (240, 248, 255)  # Ghost white
            self.width = 26
            self.height = 26
            self.vel_x = random.choice([-0.8, 0.8])
            self.float_offset = 0
        
    def update(self, platforms):
        if not self.alive:
            return
            
        # Update animation
        self.animation_frame += self.animation_speed
        
        # Special behavior for ghost enemies
        if self.enemy_type == 'ghost':
            # Ghosts fly horizontally and ignore gravity
            self.x += self.vel_x
            
            # Reverse direction at screen edges
            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
                self.vel_x *= -1
            
            # Optional: Add slight vertical floating motion (much smaller)
            self.float_offset += 0.05
            # Keep the slight floating but make it much more subtle
            # This adds a small up-down motion while maintaining horizontal flight
        else:
            # Store old position for better collision detection
            old_x = self.x
            old_y = self.y
            
            # Apply gravity for non-ghost enemies
            self.vel_y += GRAVITY
            
            # Update horizontal position first
            self.x += self.vel_x
            
            # Check horizontal collisions with platforms
            enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            for platform in platforms:
                platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
                
                if enemy_rect.colliderect(platform_rect):
                    # Horizontal collision - reverse direction
                    if self.vel_x > 0:  # Moving right
                        self.x = platform.x - self.width
                    elif self.vel_x < 0:  # Moving left
                        self.x = platform.x + platform.width
                    self.vel_x *= -1
                    break
            
            # Update vertical position
            self.y += self.vel_y
            
            # Check vertical collisions with platforms
            self.on_ground = False
            enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
            for platform in platforms:
                platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
                
                if enemy_rect.colliderect(platform_rect):
                    if self.vel_y > 0:  # Falling down
                        # Only land if enemy was above platform
                        if old_y + self.height <= platform.y + 5:
                            self.y = platform.y - self.height
                            self.vel_y = 0
                            self.on_ground = True
                    elif self.vel_y < 0:  # Moving up
                        # Hit platform from below
                        if old_y >= platform.y + platform.height - 5:
                            self.y = platform.y + platform.height
                            self.vel_y = 0
                    break
                        
            # Ground collision
            if self.y > SCREEN_HEIGHT - self.height:
                self.y = SCREEN_HEIGHT - self.height
                self.vel_y = 0
                self.on_ground = True
        
        # Reverse direction at screen edges (for non-ghosts, this is handled above for ghosts)
        if self.enemy_type != 'ghost':
            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
                self.vel_x *= -1
                
            # Platform edge detection for non-ghost enemies (improved)
            if self.on_ground:
                self.check_platform_edges(platforms)
    
    def check_platform_edges(self, platforms):
        """Make enemies turn around at platform edges - improved version"""
        # Check if enemy is about to walk off a platform
        look_ahead_distance = 10
        look_ahead_x = self.x + (look_ahead_distance if self.vel_x > 0 else -look_ahead_distance)
        
        # Create a small rectangle at the enemy's feet, looking ahead
        foot_rect = pygame.Rect(look_ahead_x, self.y + self.height, 5, 10)
        
        on_platform = False
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if foot_rect.colliderect(platform_rect):
                on_platform = True
                break
        
        # If no platform ahead and enemy is on ground, turn around
        if not on_platform and self.on_ground:
            self.vel_x *= -1
    
    def draw(self, screen):
        if not self.alive:
            return
            
        if self.enemy_type == 'goomba':
            self.draw_goomba(screen)
        elif self.enemy_type == 'koopa':
            self.draw_koopa(screen)
        elif self.enemy_type == 'spiky':
            self.draw_spiky(screen)
        elif self.enemy_type == 'ghost':
            self.draw_ghost(screen)
    
    def draw_goomba(self, screen):
        # Goomba body (mushroom-like)
        body_color = (139, 69, 19)
        dark_brown = (101, 67, 33)
        light_brown = (160, 82, 45)
        
        # Main body
        pygame.draw.ellipse(screen, body_color, 
                          (self.x, self.y + 8, self.width, self.height - 8))
        
        # Head/cap
        pygame.draw.ellipse(screen, dark_brown, 
                          (self.x + 2, self.y, self.width - 4, 16))
        
        # Cap spots
        spot_positions = [(self.x + 6, self.y + 3), (self.x + 16, self.y + 5)]
        for spot_x, spot_y in spot_positions:
            pygame.draw.circle(screen, light_brown, (spot_x, spot_y), 2)
        
        # Eyes
        eye_y = self.y + 10
        # Angry eyebrows
        pygame.draw.line(screen, BLACK, (self.x + 6, eye_y - 2), (self.x + 10, eye_y), 2)
        pygame.draw.line(screen, BLACK, (self.x + 14, eye_y), (self.x + 18, eye_y - 2), 2)
        
        # Eyes
        pygame.draw.circle(screen, WHITE, (int(self.x + 8), eye_y), 3)
        pygame.draw.circle(screen, WHITE, (int(self.x + 16), eye_y), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + 8), eye_y), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 16), eye_y), 2)
        
        # Feet (animated)
        foot_offset = int(math.sin(self.animation_frame * 3) * 2)
        pygame.draw.ellipse(screen, dark_brown, 
                          (self.x + 2 + foot_offset, self.y + self.height - 4, 6, 4))
        pygame.draw.ellipse(screen, dark_brown, 
                          (self.x + self.width - 8 - foot_offset, self.y + self.height - 4, 6, 4))
    
    def draw_koopa(self, screen):
        # Koopa shell
        shell_color = (0, 128, 0)
        shell_dark = (0, 100, 0)
        shell_light = (50, 178, 50)
        
        # Shell body
        pygame.draw.ellipse(screen, shell_color, 
                          (self.x, self.y + 6, self.width, self.height - 10))
        
        # Shell pattern
        pygame.draw.ellipse(screen, shell_dark, 
                          (self.x + 2, self.y + 8, self.width - 4, self.height - 14), 2)
        
        # Shell segments
        for i in range(3):
            segment_y = self.y + 10 + i * 4
            pygame.draw.line(screen, shell_dark, 
                           (self.x + 4, segment_y), (self.x + self.width - 4, segment_y), 1)
        
        # Head
        head_color = (255, 255, 0)  # Yellow
        pygame.draw.circle(screen, head_color, 
                         (int(self.x + self.width // 2), int(self.y + 8)), 6)
        
        # Eyes
        eye_x = self.x + self.width // 2
        pygame.draw.circle(screen, WHITE, (int(eye_x - 3), int(self.y + 6)), 2)
        pygame.draw.circle(screen, WHITE, (int(eye_x + 3), int(self.y + 6)), 2)
        pygame.draw.circle(screen, BLACK, (int(eye_x - 3), int(self.y + 6)), 1)
        pygame.draw.circle(screen, BLACK, (int(eye_x + 3), int(self.y + 6)), 1)
        
        # Feet
        foot_offset = int(math.sin(self.animation_frame * 2) * 1)
        pygame.draw.ellipse(screen, (255, 200, 0), 
                          (self.x + 3 + foot_offset, self.y + self.height - 6, 5, 6))
        pygame.draw.ellipse(screen, (255, 200, 0), 
                          (self.x + self.width - 8 - foot_offset, self.y + self.height - 6, 5, 6))
    
    def draw_spiky(self, screen):
        # Spiky enemy body
        body_color = (128, 0, 128)  # Purple
        dark_purple = (100, 0, 100)
        
        # Main body
        pygame.draw.circle(screen, body_color, 
                         (int(self.x + self.width // 2), int(self.y + self.height // 2)), 
                         self.width // 2)
        
        # Spikes around the body
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        radius = self.width // 2
        
        for angle in range(0, 360, 45):
            spike_angle = math.radians(angle + self.animation_frame * 20)
            spike_x = center_x + math.cos(spike_angle) * radius
            spike_y = center_y + math.sin(spike_angle) * radius
            spike_end_x = center_x + math.cos(spike_angle) * (radius + 6)
            spike_end_y = center_y + math.sin(spike_angle) * (radius + 6)
            
            pygame.draw.line(screen, dark_purple, 
                           (spike_x, spike_y), (spike_end_x, spike_end_y), 3)
        
        # Eyes
        pygame.draw.circle(screen, RED, (int(center_x - 4), int(center_y - 2)), 3)
        pygame.draw.circle(screen, RED, (int(center_x + 4), int(center_y - 2)), 3)
        pygame.draw.circle(screen, BLACK, (int(center_x - 4), int(center_y - 2)), 2)
        pygame.draw.circle(screen, BLACK, (int(center_x + 4), int(center_y - 2)), 2)
        
        # Angry mouth
        pygame.draw.arc(screen, BLACK, 
                       (center_x - 6, center_y + 2, 12, 8), 0, math.pi, 2)
    
    def draw_ghost(self, screen):
        # Ghost body with transparency effect
        ghost_colors = [
            (240, 248, 255),  # Ghost white
            (220, 228, 235),  # Slightly darker
            (200, 208, 215)   # Even darker
        ]
        
        # Much more subtle floating animation - just for visual effect
        float_y = self.y + math.sin(self.float_offset) * 1  # Reduced from 2 to 1
        
        # Ghost body (wavy bottom)
        body_points = []
        for i in range(self.width + 1):
            wave_y = float_y + self.height - 6 + math.sin((i + self.animation_frame * 10) * 0.5) * 3
            body_points.append((self.x + i, wave_y))
        
        # Add top of ghost
        for i in range(self.width, -1, -1):
            body_points.append((self.x + i, float_y + 6))
        
        # Draw ghost body with gradient effect
        for i, color in enumerate(ghost_colors):
            offset = i * 2
            if len(body_points) > 4:
                adjusted_points = [(x + offset, y + offset) for x, y in body_points]
                if len(adjusted_points) >= 3:
                    pygame.draw.polygon(screen, color, adjusted_points)
        
        # Ghost head
        pygame.draw.circle(screen, ghost_colors[0], 
                         (int(self.x + self.width // 2), int(float_y + 8)), 10)
        
        # Eyes (spooky)
        eye_color = (0, 0, 139)  # Dark blue
        pygame.draw.circle(screen, eye_color, 
                         (int(self.x + self.width // 2 - 4), int(float_y + 6)), 3)
        pygame.draw.circle(screen, eye_color, 
                         (int(self.x + self.width // 2 + 4), int(float_y + 6)), 3)
        
        # Glowing effect
        glow_radius = int(12 + math.sin(self.animation_frame * 2) * 2)
        glow_color = (240, 248, 255, 50)  # Semi-transparent white
        
        # Mouth (wavy)
        mouth_y = float_y + 12
        mouth_points = []
        for i in range(-4, 5):
            mouth_x = self.x + self.width // 2 + i
            mouth_wave = mouth_y + math.sin(i * 0.8 + self.animation_frame * 3) * 1
            mouth_points.append((mouth_x, mouth_wave))
        
        if len(mouth_points) >= 2:
            pygame.draw.lines(screen, BLACK, False, mouth_points, 2)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.collected = False
        self.rotation = 0
        
    def update(self):
        self.rotation += 5
        
    def draw(self, screen):
        if not self.collected:
            # Animate coin rotation
            scale = abs(math.cos(math.radians(self.rotation)))
            width = int(self.width * scale)
            if width > 2:
                coin_rect = pygame.Rect(self.x + (self.width - width) // 2, self.y, width, self.height)
                pygame.draw.ellipse(screen, YELLOW, coin_rect)
                pygame.draw.ellipse(screen, BLACK, coin_rect, 2)

class Particle:
    def __init__(self, x, y, color, vel_x=0, vel_y=0, life=60):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x + random.uniform(-2, 2)
        self.vel_y = vel_y + random.uniform(-3, -1)
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 4)
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1  # Gravity
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = int(self.size * (self.life / self.max_life))
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
        self.animation_frame = 0
        
        # Better random distribution of power types
        power_types = ['speed', 'jump', 'invincible', 'magnet']
        weights = [25, 25, 20, 30]  # Magnet slightly more common, invincible slightly less
        self.power_type = random.choices(power_types, weights=weights)[0]
        
        self.float_offset = random.uniform(0, 6.28)  # Random start phase
        
        # Set properties based on power type
        if self.power_type == 'speed':
            self.color = ORANGE
            self.effect_duration = 5000  # 5 seconds
        elif self.power_type == 'jump':
            self.color = GREEN
            self.effect_duration = 5000
        elif self.power_type == 'invincible':
            self.color = PURPLE
            self.effect_duration = 3000  # 3 seconds
        elif self.power_type == 'magnet':
            self.color = CYAN
            self.effect_duration = 4000  # 4 seconds
            
    def update(self):
        self.animation_frame += 0.1
        self.float_offset += 0.05
        
    def draw(self, screen):
        if not self.collected:
            # Floating animation
            float_y = self.y + math.sin(self.float_offset) * 3
            
            # Draw power-up with glow effect (more visible)
            for i in range(4):  # More glow layers
                size = self.width // 2 + i * 3
                alpha_color = tuple(min(255, c + 60 - i * 15) for c in self.color)
                pygame.draw.circle(screen, alpha_color, 
                                 (int(self.x + self.width//2), int(float_y + self.height//2)), size)
            
            # Draw icon based on type (larger and more visible)
            center_x = int(self.x + self.width//2)
            center_y = int(float_y + self.height//2)
            
            if self.power_type == 'speed':
                # Draw speed lines (larger)
                for i in range(4):
                    pygame.draw.line(screen, WHITE, 
                                   (center_x - 10 + i*3, center_y - 3), 
                                   (center_x - 5 + i*3, center_y + 3), 3)
            elif self.power_type == 'jump':
                # Draw up arrow (larger)
                pygame.draw.polygon(screen, WHITE, [
                    (center_x, center_y - 8),
                    (center_x - 6, center_y + 4),
                    (center_x + 6, center_y + 4)
                ])
            elif self.power_type == 'invincible':
                # Draw star (larger)
                points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5 - math.pi/2
                    x = center_x + math.cos(angle) * 8
                    y = center_y + math.sin(angle) * 8
                    points.append((x, y))
                pygame.draw.polygon(screen, WHITE, points)
            elif self.power_type == 'magnet':
                # Draw magnet shape (larger)
                pygame.draw.rect(screen, WHITE, (center_x - 4, center_y - 8, 3, 12))
                pygame.draw.rect(screen, WHITE, (center_x + 1, center_y - 8, 3, 12))
                pygame.draw.rect(screen, WHITE, (center_x - 6, center_y - 8, 5, 3))
                pygame.draw.rect(screen, WHITE, (center_x + 1, center_y - 8, 5, 3))
                pygame.draw.rect(screen, WHITE, (center_x - 6, center_y + 5, 5, 3))
                pygame.draw.rect(screen, WHITE, (center_x + 1, center_y + 5, 5, 3))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario Bros Clone - Enhanced Edition")
        self.clock = pygame.time.Clock()
        
        # Initialize music
        self.music_playing = False
        self.music_volume = 0.7
        self.load_music()
        
        # Load sound effects
        self.load_sound_effects()
        
        # Game objects
        self.player = Player(100, 400)
        
        # Generate random platforms
        self.platforms = self.generate_random_platforms()
        
        # Generate enemies, coins, and power-ups based on platforms
        self.enemies = self.generate_enemies()
        self.coins = self.generate_coins()
        self.power_ups = self.generate_power_ups()
        
        # Particle system
        self.particles = []
        
        # Enhanced game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo_multiplier = 1
        self.combo_timer = 0
        self.invulnerable = False  # Make sure this is explicitly set to False
        self.invulnerable_time = 0
        self.invulnerable_duration = 2000
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.game_won = False
        self.game_over = False
        self.win_time = 0
        self.start_time = pygame.time.get_ticks()
        
        # Add countdown timer
        self.countdown_duration = 120  # 2 minutes in seconds
        self.countdown_start_time = pygame.time.get_ticks()
        self.time_warning_played = False  # To play warning sound at 30 seconds
        
        # Camera shake effect
        self.camera_shake = 0
        self.camera_shake_duration = 0
    
    def generate_power_ups(self):
        power_ups = []
        
        # Place power-ups on platforms and in floating positions
        available_platforms = [p for p in self.platforms 
                             if p.y < SCREEN_HEIGHT - 50 and p.width >= 60]
        
        if not available_platforms:
            return power_ups
        
        # Generate 2-4 power-ups guaranteed
        num_power_ups = random.randint(2, 4)
        
        # Method 1: Place some power-ups on platforms
        platform_power_ups = min(num_power_ups // 2 + 1, len(available_platforms))
        selected_platforms = random.sample(available_platforms, platform_power_ups)
        
        for platform in selected_platforms:
            power_up_x = random.randint(int(platform.x + 10), 
                                      int(platform.x + platform.width - 30))
            power_up_y = platform.y - 25
            power_ups.append(PowerUp(power_up_x, power_up_y))
        
        # Method 2: Place remaining power-ups in floating positions
        remaining_power_ups = num_power_ups - len(power_ups)
        
        for _ in range(remaining_power_ups):
            attempts = 0
            placed = False
            
            while attempts < 30 and not placed:
                # Random position anywhere on screen
                x = random.randint(50, SCREEN_WIDTH - 70)
                y = random.randint(100, SCREEN_HEIGHT - 200)
                
                # Check if position is reachable from at least one platform
                reachable = False
                MAX_JUMP_HEIGHT = abs(JUMP_STRENGTH) * abs(JUMP_STRENGTH) / (2 * GRAVITY) - 10
                MAX_JUMP_DISTANCE = PLAYER_SPEED * (2 * abs(JUMP_STRENGTH) / GRAVITY) * 0.9
                
                for platform in available_platforms:
                    platform_center_x = platform.x + platform.width // 2
                    platform_top_y = platform.y
                    
                    horizontal_distance = abs(platform_center_x - (x + 10))  # 10 is half power-up width
                    vertical_distance = platform_top_y - y
                    
                    # Check if reachable
                    if (horizontal_distance <= MAX_JUMP_DISTANCE and 
                        -50 <= vertical_distance <= MAX_JUMP_HEIGHT):
                        reachable = True
                        break
                
                if not reachable:
                    attempts += 1
                    continue
                
                # Check if position doesn't overlap with platforms or other power-ups
                power_up_rect = pygame.Rect(x - 10, y - 10, 40, 40)
                valid_position = True
                
                # Check platform overlaps
                for platform in self.platforms:
                    platform_rect = pygame.Rect(platform.x, platform.y, 
                                               platform.width, platform.height)
                    if power_up_rect.colliderect(platform_rect):
                        valid_position = False
                        break
                
                # Check other power-up overlaps
                if valid_position:
                    for existing_power_up in power_ups:
                        if (abs(existing_power_up.x - x) < 50 and 
                            abs(existing_power_up.y - y) < 50):
                            valid_position = False
                            break
                
                if valid_position:
                    power_ups.append(PowerUp(x, y))
                    placed = True
                
                attempts += 1
        
        # Method 3: If we still don't have enough power-ups, place them more liberally
        if len(power_ups) < 2:
            for _ in range(2 - len(power_ups)):
                # Just place them on random platforms without too many restrictions
                if available_platforms:
                    platform = random.choice(available_platforms)
                    power_up_x = random.randint(int(platform.x + 10), 
                                              int(platform.x + platform.width - 30))
                    power_up_y = platform.y - 25
                    
                    # Quick check to avoid placing on same spot
                    too_close = False
                    for existing_power_up in power_ups:
                        if (abs(existing_power_up.x - power_up_x) < 30 and 
                            abs(existing_power_up.y - power_up_y) < 30):
                            too_close = True
                            break
                    
                    if not too_close:
                        power_ups.append(PowerUp(power_up_x, power_up_y))
        
        return power_ups
    
    def add_particles(self, x, y, color, count=PARTICLE_COUNT):
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def add_camera_shake(self, intensity=5, duration=300):
        self.camera_shake = intensity
        self.camera_shake_duration = duration
    
    def load_music(self):
        """Load and start background music"""
        try:
            pygame.mixer.music.load("somegame_music.wav")
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            self.music_playing = True
            print("Music loaded and playing successfully!")
        except pygame.error as e:
            print(f"Could not load music file 'somegame_music.wav': {e}")
            print("Game will continue without music.")
            self.music_playing = False
    
    def toggle_music(self):
        """Toggle music on/off"""
        if self.music_playing:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                print("Music paused")
            else:
                pygame.mixer.music.unpause()
                print("Music resumed")
        else:
            # Try to reload and play music
            self.load_music()
    
    def adjust_volume(self, change):
        """Adjust music volume"""
        self.music_volume = max(0.0, min(1.0, self.music_volume + change))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"Music volume: {int(self.music_volume * 100)}%")
    
    def generate_random_platforms(self):
        platforms = []
        
        # Always add ground platform (grass type)
        ground_platform = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
        ground_platform.platform_type = 'grass'
        platforms.append(ground_platform)
        
        # Generate accessible platforms in layers
        self.generate_accessible_platforms(platforms)
        
        return platforms
    
    def generate_accessible_platforms(self, platforms):
        """Generate platforms that are guaranteed to be reachable"""
        # Define jumping constraints
        MAX_JUMP_HEIGHT = abs(JUMP_STRENGTH) * abs(JUMP_STRENGTH) / (2 * GRAVITY) - 20  # More conservative
        MAX_JUMP_DISTANCE = PLAYER_SPEED * (2 * abs(JUMP_STRENGTH) / GRAVITY) * 0.8  # More conservative
        
        # Create platforms in accessible layers
        current_layer_platforms = [platforms[0]]  # Start with ground platform
        
        for layer in range(3):  # Create 3 layers of platforms
            next_layer_platforms = []
            layer_height = SCREEN_HEIGHT - 150 - (layer * 100)  # Better spacing between layers
            
            # Ensure layer height is reasonable
            if layer_height < 80:
                break
                
            num_platforms_in_layer = random.randint(2, 4)  # Fewer platforms per layer to avoid crowding
            
            for i in range(num_platforms_in_layer):
                attempts = 0
                platform_created = False
                
                while attempts < 50 and not platform_created:  # More attempts
                    # Random platform properties
                    width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
                    height = random.randint(MIN_PLATFORM_HEIGHT, MAX_PLATFORM_HEIGHT)
                    
                    # Simple random positioning with bounds checking
                    margin = 50  # Minimum distance from screen edges
                    max_x = SCREEN_WIDTH - width - margin
                    min_x = margin
                    
                    # Ensure we have a valid range
                    if min_x >= max_x:
                        attempts += 1
                        continue
                    
                    x = random.randint(min_x, max_x)
                    
                    # Add some height variation within the layer
                    y_variation = random.randint(-20, 20)
                    y = max(50, min(SCREEN_HEIGHT - 100, layer_height + y_variation))
                    
                    # Check if platform is reachable from at least one platform in current layer
                    reachable = False
                    for source_platform in current_layer_platforms:
                        horizontal_distance = abs((source_platform.x + source_platform.width/2) - (x + width/2))
                        height_diff = source_platform.y - (y + height)
                        
                        if (horizontal_distance <= MAX_JUMP_DISTANCE and 
                            -30 <= height_diff <= MAX_JUMP_HEIGHT):
                            reachable = True
                            break
                    
                    if not reachable:
                        attempts += 1
                        continue
                    
                    # Check for overlaps with existing platforms (more strict)
                    new_rect = pygame.Rect(x - 20, y - 20, width + 40, height + 40)  # Larger buffer
                    valid_position = True
                    
                    for existing_platform in platforms:
                        existing_rect = pygame.Rect(existing_platform.x, existing_platform.y, 
                                                  existing_platform.width, existing_platform.height)
                        
                        if new_rect.colliderect(existing_rect):
                            valid_position = False
                            break
                    
                    # Also check against platforms being created in this layer
                    for existing_platform in next_layer_platforms:
                        existing_rect = pygame.Rect(existing_platform.x, existing_platform.y, 
                                                  existing_platform.width, existing_platform.height)
                        
                        if new_rect.colliderect(existing_rect):
                            valid_position = False
                            break
                    
                    if valid_position:
                        platform = Platform(x, y, width, height)
                        platforms.append(platform)
                        next_layer_platforms.append(platform)
                        platform_created = True
                    
                    attempts += 1
            
            # If no platforms were created in this layer, try to create at least one
            if not next_layer_platforms and layer < 2:  # Don't force on last layer
                # Create a guaranteed platform
                width = MIN_PLATFORM_WIDTH + 20
                height = MIN_PLATFORM_HEIGHT
                x = max(50, min(SCREEN_WIDTH - width - 50, SCREEN_WIDTH // 2 - width // 2))  # Center platform with bounds check
                y = layer_height
                
                # Make sure it doesn't overlap
                new_rect = pygame.Rect(x - 10, y - 10, width + 20, height + 20)
                valid_position = True
                
                for existing_platform in platforms:
                    existing_rect = pygame.Rect(existing_platform.x, existing_platform.y, 
                                              existing_platform.width, existing_platform.height)
                    if new_rect.colliderect(existing_rect):
                        valid_position = False
                        break
                
                if valid_position:
                    platform = Platform(x, y, width, height)
                    platforms.append(platform)
                    next_layer_platforms.append(platform)
            
            # If still no platforms, stop creating layers
            if not next_layer_platforms:
                break
                
            current_layer_platforms = next_layer_platforms
        
        # Add some additional floating platforms
        self.add_floating_platforms(platforms)
    
    def add_connecting_platforms(self, platforms):
        """Add platforms to connect isolated areas"""
        MAX_JUMP_HEIGHT = abs(JUMP_STRENGTH) * abs(JUMP_STRENGTH) / (2 * GRAVITY) - 20
        MAX_JUMP_DISTANCE = PLAYER_SPEED * (2 * abs(JUMP_STRENGTH) / GRAVITY) * 0.8
        
        # Find platform pairs that are almost reachable and add connecting platforms
        platform_pairs = []
        for i, platform1 in enumerate(platforms):
            for j, platform2 in enumerate(platforms[i+1:], i+1):
                horizontal_distance = abs((platform1.x + platform1.width/2) - (platform2.x + platform2.width/2))
                height_diff = abs(platform1.y - platform2.y)
                
                # If platforms are close but not quite reachable, they're candidates for connection
                if (MAX_JUMP_DISTANCE < horizontal_distance < MAX_JUMP_DISTANCE * 1.5 and
                    height_diff < MAX_JUMP_HEIGHT):
                    platform_pairs.append((platform1, platform2))
        
        # Add connecting platforms for some pairs
        if platform_pairs:
            num_connections = min(2, len(platform_pairs))
            selected_pairs = random.sample(platform_pairs, num_connections)
            
            for platform1, platform2 in selected_pairs:
                # Calculate midpoint
                mid_x = (platform1.x + platform1.width/2 + platform2.x + platform2.width/2) // 2
                mid_y = (platform1.y + platform2.y) // 2
                
                # Create connecting platform
                width = random.randint(60, 100)
                height = random.randint(15, 20)
                
                x = mid_x - width // 2
                y = mid_y - height // 2
                
                # Ensure it's within screen bounds
                x = max(10, min(SCREEN_WIDTH - width - 10, x))
                y = max(50, min(SCREEN_HEIGHT - 150, y))
                
                # Check if position is valid
                new_rect = pygame.Rect(x - 10, y - 10, width + 20, height + 20)
                valid_position = True
                
                for existing_platform in platforms:
                    existing_rect = pygame.Rect(existing_platform.x, existing_platform.y, 
                                              existing_platform.width, existing_platform.height)
                    if new_rect.colliderect(existing_rect):
                        valid_position = False
                        break
                
                if valid_position:
                    platform = Platform(x, y, width, height)
                    platforms.append(platform)
    
    def add_floating_platforms(self, platforms):
        """Add some floating platforms that are accessible"""
        MAX_JUMP_HEIGHT = abs(JUMP_STRENGTH) * abs(JUMP_STRENGTH) / (2 * GRAVITY) - 30
        MAX_JUMP_DISTANCE = PLAYER_SPEED * (2 * abs(JUMP_STRENGTH) / GRAVITY) * 0.7
        
        num_floating = random.randint(1, 3)  # Fewer floating platforms
        
        for _ in range(num_floating):
            attempts = 0
            while attempts < 30:  # More attempts
                # Random platform properties (smaller floating platforms)
                width = random.randint(50, 90)
                height = random.randint(15, 20)
                
                # Random position with proper bounds checking
                margin = 30
                max_x = SCREEN_WIDTH - width - margin
                min_x = margin
                
                if min_x >= max_x:
                    break  # Can't place platform, skip
                
                x = random.randint(min_x, max_x)
                y = random.randint(80, SCREEN_HEIGHT - 250)
                
                # Check if this platform is reachable from at least one existing platform
                reachable = False
                new_rect = pygame.Rect(x, y, width, height)
                
                for existing_platform in platforms:
                    # Calculate distance and height difference
                    horizontal_distance = abs(existing_platform.x + existing_platform.width/2 - (x + width/2))
                    height_diff = existing_platform.y - (y + height)
                    
                    # Check if reachable (more lenient for floating platforms)
                    if (horizontal_distance <= MAX_JUMP_DISTANCE and 
                        -40 <= height_diff <= MAX_JUMP_HEIGHT):
                        reachable = True
                        break
                
                if not reachable:
                    attempts += 1
                    continue
                
                # Check for overlaps (stricter)
                buffer_rect = pygame.Rect(x - 30, y - 30, width + 60, height + 60)
                valid_position = True
                
                for existing_platform in platforms:
                    existing_rect = pygame.Rect(existing_platform.x, existing_platform.y, 
                                              existing_platform.width, existing_platform.height)
                    
                    if buffer_rect.colliderect(existing_rect):
                        valid_position = False
                        break
                
                if valid_position:
                    platform = Platform(x, y, width, height)
                    platforms.append(platform)
                    break
                
                attempts += 1
    
    def generate_enemies(self):
        enemies = []
        
        # Place enemies on random platforms (excluding ground and very small platforms)
        available_platforms = [p for p in self.platforms 
                             if p.y < SCREEN_HEIGHT - 50 and p.width >= 80]
        
        if not available_platforms:
            return enemies
        
        num_enemies = random.randint(2, min(4, len(available_platforms)))
        selected_platforms = random.sample(available_platforms, min(num_enemies, len(available_platforms)))
        
        for platform in selected_platforms:
            # Place enemy on platform with some margin
            margin = 10
            if platform.width > margin * 2:
                enemy_x = random.randint(int(platform.x + margin), 
                                       int(platform.x + platform.width - margin - 30))
                enemy_y = platform.y - 30
                enemy = Enemy(enemy_x, enemy_y)
                
                # Adjust enemy position based on type
                if enemy.enemy_type == 'ghost':
                    enemy.y -= 10  # Ghosts float higher
                
                enemies.append(enemy)
        
        return enemies
    
    def generate_coins(self):
        coins = []
        
        # Define jumping constraints for coin reachability
        MAX_JUMP_HEIGHT = abs(JUMP_STRENGTH) * abs(JUMP_STRENGTH) / (2 * GRAVITY) - 10
        MAX_JUMP_DISTANCE = PLAYER_SPEED * (2 * abs(JUMP_STRENGTH) / GRAVITY) * 0.9
        
        # Place coins on platforms (guaranteed reachable)
        available_platforms = [p for p in self.platforms if p.y < SCREEN_HEIGHT - 50]
        
        for platform in available_platforms:
            if platform.width >= 50:  # Only place coins on platforms big enough
                # Place coin on platform surface
                coin_x = random.randint(int(platform.x + 10), 
                                      int(platform.x + platform.width - 26))
                coin_y = platform.y - 20
                coins.append(Coin(coin_x, coin_y))
        
        # Add floating coins that are reachable from existing platforms
        num_air_coins = random.randint(2, 4)
        for _ in range(num_air_coins):
            attempts = 0
            while attempts < 20:
                # Try to place coin in reachable position
                source_platform = random.choice(available_platforms)
                
                # Calculate reachable area from source platform
                base_x = source_platform.x + source_platform.width // 2
                base_y = source_platform.y
                
                # Random position within jumping range
                offset_x = random.randint(-int(MAX_JUMP_DISTANCE * 0.7), int(MAX_JUMP_DISTANCE * 0.7))
                offset_y = random.randint(-int(MAX_JUMP_HEIGHT * 0.8), int(MAX_JUMP_HEIGHT * 0.3))
                
                coin_x = base_x + offset_x
                coin_y = base_y + offset_y
                
                # Keep coin within screen bounds
                coin_x = max(20, min(SCREEN_WIDTH - 36, coin_x))
                coin_y = max(20, min(SCREEN_HEIGHT - 100, coin_y))
                
                # Verify coin is reachable from at least one platform
                reachable = False
                coin_rect = pygame.Rect(coin_x, coin_y, 16, 16)
                
                for platform in available_platforms:
                    # Check if coin is reachable from this platform
                    platform_center_x = platform.x + platform.width // 2
                    platform_top_y = platform.y
                    
                    horizontal_distance = abs(platform_center_x - (coin_x + 8))
                    vertical_distance = platform_top_y - coin_y
                    
                    # Check if within jumping range
                    if (horizontal_distance <= MAX_JUMP_DISTANCE and 
                        -30 <= vertical_distance <= MAX_JUMP_HEIGHT):
                        reachable = True
                        break
                
                if not reachable:
                    attempts += 1
                    continue
                
                # Make sure coin doesn't overlap with platforms
                valid_position = True
                for platform in self.platforms:
                    platform_rect = pygame.Rect(platform.x - 10, platform.y - 10, 
                                               platform.width + 20, platform.height + 20)
                    if coin_rect.colliderect(platform_rect):
                        valid_position = False
                        break
                
                # Make sure coin isn't too close to other coins
                for existing_coin in coins:
                    if abs(existing_coin.x - coin_x) < 30 and abs(existing_coin.y - coin_y) < 30:
                        valid_position = False
                        break
                
                if valid_position:
                    coins.append(Coin(coin_x, coin_y))
                    break
                    
                attempts += 1
        
        # Add bonus coins in strategic locations (optional)
        self.add_bonus_coins(coins, available_platforms, MAX_JUMP_HEIGHT, MAX_JUMP_DISTANCE)
        
        return coins

    def add_bonus_coins(self, coins, platforms, max_jump_height, max_jump_distance):
        """Add bonus coins in challenging but reachable locations"""
        num_bonus = random.randint(1, 2)
        
        for _ in range(num_bonus):
            attempts = 0
            while attempts < 15:
                # Find two platforms that are connected (player can jump between them)
                if len(platforms) < 2:
                    break
                    
                platform1 = random.choice(platforms)
                platform2 = random.choice(platforms)
                
                if platform1 == platform2:
                    attempts += 1
                    continue
                
                # Check if platforms are within jumping distance
                horizontal_gap = abs((platform1.x + platform1.width//2) - (platform2.x + platform2.width//2))
                vertical_gap = abs(platform1.y - platform2.y)
                
                if horizontal_gap <= max_jump_distance and vertical_gap <= max_jump_height:
                    # Place coin between the platforms
                    mid_x = (platform1.x + platform1.width//2 + platform2.x + platform2.width//2) // 2
                    mid_y = min(platform1.y, platform2.y) - random.randint(20, 40)
                    
                    # Ensure coin is within screen bounds
                    mid_x = max(20, min(SCREEN_WIDTH - 36, mid_x))
                    mid_y = max(20, min(SCREEN_HEIGHT - 100, mid_y))
                    
                    # Check if position is valid (not overlapping with platforms)
                    coin_rect = pygame.Rect(mid_x, mid_y, 16, 16)
                    valid_position = True
                    
                    for platform in self.platforms:
                        platform_rect = pygame.Rect(platform.x - 10, platform.y - 10, 
                                                   platform.width + 20, platform.height + 20)
                        if coin_rect.colliderect(platform_rect):
                            valid_position = False
                            break
                    
                    # Check distance from existing coins
                    for existing_coin in coins:
                        if abs(existing_coin.x - mid_x) < 40 and abs(existing_coin.y - mid_y) < 40:
                            valid_position = False
                            break
                    
                    if valid_position:
                        coins.append(Coin(mid_x, mid_y))
                        break
                
                attempts += 1

    def check_win_condition(self):
        """Check if all coins have been collected"""
        all_collected = True
        for coin in self.coins:
            if not coin.collected:
                all_collected = False
                break
        
        if all_collected and not self.game_won:
            self.game_won = True
            self.win_time = pygame.time.get_ticks()
            self.play_win_sound()  # Play win sound
            print("Congratulations! You collected all coins!")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:  # Press R to regenerate level
                    if self.game_won or self.game_over:
                        # Reset game state
                        self.game_won = False
                        self.game_over = False
                        self.win_time = 0
                        self.lives = 3  # Reset lives
                        self.invulnerable = False
                        self.combo_multiplier = 1
                        self.combo_timer = 0
                    self.regenerate_level()
                elif event.key == pygame.K_m:  # Press M to toggle music
                    self.toggle_music()
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # Press + to increase volume
                    self.adjust_volume(0.1)
                elif event.key == pygame.K_MINUS:  # Press - to decrease volume
                    self.adjust_volume(-0.1)
                elif event.key == pygame.K_RETURN and (self.game_won or self.game_over):  # Press Enter to play again
                    self.game_won = False
                    self.game_over = False
                    self.win_time = 0
                    self.lives = 3  # Reset lives
                    self.invulnerable = False
                    self.combo_multiplier = 1
                    self.combo_timer = 0
                    self.regenerate_level()
        return True
    
    def regenerate_level(self):
        """Regenerate the entire level with new random platforms"""
        self.platforms = self.generate_random_platforms()
        self.enemies = self.generate_enemies()
        self.coins = self.generate_coins()
        self.power_ups = self.generate_power_ups()
        
        # Reset player position
        self.player.x = 100
        self.player.y = 400
        self.player.vel_x = 0
        self.player.vel_y = 0
        
        # Clear particles
        self.particles = []
        
        # Reset score and timers if starting new game
        if self.game_won or self.game_over:
            self.score = 0
            self.start_time = pygame.time.get_ticks()
            self.countdown_start_time = pygame.time.get_ticks()  # Reset countdown timer
            self.time_warning_played = False
            
        # Reset invulnerability when regenerating level
        self.invulnerable = False
        self.invulnerable_time = 0
    
    def draw_win_screen(self):
        """Draw the victory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Victory messages
        win_font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 48)
        instruction_font = pygame.font.Font(None, 36)
        
        # Main victory text
        win_text = win_font.render("VICTORY!", True, YELLOW)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(win_text, win_rect)
        
        # Congratulations text
        congrats_text = score_font.render("All Coins Collected!", True, WHITE)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(congrats_text, congrats_rect)
        
        # Final score
        final_score_text = score_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(final_score_text, score_rect)
        
        # Calculate completion time correctly
        completion_time = (self.win_time - self.start_time) // 1000
        time_text = instruction_font.render(f"Completion Time: {completion_time}s", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(time_text, time_rect)
        
        # Instructions
        instructions = [
            "Press ENTER to Play Again",
            "Press R to Generate New Level",
            "Press ESC to Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120 + i * 40))
            self.screen.blit(text, text_rect)
    
    def draw_game_over_screen(self):
        """Draw the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over messages
        game_over_font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 48)
        instruction_font = pygame.font.Font(None, 36)
        
        # Main game over text
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Show reason for game over
        remaining_time = self.get_remaining_time()
        if remaining_time <= 0:
            reason_text = score_font.render("Time's Up!", True, WHITE)
        else:
            reason_text = score_font.render("No Lives Remaining!", True, WHITE)
        reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(reason_text, reason_rect)
        
        # Final score
        final_score_text = score_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)
        
        # Coins collected
        coins_collected = sum(1 for coin in self.coins if coin.collected)
        total_coins = len(self.coins)
        coins_text = instruction_font.render(f"Coins Collected: {coins_collected}/{total_coins}", True, WHITE)
        coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(coins_text, coins_rect)
        
        # Instructions
        instructions = [
            "Press ENTER to Play Again",
            "Press R to Generate New Level",
            "Press ESC to Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100 + i * 40))
            self.screen.blit(text, text_rect)

    def draw_lives(self):
        """Draw lives as heart icons"""
        heart_size = 20
        heart_spacing = 25
        start_x = SCREEN_WIDTH - (self.lives * heart_spacing + 20)
        start_y = 10
        
        for i in range(self.lives):
            heart_x = start_x + i * heart_spacing
            heart_y = start_y
            
            # Draw heart shape
            # Heart is made of two circles and a triangle
            pygame.draw.circle(self.screen, RED, (heart_x + 5, heart_y + 5), 5)
            pygame.draw.circle(self.screen, RED, (heart_x + 15, heart_y + 5), 5)
            
            # Triangle for bottom of heart
            heart_points = [
                (heart_x, heart_y + 8),
                (heart_x + 20, heart_y + 8),
                (heart_x + 10, heart_y + 18)
            ]
            pygame.draw.polygon(self.screen, RED, heart_points)
            
            # Heart outline
            pygame.draw.circle(self.screen, (139, 0, 0), (heart_x + 5, heart_y + 5), 5, 2)
            pygame.draw.circle(self.screen, (139, 0, 0), (heart_x + 15, heart_y + 5), 5, 2)
            pygame.draw.polygon(self.screen, (139, 0, 0), heart_points, 2)

    def update(self):
        if not self.game_won and not self.game_over:
            # Check countdown timer
            remaining_time = self.get_remaining_time()
            
            # Play warning sound at 30 seconds (if sound is available)
            if remaining_time <= 30 and remaining_time > 29 and not self.time_warning_played:
                self.time_warning_played = True
                # You could add a warning sound here if you have one
                print("Warning: 30 seconds remaining!")
            
            # Game over when time runs out
            if remaining_time <= 0:
                self.game_over = True
                self.play_lose_sound()
                print("Time's up! Game Over!")
                return
            
            self.player.update(self.platforms)
            
            # Update camera shake
            if self.camera_shake_duration > 0:
                self.camera_shake_duration -= 1000 / FPS
                if self.camera_shake_duration <= 0:
                    self.camera_shake = 0
            
            # Update invulnerability
            if self.invulnerable:
                if pygame.time.get_ticks() - self.invulnerable_time > self.invulnerable_duration:
                    self.invulnerable = False
            
            # Update combo timer
            if self.combo_timer > 0:
                self.combo_timer -= 1000 / FPS
                if self.combo_timer <= 0:
                    self.combo_multiplier = 1
            
            # Update enemies
            for enemy in self.enemies:
                enemy.update(self.platforms)
                
            # Update coins
            for coin in self.coins:
                coin.update()
                
            # Update power-ups
            for power_up in self.power_ups:
                power_up.update()
                
            # Update particles
            self.particles = [p for p in self.particles if p.life > 0]
            for particle in self.particles:
                particle.update()
                
            # Check collisions
            self.check_collisions()
            
            # Check win condition
            self.check_win_condition()
    
    def check_collisions(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        # Player vs enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if player_rect.colliderect(enemy_rect):
                    # Special case for spiky enemies - player always dies when touching them
                    if enemy.enemy_type == 'spiky':
                        # Player hit by spiky enemy - always lose a life if not invulnerable
                        if not self.invulnerable and not self.player.invincible_power:
                            # Extra camera shake for spiky enemy (more dangerous)
                            self.add_camera_shake(8, 500)
                            self.lose_life()
                    else:
                        # For other enemies, check if player is jumping on them
                        if self.player.vel_y > 0 and self.player.y < enemy.y:
                            enemy.alive = False
                            self.player.vel_y = JUMP_STRENGTH // 2  # Small bounce
                            
                            # Enhanced scoring with combo system
                            points = 100 * self.combo_multiplier
                            self.score += points
                            self.combo_multiplier = min(5, self.combo_multiplier + 1)
                            self.combo_timer = 3000  # 3 seconds to maintain combo
                            
                            # Add particles
                            self.add_particles(enemy.x + enemy.width//2, enemy.y + enemy.height//2, 
                                             YELLOW, 15)
                            
                            # Camera shake
                            self.add_camera_shake(3, 200)
                            
                        else:
                            # Player hit by enemy - lose a life if not invulnerable
                            if not self.invulnerable and not self.player.invincible_power:
                                self.lose_life()
        
        # Player vs coins (with magnet effect)
        for coin in self.coins:
            if not coin.collected:
                coin_rect = pygame.Rect(coin.x, coin.y, coin.width, coin.height)
                
                # Magnet effect
                if self.player.magnet_power:
                    distance = math.sqrt((coin.x - self.player.x)**2 + (coin.y - self.player.y)**2)
                    if distance < 100:  # Magnet range
                        # Pull coin towards player
                        dx = self.player.x - coin.x
                        dy = self.player.y - coin.y
                        coin.x += dx * 0.1
                        coin.y += dy * 0.1
                
                if player_rect.colliderect(coin_rect):
                    coin.collected = True
                    points = 50 * self.combo_multiplier
                    self.score += points
                    
                    # Add coin particles
                    self.add_particles(coin.x + coin.width//2, coin.y + coin.height//2, 
                                     YELLOW, 10)
        
        # Player vs power-ups
        for power_up in self.power_ups:
            if not power_up.collected:
                power_up_rect = pygame.Rect(power_up.x, power_up.y, power_up.width, power_up.height)
                if player_rect.colliderect(power_up_rect):
                    power_up.collected = True
                    self.player.apply_power_up(power_up.power_type, power_up.effect_duration)
                    self.score += 200
                    
                    # Add power-up particles
                    self.add_particles(power_up.x + power_up.width//2, power_up.y + power_up.height//2, 
                                     power_up.color, 20)
                    
                    # Camera shake for power-up
                    self.add_camera_shake(4, 250)
    
    def lose_life(self):
        """Handle losing a life"""
        self.lives -= 1
        print(f"Life lost! Lives remaining: {self.lives}")
        
        # Reset player position
        spawn_x = 100
        spawn_y = 400
        self.player.x = spawn_x
        self.player.y = spawn_y
        self.player.vel_x = 0
        self.player.vel_y = 0
        
        # Add red particle effect at spawn point every time player dies
        self.add_particles(spawn_x + self.player.width//2, 
                         spawn_y + self.player.height//2, RED, 25)
        
        # Camera shake for respawn
        self.add_camera_shake(6, 400)
        
        if self.lives <= 0:
            self.game_over = True
            self.play_lose_sound()  # Play lose sound
            print("Game Over!")
        else:
            # Make invulnerable temporarily
            self.invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()
    
    def draw_background(self):
        """Draw a beautiful background"""
        # Create a gradient sky background
        for y in range(SCREEN_HEIGHT):
            # Create gradient from light blue at top to lighter blue at bottom
            ratio = y / SCREEN_HEIGHT
            
            # Sky colors - from dark blue at top to light blue at bottom
            top_color = (135, 206, 250)    # Light sky blue
            bottom_color = (173, 216, 230)  # Light blue
            
            # Interpolate between colors
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw clouds
        self.draw_clouds()
        
        # Draw distant mountains
        self.draw_mountains()
        
        # Draw sun
        self.draw_sun()
    
    def draw_clouds(self):
        """Draw fluffy clouds in the background"""
        cloud_color = (255, 255, 255, 180)  # Semi-transparent white
        
        # Create cloud positions (static for consistency)
        cloud_positions = [
            (100, 80, 60),   # x, y, size
            (300, 50, 80),
            (500, 90, 70),
            (650, 60, 50),
            (150, 150, 40),
            (400, 120, 55),
            (700, 140, 65)
        ]
        
        for cloud_x, cloud_y, cloud_size in cloud_positions:
            # Draw multiple overlapping circles to create cloud shape
            for i in range(5):
                offset_x = (i - 2) * (cloud_size // 4)
                offset_y = random.randint(-cloud_size//6, cloud_size//6)
                radius = cloud_size // 2 + random.randint(-5, 5)
                
                # Main cloud body
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (cloud_x + offset_x, cloud_y + offset_y), radius)
                
                # Cloud highlight
                pygame.draw.circle(self.screen, (240, 248, 255), 
                                 (cloud_x + offset_x - 3, cloud_y + offset_y - 3), radius - 5)
    
    def draw_mountains(self):
        """Draw distant mountains"""
        mountain_color = (119, 136, 153)  # Light slate gray
        mountain_dark = (105, 105, 105)   # Dim gray
        
        # Back mountains (darker, further)
        back_mountain_points = [
            (0, SCREEN_HEIGHT - 200),
            (150, SCREEN_HEIGHT - 300),
            (300, SCREEN_HEIGHT - 250),
            (450, SCREEN_HEIGHT - 320),
            (600, SCREEN_HEIGHT - 280),
            (SCREEN_WIDTH, SCREEN_HEIGHT - 220),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, SCREEN_HEIGHT)
        ]
        pygame.draw.polygon(self.screen, mountain_dark, back_mountain_points)
        
        # Front mountains (lighter, closer)
        front_mountain_points = [
            (0, SCREEN_HEIGHT - 150),
            (100, SCREEN_HEIGHT - 200),
            (250, SCREEN_HEIGHT - 180),
            (400, SCREEN_HEIGHT - 240),
            (550, SCREEN_HEIGHT - 190),
            (700, SCREEN_HEIGHT - 210),
            (SCREEN_WIDTH, SCREEN_HEIGHT - 160),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, SCREEN_HEIGHT)
        ]
        pygame.draw.polygon(self.screen, mountain_color, front_mountain_points)
        
        # Add snow caps on peaks
        snow_color = (255, 250, 250)  # Snow white
        snow_peaks = [
            (150, SCREEN_HEIGHT - 300, 20),  # x, y, width
            (450, SCREEN_HEIGHT - 320, 25),
            (400, SCREEN_HEIGHT - 240, 15),
            (700, SCREEN_HEIGHT - 210, 18)
        ]
        
        for peak_x, peak_y, width in snow_peaks:
            snow_points = [
                (peak_x - width, peak_y + 20),
                (peak_x, peak_y),
                (peak_x + width, peak_y + 20)
            ]
            pygame.draw.polygon(self.screen, snow_color, snow_points)
    
    def draw_sun(self):
        """Draw a bright sun"""
        sun_x = SCREEN_WIDTH - 100
        sun_y = 80
        sun_radius = 30
        
        # Sun rays
        ray_color = (255, 255, 0, 100)  # Semi-transparent yellow
        for angle in range(0, 360, 30):
            ray_angle = math.radians(angle)
            start_x = sun_x + math.cos(ray_angle) * (sun_radius + 5)
            start_y = sun_y + math.sin(ray_angle) * (sun_radius + 5)
            end_x = sun_x + math.cos(ray_angle) * (sun_radius + 20)
            end_y = sun_y + math.sin(ray_angle) * (sun_radius + 20)
            
            pygame.draw.line(self.screen, (255, 255, 0), 
                           (start_x, start_y), (end_x, end_y), 3)
        
        # Sun body with gradient effect
        for radius in range(sun_radius, 0, -2):
            alpha = 255 - (sun_radius - radius) * 8
            color_intensity = 255 - (sun_radius - radius) * 3
            sun_color = (255, color_intensity, 0)
            pygame.draw.circle(self.screen, sun_color, (sun_x, sun_y), radius)
        
        # Sun highlight
        pygame.draw.circle(self.screen, (255, 255, 200), 
                         (sun_x - 8, sun_y - 8), 8)

    def draw(self):
        # Calculate camera offset for shake effect
        shake_x = random.randint(-self.camera_shake, self.camera_shake) if self.camera_shake > 0 else 0
        shake_y = random.randint(-self.camera_shake, self.camera_shake) if self.camera_shake > 0 else 0
        
        # Draw background
        self.draw_background()
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
            
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen)
            
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Draw player (with flashing effect if invulnerable)
        if self.invulnerable:
            # Flash player by only drawing every few frames
            flash_rate = 200  # milliseconds
            if (pygame.time.get_ticks() // flash_rate) % 2 == 0:
                self.player.draw(self.screen)
        else:
            self.player.draw(self.screen)
        
        # Enhanced UI
        self.draw_enhanced_ui()
        
        # Draw win screen if game is won
        if self.game_won:
            self.draw_win_screen()
        
        # Draw game over screen if game is over
        if self.game_over:
            self.draw_game_over_screen()
        
        pygame.display.flip()
    
    def draw_enhanced_ui(self):
        # Score with combo multiplier
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        if self.combo_multiplier > 1:
            combo_text = self.small_font.render(f"Combo x{self.combo_multiplier}!", True, ORANGE)
            self.screen.blit(combo_text, (10, 45))
        
        # Level indicator
        level_text = self.small_font.render(f"Level: {self.level}", True, BLACK)
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, 10))
        
        # Draw countdown timer
        remaining_time = self.get_remaining_time()
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        
        # Change color based on remaining time
        if remaining_time <= 30:
            timer_color = RED  # Red when time is running out
        elif remaining_time <= 60:
            timer_color = ORANGE  # Orange when getting low
        else:
            timer_color = BLACK  # Normal color
        
        timer_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, timer_color)
        timer_rect = timer_text.get_rect()
        timer_rect.centerx = SCREEN_WIDTH // 2
        timer_rect.y = 10
        self.screen.blit(timer_text, timer_rect)
        
        # Add flashing effect when time is very low (last 10 seconds)
        if remaining_time <= 10 and remaining_time > 0:
            if int(remaining_time * 2) % 2 == 0:  # Flash every half second
                warning_text = self.small_font.render("TIME RUNNING OUT!", True, RED)
                warning_rect = warning_text.get_rect()
                warning_rect.centerx = SCREEN_WIDTH // 2
                warning_rect.y = 50
                self.screen.blit(warning_text, warning_rect)
        
        # Draw lives
        self.draw_lives()
        
        # Draw coins remaining
        coins_remaining = sum(1 for coin in self.coins if not coin.collected)
        coins_text = self.small_font.render(f"Coins: {coins_remaining}", True, BLACK)
        self.screen.blit(coins_text, (10, 70))
        
        # Power-up status indicators
        y_offset = 95
        if self.player.speed_boost:
            speed_text = self.small_font.render("SPEED BOOST!", True, ORANGE)
            self.screen.blit(speed_text, (10, y_offset))
            y_offset += 20
        
        if self.player.jump_boost:
            jump_text = self.small_font.render("SUPER JUMP!", True, GREEN)
            self.screen.blit(jump_text, (10, y_offset))
            y_offset += 20
        
        if self.player.invincible_power:
            invincible_text = self.small_font.render("INVINCIBLE!", True, PURPLE)
            self.screen.blit(invincible_text, (10, y_offset))
            y_offset += 20
        
        if self.player.magnet_power:
            magnet_text = self.small_font.render("COIN MAGNET!", True, CYAN)
            self.screen.blit(magnet_text, (10, y_offset))
            y_offset += 20
        
        # Music status
        music_status = "ON" if (self.music_playing and pygame.mixer.music.get_busy()) else "OFF"
        music_text = self.small_font.render(f"Music: {music_status}", True, BLACK)
        self.screen.blit(music_text, (10, y_offset))
        
        # Instructions (condensed)
        if not self.game_won and not self.game_over:
            instructions = [
                "WASD/Arrows: Move | Space: Jump | R: New Level | M: Music | ESC: Quit"
            ]
            
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 20).render(instruction, True, BLACK)
                self.screen.blit(text, (10, SCREEN_HEIGHT - 30 + i * 20))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        # Stop music when game ends
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()

    def load_sound_effects(self):
        """Load sound effects for win and lose"""
        try:
            self.win_sound = pygame.mixer.Sound("win.wav")
            print("Win sound loaded successfully!")
        except pygame.error as e:
            print(f"Could not load win sound 'win.wav': {e}")
            self.win_sound = None
            
        try:
            self.lose_sound = pygame.mixer.Sound("lose.ogg")
            print("Lose sound loaded successfully!")
        except pygame.error as e:
            print(f"Could not load lose sound 'lose.ogg': {e}")
            self.lose_sound = None

    def play_win_sound(self):
        """Play the win sound effect"""
        if self.win_sound:
            try:
                self.win_sound.play()
            except pygame.error as e:
                print(f"Error playing win sound: {e}")

    def play_lose_sound(self):
        """Play the lose sound effect"""
        if self.lose_sound:
            try:
                self.lose_sound.play()
            except pygame.error as e:
                print(f"Error playing lose sound: {e}")

    def get_remaining_time(self):
        """Get remaining time in seconds"""
        elapsed_time = (pygame.time.get_ticks() - self.countdown_start_time) / 1000
        remaining_time = max(0, self.countdown_duration - elapsed_time)
        return remaining_time

if __name__ == "__main__":
    game = Game()
    game.run()
