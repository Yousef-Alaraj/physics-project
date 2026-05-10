import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Disable default matplotlib keybinds so they don't interfere
for key in mpl.rcParams:
    if key.startswith('keymap.'):
        mpl.rcParams[key] = []

K = 8.99e9 
LIMIT = 10
GRID_RES = 25

x_range = y_range = np.linspace(-LIMIT, LIMIT, GRID_RES)
X, Y = np.meshgrid(x_range, y_range)

# Source charges list
charges = [
    {"q": 1, "x": -2, "y": 0},
    {"q": -1, "x": 2, "y": 0}
]

# State dictionary for our test charge
test_charge = {"active": False, "q": 1, "x": 0.0, "y": 0.0}

selected_target = None
target_type = None  
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
    # UPDATED: We now return the raw magnitude so we can scale the arrows!
    return Ex_total, Ey_total, mag

def get_hovered_target(x, y):
    if test_charge["active"]:
        if np.sqrt((x - test_charge["x"])**2 + (y - test_charge["y"])**2) < RADIUS:
            return "test", test_charge
            
    for c in charges:
        if np.sqrt((x - c["x"])**2 + (y - c["y"])**2) < RADIUS:
            return "source", c
            
    return None, None

def on_press(event):
    global selected_target, target_type, is_dragging
    if event.xdata is None:
        return
    target_type, selected_target = get_hovered_target(event.xdata, event.ydata)
    if selected_target:
        is_dragging = True

def on_motion(event):
    if is_dragging and selected_target and event.xdata is not None:
        selected_target["x"], selected_target["y"] = event.xdata, event.ydata
        update_plot()

def on_release(event):
    global is_dragging, selected_target, target_type
    is_dragging = False
    selected_target = None
    target_type = None

def on_scroll(event):
    if event.xdata is None:
        return
    t_type, target = get_hovered_target(event.xdata, event.ydata)
    
    if target:
        if event.button == 'up':
            target["q"] += 1
        if event.button == 'down':
            target["q"] -= 1
        
        if target["q"] == 0 and t_type == "source":
            charges.remove(target)
        update_plot()

def on_key(event):
    if event.xdata is None:
        return
    
    t_type, target = get_hovered_target(event.xdata, event.ydata)

    if target:
        if event.key == '-': 
            target["q"] *= -1
        elif event.key in '123456789': 
            sign = 1 if target["q"] >= 0 else -1
            target["q"] = int(event.key) * sign
        elif event.key in ['backspace', 'delete']:
            if t_type == "test":
                test_charge["active"] = False
            else:
                charges.remove(target)
    else:
        if event.key == 't':
            test_charge["active"] = True
            test_charge["x"] = event.xdata
            test_charge["y"] = event.ydata
        elif event.key in '123456789':
            charges.append({"q": int(event.key), "x": event.xdata, "y": event.ydata})
        elif event.key == 'p':
            charges.append({"q": 1, "x": event.xdata, "y": event.ydata})
        elif event.key in ['n', '-']:
            charges.append({"q": -1, "x": event.xdata, "y": event.ydata})

    if event.key == 'c':
        charges.clear()
        test_charge["active"] = False
        
    update_plot()

plt.ion()
fig, ax = plt.subplots(figsize=(10, 10), num='Physics 2: Electric Field Visualizer')

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('key_press_event', on_key)
fig.canvas.mpl_connect('scroll_event', on_scroll)

