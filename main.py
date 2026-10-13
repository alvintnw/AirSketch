import cv2
import numpy as np
import time
import HandTrackingModule as htm
WIDTH, HEIGHT = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
if not cap.isOpened():
    raise RuntimeError("Camera tidak dapat dibuka. Pastikan webcam terhubung dan tidak sedang digunakan aplikasi lain.")

detector = htm.HandDetector(detection_con=0.85, track_con=0.8)
PALETTE = [
    {"name": "CYAN",    "color": (255, 230, 0)},
    {"name": "NEON-G",  "color": (50, 255, 50)},
    {"name": "PINK",    "color": (204, 0, 255)},
    {"name": "AMBER",   "color": (0, 165, 255)},
    {"name": "RED",     "color": (40, 40, 255)},
    {"name": "ERASER",  "color": (0, 0, 0)},
]

draw_color = PALETTE[0]["color"]
brush_size = 8
eraser_size = 65
SMOOTH_FACTOR = 0.65
prev_x, prev_y = 0, 0
draw_x, draw_y = 0, 0
canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
prev_time = 0
clear_timer = 0
canvas_history = []
redo_history = []
MAX_HISTORY = 30
clear_done = False
show_camera = True
show_grid = False
show_canvas = True
last_selection_time = 0
shape_mode = None
shape_start = None
shape_end = None


def save_canvas_state():
    canvas_history.append(canvas.copy())
    if len(canvas_history) > MAX_HISTORY:
        canvas_history.pop(0)
    redo_history.clear()


def undo_canvas():
    global canvas
    if canvas_history:
        redo_history.append(canvas.copy())
        canvas = canvas_history.pop()


def redo_canvas():
    global canvas
    if redo_history:
        canvas_history.append(canvas.copy())
        canvas = redo_history.pop()


def draw_shape(target, mode, start, end, color, thickness):
    if mode == "line":
        cv2.line(target, start, end, color, thickness)
    elif mode == "rectangle":
        cv2.rectangle(target, start, end, color, thickness)
    elif mode == "circle":
        radius = int(np.hypot(end[0] - start[0], end[1] - start[1]))
        cv2.circle(target, start, radius, color, thickness)


def save_transparent_png(filename):
    alpha = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    alpha = np.where(alpha > 0, 255, 0).astype(np.uint8)
    output = cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)
    output[:, :, 3] = alpha
    cv2.imwrite(filename, output)


def save_white_jpg(filename):
    output = np.full_like(canvas, 255)
    mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY) > 0
    output[mask] = canvas[mask]
    cv2.imwrite(filename, output)


