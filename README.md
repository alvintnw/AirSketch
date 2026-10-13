# Air Canvas Pro 
A professional AI-based virtual whiteboard using Computer Vision. Draw in mid-air using hand gestures!

## Features
- **Skeletal Hand Tracking:** Powered by MediaPipe.
- **Modern UI:** Glassmorphism-style HUD with live brush preview.
- **Gesture Controls:**
  - 👆 Index Finger: Draw
  - ✌️ Two Fingers: Selection & Navigation
  - 👌 Pinch: Dynamic Brush Resizing
  - 🖐️ Five Fingers: Clear Canvas (1s hold)
- **Editing Controls:**
   - `Z`: Undo the last stroke or clear action
   - `Y`: Redo the last undone action
   - `B`: Toggle camera view and whiteboard mode
   - `G`: Toggle whiteboard grid
   - `V`: Toggle drawing layer visibility
   - `C`: Clear the canvas
   - `S`: Save the canvas as a PNG image
   - `P`: Save a transparent PNG
   - `J`: Save a JPG with a white background
- **Shape Modes:**
   - `N`: Freehand drawing
   - `L`: Straight line
   - `R`: Rectangle
   - `O`: Circle

## Setup
1. Clone this repo:
```bash
   git clone https://github.com/FatemeMolaeiJahromi/Air-Canvas.git
   cd Air-Canvas
   
# 2. Create Virtual Enviroment:
   python -m venv venv
   # Activate: venv\Scripts\activate (on Windows)

# 3. Install dependencies:
   pip install -r requirements.txt
   
# 4. Run
   python main.py
   
Requirements
Python 3.11+
Webcam
