import pygame
import numpy as np
import tkinter as tk
from tkinter import ttk

# Constants
G = 1  # Gravitational constant (normalized for simplicity)
dt = 0.01  # Time step
num_steps = 1000  # Number of simulation steps
WIDTH, HEIGHT = 800, 600
SCALE = 100  # Scaling factor for better visualization

# Default Initial Conditions
bodies = [
    {'mass': 0.4, 'pos': np.array([-1.0, 0.0]), 'vel': np.array([0.0, -1.5]), 'color': (255, 0, 0)},
    {'mass': 1.9, 'pos': np.array([1.0, 0.0]), 'vel': np.array([0.0, 1.0]), 'color': (0, 255, 0)},
    {'mass': 2.0, 'pos': np.array([0.0, 0.0]), 'vel': np.array([1.0, 0.0]), 'color': (0, 0, 255)}
]

def compute_accelerations(bodies):
    n = len(bodies)
    accelerations = [np.zeros(2) for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                r = bodies[j]['pos'] - bodies[i]['pos']
                distance = np.linalg.norm(r)
                if distance > 0:
                    force = G * bodies[j]['mass'] / distance**3 * r
                    accelerations[i] += force
    return accelerations

def update_positions(bodies, dt):
    accels = compute_accelerations(bodies)
    for i, body in enumerate(bodies):
        body['vel'] += accels[i] * dt
        body['pos'] += body['vel'] * dt
    return bodies

def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    
    trails = [[] for _ in bodies]
    
    while running:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        update_positions(bodies, dt)
        
        for i, body in enumerate(bodies):
            x, y = body['pos'] * SCALE + np.array([WIDTH / 2, HEIGHT / 2])
            radius = int(body['mass'] * 5)  # Mass-based size scaling
            pygame.draw.circle(screen, body['color'], (int(x), int(y)), radius)
            trails[i].append((int(x), int(y)))
            if len(trails[i]) > 100:
                trails[i].pop(0)
            
            # Fade-out effect for trails
            for j, trail_pos in enumerate(trails[i]):
                alpha = int(255 * (j / len(trails[i])))  # Gradual fade
                trail_color = tuple(min(255, c + 100) for c in body['color'])  # Brighter trail color
                pygame.draw.circle(screen, trail_color, trail_pos, 2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def create_gui():
    root = tk.Tk()
    root.title("Three-Body Problem Simulation")
    
    ttk.Label(root, text="Initial Conditions:").grid(row=0, column=0, columnspan=4)
    
    for i, body in enumerate(bodies):
        ttk.Label(root, text=f"Body {i+1} Mass:").grid(row=i+1, column=0)
        mass_entry = ttk.Entry(root)
        mass_entry.insert(0, str(body['mass']))
        mass_entry.grid(row=i+1, column=1)
        
        ttk.Label(root, text=f"Pos (x, y):").grid(row=i+1, column=2)
        pos_entry = ttk.Entry(root)
        pos_entry.insert(0, f"{body['pos'][0]}, {body['pos'][1]}")
        pos_entry.grid(row=i+1, column=3)
        
        ttk.Label(root, text=f"Vel (vx, vy):").grid(row=i+1, column=4)
        vel_entry = ttk.Entry(root)
        vel_entry.insert(0, f"{body['vel'][0]}, {body['vel'][1]}")
        vel_entry.grid(row=i+1, column=5)
    
    start_button = ttk.Button(root, text="Start Simulation", command=run_simulation)
    start_button.grid(row=len(bodies) + 1, column=0, columnspan=6)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
