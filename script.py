import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


for key in mpl.rcParams:
    if key.startswith('keymap.'):
        mpl.rcParams[key] = []


K = 8.99e9 
LIMIT = 10
GRID_RES = 25

x_range = y_range = np.linspace(-LIMIT, LIMIT, GRID_RES)
X, Y = np.meshgrid(x_range, y_range)

charges = [
    {"q": 1, "x": -2, "y": 0},
    {"q": -1, "x": 2, "y": 0}
]

selected_charge = None
is_dragging = False
RADIUS = 0.8 

def calculate_field(X, Y, charges_list):
    Ex_total = np.zeros_like(X)
    Ey_total = np.zeros_like(Y)
    
    for c in charges_list:
        dx = X - c["x"]
        dy = Y - c["y"]
        r_cubed = (dx**2 + dy**2 + 1e-15)**1.5
        Ex_total += K * c["q"] * dx / r_cubed
        Ey_total += K * c["q"] * dy / r_cubed
        
    mag = np.sqrt(Ex_total**2 + Ey_total**2 + 1e-15)
    return Ex_total/mag, Ey_total/mag


def get_hovered_charge(x, y):
    for c in charges:
        if np.sqrt((x - c["x"])**2 + (y - c["y"])**2) < RADIUS:
            return c
    return None

def on_press(event):
    global selected_charge, is_dragging
    if event.xdata is None:
        return
    selected_charge = get_hovered_charge(event.xdata, event.ydata)
    if selected_charge:
        is_dragging = True

def on_motion(event):
    if is_dragging and selected_charge and event.xdata is not None:
        selected_charge["x"], selected_charge["y"] = event.xdata, event.ydata
        update_plot()

def on_release(event):
    global is_dragging, selected_charge
    is_dragging = False
    selected_charge = None

def on_scroll(event):
    if event.xdata is None:
        return
    c = get_hovered_charge(event.xdata, event.ydata)
    
    if c:
        if event.button == 'up':
            c["q"] += 1
        if event.button == 'down':
            c["q"] -= 1
        
        
        if c["q"] == 0:
            charges.remove(c)
        update_plot()

def on_key(event):
    if event.xdata is None:
        return
    
    c = get_hovered_charge(event.xdata, event.ydata)
    

    if c:
        if event.key == '-': 
            c["q"] *= -1
        elif event.key in '123456789': 
            sign = 1 if c["q"] > 0 else -1
            c["q"] = int(event.key) * sign
        elif event.key in ['backspace', 'delete']:
            charges.remove(c)
            
            
    else:
        if event.key in '123456789':
            charges.append({"q": int(event.key), "x": event.xdata, "y": event.ydata})
        elif event.key == 'p':
            charges.append({"q": 1, "x": event.xdata, "y": event.ydata})
        elif event.key in ['n', '-']:
            charges.append({"q": -1, "x": event.xdata, "y": event.ydata})


    if event.key == 'c':
        charges.clear()
        
    update_plot()


plt.ion()
fig, ax = plt.subplots(figsize=(9, 9), num='Physics 2: Electric Field Visualizer')


fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('key_press_event', on_key)
fig.canvas.mpl_connect('scroll_event', on_scroll)

def update_plot():
    ax.clear()
    
    # U, V = calculate_field(X, Y, charges)
    # ax.quiver(X, Y, U, V, color='cornflowerblue', alpha=0.5, pivot='mid')
    
    # for c in charges:
    #     color = 'red' if c["q"] > 0 else 'blue'
    #     label = f"+{c['q']}" if c["q"] > 0 else f"{c['q']}"
    #     # Make bigger charges look slightly bigger on screen
    #     size = 300 + (abs(c["q"]) * 50) 
    #     ax.scatter(c["x"], c["y"], color=color, s=size, zorder=5, edgecolors='black')
    #     ax.text(c["x"], c["y"], label, color='white', weight='bold', 
    #             ha='center', va='center', zorder=6)

    # ax.set_xlim(-LIMIT, LIMIT)
    # ax.set_ylim(-LIMIT, LIMIT)
    # ax.axhline(0, color='black', lw=0.5, alpha=0.3)
    # ax.axvline(0, color='black', lw=0.5, alpha=0.3)
    
    # title = ("Interactive Electric Fields\n"
    #          "[1-9] Drop specific charge | [Scroll] Edit charge size | [-] Flip Sign\n"
    #          "[Backspace] Delete charge | [C] Clear All")
    # ax.set_title(title, pad=15)
    
    # fig.canvas.draw_idle()

update_plot()
plt.show(block=True)