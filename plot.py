import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GainPlotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Multi-Channel Amplitude vs Time with Gain")
        self.master.geometry("900x700")
        
        # Load channel data
        # In a real application, handle file not found errors
        try:
            self.channel_data = { 
                "Channel 1": pd.read_csv("channel1.csv"),
                "Channel 2": pd.read_csv("channel2.csv"),
                "Channel 3": pd.read_csv("channel3.csv")
            }
            
            # Clean up the data
            for key, df in self.channel_data.items():
                # Strip whitespace from column names
                df.columns = df.columns.str.strip()
                # Ensure there's a Time column
                if 'Time' not in df.columns:
                    raise ValueError(f"{key} CSV file must contain a 'Time' column")
                # Drop rows with missing time values
                self.channel_data[key] = df.dropna(subset=['Time'])
                
        except FileNotFoundError as e:
            print(f"Error loading channel data: {e}")
            # Create some dummy data for testing if files aren't found
            self.create_dummy_data()
            
        # Channel data and state
        self.channels = [
            {"name": "Channel 1", "color": 'yellow', "visible": True, "gain": 1.0, "cursor_color": 'yellow'},
            {"name": "Channel 2", "color": '#C71585', "visible": True, "gain": 1.0, "cursor_color": '#C71585'},
            {"name": "Channel 3", "color": 'blue', "visible": True, "gain": 1.0, "cursor_color": 'blue'}
        ]
        
        self.gain_values = [0.5, 1.0, 2.0, 5.0, 10.0]
        self.active_channel = 0  # Default active channel index

        # Main frames
        control_frame = ttk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=10)
        
        channels_frame = ttk.LabelFrame(master, text="Channel Controls")
        channels_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=10)

        # Create channel control rows
        self.active_rb_var = tk.IntVar(value=self.active_channel)
        for i, channel in enumerate(self.channels):
            channel_frame = ttk.Frame(channels_frame)
            channel_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Channel visibility checkbox
            channel["var_visible"] = tk.BooleanVar(value=channel["visible"])
            channel_cb = ttk.Checkbutton(
                channel_frame, 
                text=channel["name"],
                variable=channel["var_visible"],
                command=lambda idx=i: self.on_channel_visibility_change(idx)
            )
            channel_cb.pack(side=tk.LEFT, padx=5)
            
            # Channel color indicator
            color_label = ttk.Label(channel_frame, text="   ", background=channel["color"])
            color_label.pack(side=tk.LEFT, padx=5)
            
            # Channel gain control
            channel["var_gain"] = tk.DoubleVar(value=channel["gain"])
            ttk.Label(channel_frame, text="Gain:").pack(side=tk.LEFT, padx=5)
            gain_cb = ttk.Combobox(
                channel_frame, 
                textvariable=channel["var_gain"],
                values=self.gain_values, 
                state="readonly", 
                width=5
            )
            gain_cb.pack(side=tk.LEFT, padx=5)
            gain_cb.bind("<<ComboboxSelected>>", self.update_plot)
            
            # Active channel selection (for cursor measurements)
            channel["active_rb"] = ttk.Radiobutton(
                channel_frame,
                text="Active",
                variable=self.active_rb_var,
                value=i,
                command=lambda idx=i: self.set_active_channel(idx)
            )
            channel["active_rb"].pack(side=tk.LEFT, padx=5)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)

        # Label for displaying cursor coordinates
        self.coord_label = ttk.Label(master, text="X: ---, Y: ---", anchor='center')
        self.coord_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Vertical cursors
        self.cursor1 = self.ax.axvline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)
        self.cursor2 = self.ax.axvline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)

        # Horizontal cursors
        self.cursor_h1 = self.ax.axhline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)
        self.cursor_h2 = self.ax.axhline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)

        # Text boxes
        self.delta_text = self.ax.text(0.7, 0.95, '', transform=self.ax.transAxes,
                                       verticalalignment='top',
                                       bbox=dict(boxstyle='round', facecolor=self.channels[self.active_channel]['color'], alpha=0.3),
                                       visible=False)
        self.delta_y_text = self.ax.text(0.7, 0.85, '', transform=self.ax.transAxes,
                                         verticalalignment='top',
                                         bbox=dict(boxstyle='round', facecolor=self.channels[self.active_channel]['color'], alpha=0.3),
                                         visible=False)

        # Click buffers
        self.cursor_clicks = []     # For vertical
        self.h_cursor_clicks = []   # For horizontal

        # Drag state
        self.dragging = None  # None, 'v1', 'v2', 'h1', or 'h2'

        # Event bindings
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)

        self.plot()

    def create_dummy_data(self):
        """Create dummy data for testing when real data files are not available"""
        import numpy as np
        
        # Create time axis from 0 to 10 seconds
        time = np.linspace(0, 10, 1000)
        
        # Create Channel 1: Sine wave
        ch1_data = pd.DataFrame({
            'Time': time,
            'Amplitude': np.sin(2 * np.pi * 1 * time)  # 1 Hz sine wave
        })
        
        # Create Channel 2: Cosine wave
        ch2_data = pd.DataFrame({
            'Time': time,
            'Amplitude': np.cos(2 * np.pi * 0.5 * time)  # 0.5 Hz cosine wave
        })
        
        # Create Channel 3: Square wave
        ch3_data = pd.DataFrame({
            'Time': time,
            'Amplitude': np.sign(np.sin(2 * np.pi * 0.25 * time))  # 0.25 Hz square wave
        })
        
        self.channel_data = {
            "Channel 1": ch1_data,
            "Channel 2": ch2_data,
            "Channel 3": ch3_data
        }
        
        print("Created dummy data for testing")

    def on_channel_visibility_change(self, channel_idx):
        """Handle channel visibility changes"""
        # If the active channel is being hidden, clear its cursors
        if channel_idx == self.active_channel and not self.channels[channel_idx]["var_visible"].get():
            self.clear_cursors()
        
        # Update the plot
        self.update_plot()
        
        # If no channels are visible after this change, make sure cursors are cleared
        has_visible_channels = any(channel["var_visible"].get() for channel in self.channels)
        if not has_visible_channels:
            self.clear_cursors()

    def clear_cursors(self):
        """Clear all cursors and measurements"""
        self.cursor_clicks = []
        self.h_cursor_clicks = []
        self.cursor1.set_visible(False)
        self.cursor2.set_visible(False)
        self.cursor_h1.set_visible(False)
        self.cursor_h2.set_visible(False)
        self.delta_text.set_visible(False)
        self.delta_y_text.set_visible(False)
        self.canvas.draw()

    def set_active_channel(self, channel_idx):
        # Store the previous active channel for reference
        prev_channel = self.active_channel
        
        # Update active channel
        self.active_channel = channel_idx
        
        # Clear cursors if the newly active channel is not visible
        if not self.channels[channel_idx]["var_visible"].get():
            self.clear_cursors()
            # Make the channel visible since it's now active
            self.channels[channel_idx]["var_visible"].set(True)
            self.update_plot()
            return
        
        # Clear previous cursors and measurements when changing active channel
        self.clear_cursors()
        
        # Update the plot to refresh with new active channel settings
        self.canvas.draw()

    def plot(self):
        self.ax.clear()
        
        has_visible_channels = False
        
        for i, channel in enumerate(self.channels):
            if not channel["var_visible"].get():
                continue
                
            has_visible_channels = True
            
            # Get data for this channel
            df = self.channel_data[channel["name"]]
            time_data = df["Time"]
            
            # Determine amplitude column name
            amplitude_col = "Amplitude"
            if f"Amplitude{i+1}" in df.columns:
                amplitude_col = f"Amplitude{i+1}"
            elif "Amplitude" not in df.columns:
                # If no obvious amplitude column, use the second column
                amplitude_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            # Apply gain and plot
            scaled_amplitude = df[amplitude_col] * channel["var_gain"].get()
            self.ax.plot(time_data, scaled_amplitude,
                        label=f"{channel['name']} (Gain = {channel['var_gain'].get()}x)",
                        color=channel["color"])
        
        if not has_visible_channels:
            # Show at least one channel if none are selected
            self.channels[0]["var_visible"].set(True)
            df = self.channel_data[self.channels[0]["name"]]
            time_data = df["Time"]
            amplitude_col = "Amplitude"
            if "Amplitude1" in df.columns:
                amplitude_col = "Amplitude1"
            elif "Amplitude" not in df.columns:
                amplitude_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
                
            scaled_amplitude = df[amplitude_col] * self.channels[0]["var_gain"].get()
            self.ax.plot(time_data, scaled_amplitude,
                        label=f"{self.channels[0]['name']} (Gain = {self.channels[0]['var_gain'].get()}x)",
                        color=self.channels[0]["color"])
        
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude (V)")
        self.ax.set_title("Multi-Channel Amplitude vs Time")
        self.ax.grid(True)
        self.ax.legend()

        # Reinitialize cursors
        self.cursor1 = self.ax.axvline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)
        self.cursor2 = self.ax.axvline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)
        self.cursor_h1 = self.ax.axhline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)
        self.cursor_h2 = self.ax.axhline(color=self.channels[self.active_channel]["cursor_color"], linestyle='--', linewidth=1, visible=False)

        # Text boxes
        self.delta_text = self.ax.text(0.7, 0.95, '', transform=self.ax.transAxes,
                                       verticalalignment='top',
                                       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7),
                                       visible=False)
        self.delta_y_text = self.ax.text(0.7, 0.85, '', transform=self.ax.transAxes,
                                         verticalalignment='top',
                                         bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.7),
                                         visible=False)

        # Only restore cursor positions if the active channel is visible
        if self.channels[self.active_channel]["var_visible"].get():
            if self.cursor_clicks:
                if len(self.cursor_clicks) >= 1:
                    self.cursor1.set_xdata([self.cursor_clicks[0]])
                    self.cursor1.set_visible(True)
                if len(self.cursor_clicks) >= 2:
                    self.cursor2.set_xdata([self.cursor_clicks[1]])
                    self.cursor2.set_visible(True)
                    self.update_vertical_delta()
            
            if self.h_cursor_clicks:
                if len(self.h_cursor_clicks) >= 1:
                    self.cursor_h1.set_ydata([self.h_cursor_clicks[0]])
                    self.cursor_h1.set_visible(True)
                if len(self.h_cursor_clicks) >= 2:
                    self.cursor_h2.set_ydata([self.h_cursor_clicks[1]])
                    self.cursor_h2.set_visible(True)
                    self.update_horizontal_delta()
        else:
            # If active channel is not visible, clear cursors
            self.cursor_clicks = []
            self.h_cursor_clicks = []

        self.canvas.draw()

    def update_plot(self, event=None):
        # Check if active channel is visible
        if not self.channels[self.active_channel]["var_visible"].get():
            # Clear cursors if active channel becomes invisible
            self.clear_cursors()
        
        self.plot()

    def on_mouse_move(self, event):
        if event.inaxes == self.ax:
            x_val = event.xdata
            y_val = event.ydata
            active_channel = self.channels[self.active_channel]
            self.coord_label.config(text=f"X: {x_val:.3f}, Y: {y_val:.3f} ({active_channel['name']})")
        else:
            self.coord_label.config(text="X: ---, Y: ---")

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
            
        # Check if the active channel is visible before allowing cursor placement
        if not self.channels[self.active_channel]["var_visible"].get():
            return

        x = event.xdata
        y = event.ydata
        active_channel_color = self.channels[self.active_channel]["cursor_color"]

        # Left click (vertical cursors)
        if event.button == 1:
            if self.cursor1.get_visible() and abs(x - self.cursor1.get_xdata()[0]) < (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.02:
                self.dragging = 'v1'
                return
            elif self.cursor2.get_visible() and abs(x - self.cursor2.get_xdata()[0]) < (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.02:
                self.dragging = 'v2'
                return

            if len(self.cursor_clicks) == 2:
                self.cursor_clicks.clear()
                self.cursor1.set_visible(False)
                self.cursor2.set_visible(False)
                self.delta_text.set_visible(False)
                self.canvas.draw_idle()

            self.cursor_clicks.append(x)

            if len(self.cursor_clicks) == 1:
                self.cursor1.set_xdata([x])
                self.cursor1.set_color(active_channel_color)
                self.cursor1.set_visible(True)
                self.canvas.draw_idle()

            elif len(self.cursor_clicks) == 2:
                self.cursor2.set_xdata([x])
                self.cursor2.set_color(active_channel_color)
                self.cursor2.set_visible(True)
                self.update_vertical_delta()
                self.canvas.draw_idle()

        # Right click (horizontal cursors)
        elif event.button == 3:
            if self.cursor_h1.get_visible() and abs(y - self.cursor_h1.get_ydata()[0]) < (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.02:
                self.dragging = 'h1'
                return
            elif self.cursor_h2.get_visible() and abs(y - self.cursor_h2.get_ydata()[0]) < (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.02:
                self.dragging = 'h2'
                return

            if len(self.h_cursor_clicks) == 2:
                self.h_cursor_clicks.clear()
                self.cursor_h1.set_visible(False)
                self.cursor_h2.set_visible(False)
                self.delta_y_text.set_visible(False)
                self.canvas.draw_idle()

            self.h_cursor_clicks.append(y)

            if len(self.h_cursor_clicks) == 1:
                self.cursor_h1.set_ydata([y])
                self.cursor_h1.set_color(active_channel_color)
                self.cursor_h1.set_visible(True)
                self.canvas.draw_idle()

            elif len(self.h_cursor_clicks) == 2:
                self.cursor_h2.set_ydata([y])
                self.cursor_h2.set_color(active_channel_color)
                self.cursor_h2.set_visible(True)
                self.update_horizontal_delta()
                self.canvas.draw_idle()

    def on_release(self, event):
        self.dragging = None

    def on_drag(self, event):
        if self.dragging is None or event.inaxes != self.ax:
            return

        # Check if the active channel is visible before allowing cursor manipulation
        if not self.channels[self.active_channel]["var_visible"].get():
            return

        if self.dragging == 'v1':
            x = event.xdata
            xmin, xmax = self.ax.get_xlim()
            x = max(min(x, xmax), xmin)
            self.cursor1.set_xdata([x])
            self.cursor_clicks[0] = x
            self.update_vertical_delta()
            self.canvas.draw_idle()
        elif self.dragging == 'v2':
            x = event.xdata
            xmin, xmax = self.ax.get_xlim()
            x = max(min(x, xmax), xmin)
            self.cursor2.set_xdata([x])
            self.cursor_clicks[1] = x
            self.update_vertical_delta()
            self.canvas.draw_idle()
        elif self.dragging == 'h1':
            y = event.ydata
            ymin, ymax = self.ax.get_ylim()
            y = max(min(y, ymax), ymin)
            self.cursor_h1.set_ydata([y])
            self.h_cursor_clicks[0] = y
            self.update_horizontal_delta()
            self.canvas.draw_idle()
        elif self.dragging == 'h2':
            y = event.ydata
            ymin, ymax = self.ax.get_ylim()
            y = max(min(y, ymax), ymin)
            self.cursor_h2.set_ydata([y])
            self.h_cursor_clicks[1] = y
            self.update_horizontal_delta()
            self.canvas.draw_idle()

    def update_vertical_delta(self):
        if len(self.cursor_clicks) == 2:
            delta_x = abs(self.cursor_clicks[1] - self.cursor_clicks[0])
            active_channel = self.channels[self.active_channel]
            if delta_x != 0:
                freq = 1 / delta_x
                self.delta_text.set_text(f"ΔTime = {delta_x:.4f} s\nFreq = {freq:.2f} Hz\n({active_channel['name']})")
                # Change the box color to match channel
                self.delta_text.set_bbox(dict(boxstyle='round', facecolor=active_channel['color'], alpha=0.3))
            else:
                self.delta_text.set_text(f"ΔTime = 0.0000 s\nFreq = ∞\n({active_channel['name']})")
                self.delta_text.set_bbox(dict(boxstyle='round', facecolor=active_channel['color'], alpha=0.3))
            self.delta_text.set_visible(True)
            self.delta_y_text.set_visible(False)

    def update_horizontal_delta(self):
        if len(self.h_cursor_clicks) == 2:
            delta_y = abs(self.h_cursor_clicks[1] - self.h_cursor_clicks[0])
            active_channel = self.channels[self.active_channel]
            self.delta_y_text.set_text(f"ΔAmp = {delta_y:.4f} V\n({active_channel['name']})")
            # Change the box color to match channel
            self.delta_y_text.set_bbox(dict(boxstyle='round', facecolor=active_channel['color'], alpha=0.3))
            self.delta_y_text.set_visible(True)
            self.delta_text.set_visible(False)


if __name__ == "__main__":
    root = tk.Tk()
    app = GainPlotApp(root)
    root.mainloop()