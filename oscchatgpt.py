import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# Constants
ADC_MAX = 1023
VREF = 3.3

# MCP6S21 Gain mapping and corresponding max input and v/div
GAIN_INFO = {
    "1x":  {"gain": 1,  "max_input": 3.30,  "vdiv": 0.5},
    "2x":  {"gain": 2,  "max_input": 1.65,  "vdiv": 0.25},
    "4x":  {"gain": 4,  "max_input": 0.825, "vdiv": 0.1},
    "5x":  {"gain": 5,  "max_input": 0.66,  "vdiv": 0.05},
    "8x":  {"gain": 8,  "max_input": 0.412, "vdiv": 0.02},
    "10x": {"gain": 10, "max_input": 0.33,  "vdiv": 0.01},
    "16x": {"gain": 16, "max_input": 0.206, "vdiv": 0.005},
    "32x": {"gain": 32, "max_input": 0.103, "vdiv": 0.002}
}

def format_voltage(value):
    if value < 1.0:
        return f"{value * 1000:.0f} mV"
    else:
        return f"{value:.2f} V"

def format_vdiv(v):
    if v < 0.001:
        return f"{v*1_000_000:.0f} µV/div"
    elif v < 1.0:
        return f"{v*1000:.0f} mV/div"
    else:
        return f"{v:.0f} V/div"

class OscilloscopeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Easy DAQ Oscilloscope with MCP6S21 Gain Scaling")

        self.selected_gain = tk.StringVar(value="1x")

        ttk.Label(root, text="Select MCP6S21 PGA Gain:").pack(pady=5)
        gain_menu = ttk.OptionMenu(root, self.selected_gain, "1x", *GAIN_INFO.keys(), command=lambda _: self.update_plot())
        gain_menu.pack()

        ttk.Button(root, text="Start Capture", command=self.update_plot).pack(pady=10)

        self.info_label = ttk.Label(root, text="")
        self.info_label.pack()

        self.figure, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()

    def update_plot(self):
        gain_str = self.selected_gain.get()
        gain_data = GAIN_INFO[gain_str]
        gain = gain_data["gain"]
        max_input = gain_data["max_input"]
        vdiv = gain_data["vdiv"]
        total_v_range = vdiv * 8

        # Simulated ADC data (or replace with UART read)
        adc_samples = [random.randint(450, 570) for _ in range(100)]
        voltages = [((val / ADC_MAX) * VREF) / gain for val in adc_samples]

        self.ax.clear()
        self.ax.plot(voltages, label="Input Signal")
        self.ax.set_title("Oscilloscope View")
        self.ax.set_ylabel("Voltage")
        self.ax.set_xlabel("Sample #")
        self.ax.set_ylim(0, total_v_range)
        self.ax.grid(True)
        self.ax.legend()

        self.canvas.draw()

        self.info_label.config(
            text=f"Gain: {gain_str} | Max Input: {format_voltage(max_input)} | V/Div: {format_vdiv(vdiv)} | Plot Range: 0 – {format_voltage(total_v_range)}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = OscilloscopeGUI(root)
    root.mainloop()