def update_plot():
    ax.clear()
    
    # 1. Draw the dynamic background E-field Map
    Ex, Ey, E_mag = calculate_field(X, Y, charges)
    
    # Scale vectors logarithmically so they grow smoothly without covering the whole screen
    log_mag = np.log10(E_mag + 1)
    U = (Ex / E_mag) * log_mag
    V = (Ey / E_mag) * log_mag
    
    # Draw field arrows: Length is dynamic, color changes based on strength (log_mag)
    ax.quiver(X, Y, U, V, log_mag, cmap='plasma', alpha=0.7, pivot='mid')
    
    # 2. Draw Source Charges
    for c in charges:
        color = 'red' if c["q"] > 0 else 'blue'
        label = f"+{c['q']}" if c["q"] > 0 else f"{c['q']}"
        size = 300 + (abs(c["q"]) * 50) 
        ax.scatter(c["x"], c["y"], color=color, s=size, zorder=5, edgecolors='black')
        ax.text(c["x"], c["y"], label, color='white', weight='bold', 
                ha='center', va='center', zorder=6)

    # 3. Draw Test Charge & Calculate Exact E and F
    if test_charge["active"]:
        Ex_tc, Ey_tc = 0.0, 0.0
        for c in charges:
            dx = test_charge["x"] - c["x"]
            dy = test_charge["y"] - c["y"]
            r_squared = dx**2 + dy**2
            if r_squared > 0.01: 
                r_cubed = r_squared**1.5
                Ex_tc += K * c["q"] * dx / r_cubed
                Ey_tc += K * c["q"] * dy / r_cubed
                
        E_tc_mag = np.sqrt(Ex_tc**2 + Ey_tc**2 + 1e-15)
        F_mag = abs(test_charge["q"]) * E_tc_mag
        
        tc_color = 'lime' if test_charge["q"] >= 0 else 'magenta'
        
        # Test Charge Marker
        ax.scatter(test_charge["x"], test_charge["y"], color=tc_color, s=250, marker='*', zorder=7, edgecolors='black')
        
        # FIXED: Test Charge label made highly visible (offset slightly, larger font, white background box)
        ax.text(test_charge["x"] + 0.6, test_charge["y"] + 0.6, 
                f"Test: {test_charge['q']}q", color='black', weight='bold', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.3'),
                ha='left', va='bottom', zorder=10, fontsize=11)
        
        scale_factor = np.log10(E_tc_mag + 1) * 0.3
        
        # Plot E-Field Vector (Orange)
        if E_tc_mag > 0:
            dx_E = (Ex_tc / E_tc_mag) * scale_factor
            dy_E = (Ey_tc / E_tc_mag) * scale_factor
            ax.arrow(test_charge["x"], test_charge["y"], dx_E, dy_E, 
                     color='darkorange', width=0.1, head_width=0.35, zorder=6)
            ax.text(test_charge["x"] + dx_E*1.2, test_charge["y"] + dy_E*1.2, 
                    f"E = {E_tc_mag:.1e} N/C", color='darkorange', fontsize=10, weight='bold',
                    bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=0))
        
        # Plot Force Vector (Purple)
        if F_mag > 0:
            Fx = test_charge["q"] * Ex_tc
            Fy = test_charge["q"] * Ey_tc
            dx_F = (Fx / F_mag) * (scale_factor * 1.5)
            dy_F = (Fy / F_mag) * (scale_factor * 1.5)
            ax.arrow(test_charge["x"], test_charge["y"], dx_F, dy_F, 
                     color='purple', width=0.1, head_width=0.35, zorder=5)
            ax.text(test_charge["x"] + dx_F*1.2, test_charge["y"] + dy_F*1.2, 
                    f"F = {F_mag:.1e} N", color='purple', fontsize=10, weight='bold',
                    bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=0))


    ax.set_xlim(-LIMIT, LIMIT)
    ax.set_ylim(-LIMIT, LIMIT)
    ax.axhline(0, color='black', lw=0.5, alpha=0.3)
    ax.axvline(0, color='black', lw=0.5, alpha=0.3)
    
    title = ("Interactive Electric Fields\n"
             "[1-9] Drop charge | [T] Toggle Test Charge | [Scroll] Edit charge size \n"
             "[-] Flip Sign | [Backspace] Delete | [C] Clear All")
    ax.set_title(title, pad=15)
    
    fig.canvas.draw_idle()

update_plot()
plt.show(block=True)