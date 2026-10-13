# AirSketch

Air Canvas Studio is a computer vision-based virtual whiteboard that lets you draw in the air using hand gestures. It uses a webcam, OpenCV, and MediaPipe hand tracking to turn index-finger movements into digital drawings in real time.

## Features

- Real-time hand landmark tracking powered by MediaPipe
- Freehand drawing with a smooth cursor and adjustable brush size
- Gesture-based color selection and navigation
- Pinch gesture for dynamic brush and eraser resizing
- Freehand, line, rectangle, and circle drawing modes
- Undo and redo history with up to 30 canvas states
- Camera view and clean whiteboard view
- Optional whiteboard grid and drawing-layer visibility
- Canvas export as a regular PNG, transparent PNG, or white-background JPG
- Hands-free canvas clearing by holding all five fingers up

## Gesture Controls

| Gesture | Action |
| --- | --- |
| Index finger up | Draw on the canvas |
| Index and middle fingers up | Navigate and select a color |
| Thumb and index finger pinch | Change brush or eraser size |
| All five fingers up for 1.2 seconds | Clear the canvas |

## Keyboard Controls

| Key | Action |
| --- | --- |
| `N` | Freehand drawing mode |
| `L` | Straight-line mode |
| `R` | Rectangle mode |
| `O` | Circle mode |
| `Z` | Undo |
| `Y` | Redo |
| `B` | Toggle camera and whiteboard view |
| `G` | Toggle the whiteboard grid |
| `V` | Toggle drawing-layer visibility |
| `C` | Clear the canvas |
| `S` | Save a regular PNG |
| `P` | Save a transparent PNG |
| `J` | Save a JPG with a white background |
| `Q` | Quit the application |

## Requirements

- Python 3.11 or newer
- A working webcam
- Windows, macOS, or Linux with a graphical desktop environment

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/FatemeMolaeiJahromi/Air-Canvas.git
   cd Air-Canvas
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **macOS or Linux**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run the Application

Make sure your webcam is connected and available, then run:

```bash
python main.py
```

Move your hand in front of the camera and use the gesture controls to draw. Exported files are saved in the project directory with timestamp-based filenames.

## Troubleshooting

- If the camera cannot be opened, close applications that may already be using the webcam.
- Use good lighting and keep your hand inside the camera frame for more reliable tracking.
- Press `Q` to close the application safely.

## Project Structure

```text
.
├── HandTrackingModule.py  # MediaPipe hand detection and finger recognition
├── main.py                # Drawing application and user interface
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```
