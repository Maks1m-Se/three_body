import pygame
import numpy as np
import tkinter as tk
from tkinter import ttk
import pygame.gfxdraw

# Constants
G = 1  # Gravitational constant (normalized for simplicity)
dt = 0.01  # Time step for numerical integration
num_steps = 1000  # Number of simulation steps
WIDTH, HEIGHT = 1000, 800  # Screen dimensions
SCALE = 100  # Scaling factor to visualize position values in pixels

# UI Controls
paused = False
speed_multiplier = 1.0  # Speed control factor
button_font = None

# Load Background Image
pygame.init()
BACKGROUND_IMAGE = pygame.image.load("assets/background/space.jpeg")
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = BACKGROUND_IMAGE.get_size()
background_x, background_y = 0, 0  # Initial position for moving background
background_speed_x = 0.1  # Slow diagonal movement speed
background_speed_y = 0.02  # Slow diagonal movement speed
max_body_speed = 8

# Load and Play Background Music
pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/epiano.mp3")
pygame.mixer.music.play(-1)  # Loop music indefinitely
pygame.mixer.music.set_volume(.7)

# Default Initial Conditions - Slightly Unstable System
def default_bodies():
    return [
        {'mass': 1.0, 'pos': np.array([-1.02, 0.25]), 'vel': np.array([0.47, 0.42]), 'color': (255, 0, 0)},
        {'mass': .4, 'pos': np.array([2.01, -0.24]), 'vel': np.array([-0.8, .85]), 'color': (0, 255, 0)},
        {'mass': 2.0, 'pos': np.array([0.0, 0.0]), 'vel': np.array([-0.92, -0.97]), 'color': (0, 0, 255)}
    ]

bodies = default_bodies()
trails = [[] for _ in bodies]  # Restore trails
max_trail_length = 3000  # Controls how long the trails remain visible

