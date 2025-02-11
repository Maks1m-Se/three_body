import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk
import pandas as pd

# Constants
G = 1  # Gravitational constant (normalized for simplicity)
dt = 0.01  # Time step
num_steps = 1000  # Number of simulation steps

# Default Initial Conditions
bodies = [
    {'mass': 1.0, 'pos': np.array([-1.0, 0.0]), 'vel': np.array([0.0, -1.0])},
    {'mass': 1.0, 'pos': np.array([1.0, 0.0]), 'vel': np.array([0.0, 1.0])},
    {'mass': 1.0, 'pos': np.array([0.0, 0.0]), 'vel': np.array([1.0, 0.0])}
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

def simulate():
    global bodies
    positions = [[] for _ in bodies]
    for _ in range(num_steps):
        bodies = update_positions(bodies, dt)
        for i, body in enumerate(bodies):
            positions[i].append(body['pos'].copy())
    return positions

def animate(i, scatters, positions):
    for scatter, pos in zip(scatters, positions):
        scatter.set_offsets(pos[i])
    return scatters

def start_simulation():
    positions = simulate()
    fig, ax = plt.subplots()
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_facecolor('black')
    
    scatters = [ax.scatter([], [], s=50, c='red', edgecolors='white') for _ in positions]
    ani = animation.FuncAnimation(fig, animate, frames=num_steps, fargs=(scatters, positions), interval=20, blit=False)
    plt.show()

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
    
    start_button = ttk.Button(root, text="Start Simulation", command=start_simulation)
    start_button.grid(row=len(bodies) + 1, column=0, columnspan=6)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