def render_ui(img, current_color, current_brush_size, fps):
    header_h = 85
    box_w = WIDTH // len(PALETTE)
    sub_overlay = img[0:header_h, 0:WIDTH].copy()
    cv2.rectangle(sub_overlay, (0, 0), (WIDTH, header_h), (20, 20, 25), -1)
    img[0:header_h, 0:WIDTH] = cv2.addWeighted(sub_overlay, 0.75, img[0:header_h, 0:WIDTH], 0.25, 0)
    cv2.line(img, (0, header_h), (WIDTH, header_h), (80, 80, 80), 1)

    for i, item in enumerate(PALETTE):
        x1 = i * box_w + 12
        x2 = (i + 1) * box_w - 12
        col = item["color"]
        name = item["name"]
        is_active = (col == current_color)
        bg_col = (40, 40, 40) if name == "ERASER" else col
        if is_active:
            cv2.rectangle(img, (x1 - 3, 10), (x2 + 3, header_h - 10), (255, 255, 255), 3)

        cv2.rectangle(img, (x1, 13), (x2, header_h - 13), bg_col, -1)
        text_color = (255, 255, 255) if name != "CYAN" else (30, 30, 30)
        cv2.putText(img, name, (x1 + 25, 52), cv2.FONT_HERSHEY_DUPLEX, 0.6, text_color, 1, cv2.LINE_AA)

    widget_w, widget_h = 240, 75
    w_overlay = img[HEIGHT - widget_h - 15:HEIGHT - 15, 15:15 + widget_w].copy()
    cv2.rectangle(w_overlay, (0, 0), (widget_w, widget_h), (15, 15, 15), -1)
    img[HEIGHT - widget_h - 15:HEIGHT - 15, 15:15 + widget_w] = cv2.addWeighted(
        w_overlay, 0.7, img[HEIGHT - widget_h - 15:HEIGHT - 15, 15:15 + widget_w], 0.3, 0
    )
    cv2.rectangle(img, (15, HEIGHT - widget_h - 15), (15 + widget_w, HEIGHT - 15), (80, 80, 80), 1)

    is_eraser = current_color == (0, 0, 0)
    preview_col = (200, 200, 200) if is_eraser else current_color
    preview_size = eraser_size if is_eraser else current_brush_size
    cv2.circle(img, (55, HEIGHT - 52), preview_size // 2 + 2, preview_col, -1)
    status_label = f"ERASER: {eraser_size}px" if current_color == (0, 0, 0) else f"BRUSH: {current_brush_size}px"
    cv2.putText(img, status_label, (90, HEIGHT - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.putText(img, f"FPS: {int(fps)}", (WIDTH - 110, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

print("=" * 55)
print(">>> Air Canvas Studio Pro is running...")
print(">>> Shortcuts: [Q] Quit | [C] Clear | [Z] Undo | [Y] Redo")
print(">>> Modes: [N] Freehand | [L] Line | [R] Rectangle | [O] Circle")
print(">>> View: [B] Camera/Board | [G] Grid | [V] Drawing Layer | [S/P/J] Export")
print("=" * 55)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img = detector.find_hands(img, draw=False)
    lm_list = detector.find_position(img)

    if len(lm_list) != 0:
        x1, y1 = lm_list[8][1], lm_list[8][2]
        x2, y2 = lm_list[12][1], lm_list[12][2]
        x0, y0 = lm_list[4][1], lm_list[4][2]

        fingers = detector.fingers_up()

        if fingers == [1, 1, 1, 1, 1]:
            if clear_timer == 0:
                clear_timer = time.time()
            elif time.time() - clear_timer > 1.2 and not clear_done:
                save_canvas_state()
                canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                clear_done = True
                cv2.putText(img, "CANVAS CLEARED!", (WIDTH // 2 - 180, HEIGHT // 2),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 2)
            elif not clear_done:
                progress = int((time.time() - clear_timer) / 1.2 * 100)
                cv2.putText(img, f"Clearing... {progress}%", (WIDTH // 2 - 100, HEIGHT // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 180, 255), 2)
            prev_x, prev_y = 0, 0
        elif clear_done:
            clear_timer = 0
            clear_done = False
            show_camera = True
        elif len(fingers) >= 3 and fingers[1] and fingers[2] and not fingers[3]:
            clear_timer = 0
            prev_x, prev_y = 0, 0
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(img, (center_x, center_y), 15, (255, 255, 255), 2)
            cv2.putText(img, "NAVIGATE", (center_x - 35, center_y - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            if y1 < 85:
                box_w = WIDTH // len(PALETTE)
                selected_idx = x1 // box_w
                if selected_idx < len(PALETTE) and time.time() - last_selection_time > 0.35:
                    draw_color = PALETTE[selected_idx]["color"]
                    last_selection_time = time.time()
        elif len(fingers) >= 2 and fingers[0] and fingers[1] and not fingers[2] and not fingers[3]:
            clear_timer = 0
            prev_x, prev_y = 0, 0

            pinch_dist = int(np.hypot(x1 - x0, y1 - y0))
            brush_size = int(np.interp(pinch_dist, [25, 180], [3, 40]))
            eraser_size = int(np.interp(pinch_dist, [25, 180], [20, 100]))

            cv2.line(img, (x0, y0), (x1, y1), (255, 255, 0), 2)
            cv2.circle(img, ((x0 + x1) // 2, (y0 + y1) // 2), 6, (0, 255, 255), -1)

        elif len(fingers) >= 2 and fingers[1] and not fingers[2]:
            clear_timer = 0

            if prev_x == 0 and prev_y == 0:
                save_canvas_state()
                draw_x, draw_y = x1, y1
                prev_x, prev_y = x1, y1
            else:
                draw_x = int(SMOOTH_FACTOR * x1 + (1 - SMOOTH_FACTOR) * draw_x)
                draw_y = int(SMOOTH_FACTOR * y1 + (1 - SMOOTH_FACTOR) * draw_y)

            if shape_mode is None:
                cv2.circle(img, (draw_x, draw_y), 6, (255, 255, 255), -1)
                cv2.circle(img, (draw_x, draw_y), brush_size + 4, draw_color, 2)

                if draw_color == (0, 0, 0):
                    cv2.line(canvas, (prev_x, prev_y), (draw_x, draw_y), draw_color, eraser_size)
                else:
                    cv2.line(canvas, (prev_x, prev_y), (draw_x, draw_y), draw_color, brush_size)
            else:
                if shape_start is None:
                    save_canvas_state()
                    shape_start = (draw_x, draw_y)
                shape_end = (draw_x, draw_y)
                draw_shape(img, shape_mode, shape_start, shape_end, draw_color, brush_size)

            prev_x, prev_y = draw_x, draw_y

        else:
            if shape_start is not None and shape_end is not None:
                draw_shape(canvas, shape_mode, shape_start, shape_end, draw_color, brush_size)
                shape_start = None
                shape_end = None
            clear_timer = 0
            prev_x, prev_y = 0, 0
    else:
        if shape_start is not None and shape_end is not None:
            draw_shape(canvas, shape_mode, shape_start, shape_end, draw_color, brush_size)
            shape_start = None
            shape_end = None
        clear_timer = 0
        clear_done = False
        prev_x, prev_y = 0, 0

    if not show_camera:
        img = np.full_like(img, (245, 245, 245))
        if show_grid:
            for grid_x in range(0, WIDTH, 40):
                cv2.line(img, (grid_x, 0), (grid_x, HEIGHT), (220, 220, 220), 1)
            for grid_y in range(0, HEIGHT, 40):
                cv2.line(img, (0, grid_y), (WIDTH, grid_y), (220, 220, 220), 1)

    if show_canvas:
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)

        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, canvas)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time

    render_ui(img, draw_color, brush_size, fps)

    cv2.imshow("Air Canvas Studio Pro [Vision AI]", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        save_canvas_state()
        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    elif key == ord('z'):
        undo_canvas()
        prev_x, prev_y = 0, 0
    elif key == ord('y'):
        redo_canvas()
        prev_x, prev_y = 0, 0
    elif key == ord('b'):
        show_camera = not show_camera
    elif key == ord('g'):
        show_grid = not show_grid
    elif key == ord('v'):
        show_canvas = not show_canvas
    elif key == ord('l'):
        shape_mode = "line"
    elif key == ord('r'):
        shape_mode = "rectangle"
    elif key == ord('o'):
        shape_mode = "circle"
    elif key == ord('n'):
        shape_mode = None
    elif key == ord('s'):
        filename = f"canvas_{int(time.time())}.png"
        cv2.imwrite(filename, canvas)
        print(f"[+] Saved screenshot as: {filename}")
    elif key == ord('p'):
        filename = f"canvas_{int(time.time())}_transparent.png"
        save_transparent_png(filename)
        print(f"[+] Saved transparent PNG as: {filename}")
    elif key == ord('j'):
        filename = f"canvas_{int(time.time())}_white.jpg"
        save_white_jpg(filename)
        print(f"[+] Saved white-background JPG as: {filename}")

cap.release()
cv2.destroyAllWindows()