def compute_accelerations(bodies):
    """Computes gravitational acceleration for each body due to all other bodies."""
    n = len(bodies)
    accelerations = [np.zeros(2) for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                r = bodies[j]['pos'] - bodies[i]['pos']  # Vector from body[i] to body[j]
                distance = np.linalg.norm(r)  # Euclidean distance
                if distance > 0:
                    force = G * bodies[j]['mass'] / distance**3 * r  # Newton's law of gravity (normalized)
                    accelerations[i] += force
    return accelerations

def update_positions(bodies, dt):
    """Updates positions and velocities using the Euler method."""
    accels = compute_accelerations(bodies)
    for i, body in enumerate(bodies):
        body['vel'] += accels[i] * dt * speed_multiplier  # Adjust simulation speed
        
        # Speed control
        if body['vel'][0] > max_body_speed:
            print(f"body {i} vel x: {body['vel'][0]}")
            print('SPEED CONTROL')
            body['vel'][0] = max_body_speed     
        if body['vel'][1] > max_body_speed:
            print(f"body {i} vel y: {body['vel'][1]}")
            print('SPEED CONTROL')
            body['vel'][1] = max_body_speed
        if body['vel'][0] < -max_body_speed:
            print(f"body {i} vel x: {body['vel'][0]}")
            print('SPEED CONTROL')
            body['vel'][0] = -max_body_speed
        if body['vel'][1] < -max_body_speed:
            print(f"body {i} vel y: {body['vel'][1]}")
            print('SPEED CONTROL')
            body['vel'][1] = -max_body_speed

        print(f"body {i} vel x,y:", body['vel'] ) ### Debugging
        body['pos'] += body['vel'] * dt * speed_multiplier
    return bodies

def toggle_pause():
    """Toggles the simulation pause state."""
    global paused
    paused = not paused

def adjust_speed(factor):
    """Adjusts the simulation speed multiplier."""
    global speed_multiplier
    speed_multiplier += factor
    #speed_multiplier = max(0.1, min(speed_multiplier * factor, 10))  # Keep speed within reasonable bounds

def reset_simulation():
    """Resets the simulation to the default initial conditions."""
    global bodies, paused, speed_multiplier, trails
    bodies = default_bodies()
    paused = False
    speed_multiplier = 1.0
    trails = [[] for _ in bodies]  # Reset trails

def get_center_of_mass():
    """Computes the center of mass of the system to keep it centered in the view."""
    total_mass = sum(body['mass'] for body in bodies)
    center_of_mass = sum(body['pos'] * body['mass'] for body in bodies) / total_mass
    return center_of_mass

def run_simulation():
    """Runs the simulation loop using Pygame to visualize motion and add UI controls."""
    global button_font, background_x, background_y
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    button_font = pygame.font.Font(None, 25) 
    running = True
    
    while running:
        # Move background diagonally
        background_x = (background_x + background_speed_x) % BACKGROUND_WIDTH
        background_y = (background_y + background_speed_y) % BACKGROUND_HEIGHT
        
        for x_offset in range(0, WIDTH, BACKGROUND_WIDTH):
            for y_offset in range(0, HEIGHT, BACKGROUND_HEIGHT):
                screen.blit(BACKGROUND_IMAGE, (x_offset - background_x, y_offset - background_y))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Allow the user to close the window
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 10 <= mx <= 110 and 700 <= my <= 730:  # Fix button click areas
                    toggle_pause()
                elif 130 <= mx <= 180 and 700 <= my <= 730:
                    adjust_speed(1.1)
                elif 190 <= mx <= 240 and 700 <= my <= 730:
                    adjust_speed(0.9)
                elif 260 <= mx <= 360 and 700 <= my <= 730:
                    reset_simulation()

        
        if not paused:
            update_positions(bodies, dt)  # Update the positions of the bodies
        
        center_of_mass = get_center_of_mass()
        
        for i, body in enumerate(bodies):
            pos_adjusted = (body['pos'] - center_of_mass) * SCALE + np.array([WIDTH / 2, HEIGHT / 2])
            x, y = int(pos_adjusted[0]), int(pos_adjusted[1])
            radius = int(body['mass'] * 5)  # Scale the size of the body based on its mass
            
            
            #draw trails
            trails[i].append((x, y))
            if len(trails[i]) > max_trail_length:
                trails[i].pop(0)
            for j, trail_pos in enumerate(trails[i]):
                fade_factor = j / len(trails[i])
                trail_color = tuple(int(c * fade_factor)*0.3 for c in body['color'])
                pygame.gfxdraw.filled_circle(screen, trail_pos[0], trail_pos[1], 1, trail_color)

            #draw bodies
            pygame.gfxdraw.filled_circle(screen, x, y, radius, body['color'])
            pygame.gfxdraw.aacircle(screen, x, y, radius, body['color'])



        # UI Buttons
        button_color = (50, 50, 150)  # Dark blue
        hover_color = (70, 70, 200)  # Brighter blue on hover
        text_color = (255, 255, 255)  # White text

        # Button positions
        buttons = [
            {"rect": pygame.Rect(10, HEIGHT-50, 70, 30), "label": "Pause", "action": toggle_pause},
            {"rect": pygame.Rect(100, HEIGHT-50, 70, 30), "label": "Reset", "action": reset_simulation},
            {"rect": pygame.Rect(200, HEIGHT-50, 30, 30), "label": "+", "action": lambda: adjust_speed(0.1)},
            {"rect": pygame.Rect(240, HEIGHT-50, 30, 30), "label": "-", "action": lambda: adjust_speed(-0.1)},
            
        ]

        # Handle button clicks
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        button["action"]()

        # Draw buttons
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in buttons:
            rect = button["rect"]
            color = hover_color if rect.collidepoint(mouse_x, mouse_y) else button_color  # Highlight on hover
            pygame.draw.rect(screen, color, rect, border_radius=10)  # Rounded corners
            label_surface = button_font.render(button["label"], True, text_color)
            screen.blit(label_surface, (rect.x + 10, rect.y + 5))  # Center text

        # Display the speed multiplier value next to + and - buttons
        speed_text = button_font.render(f"x{speed_multiplier:.1f}", True, text_color)  # Format with 1 decimal
        screen.blit(speed_text, (280, HEIGHT - 45))  # Position next to '-' button

        

        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    run_simulation()
