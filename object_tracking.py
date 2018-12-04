import argparse
import cv2
import dlib

# drag and select the roi
def drag_and_select(event, x, y, flags, param):
    global dragging, roi_selected, startX, startY, endX, endY

    if event == cv2.EVENT_LBUTTONDOWN:
        (startX, startY) = (x, y)
        roi_selected = False
        dragging = True
    elif event == cv2.EVENT_LBUTTONUP:
        roi_selected = True
        dragging = False

    (endX, endY) = x, y

ap = argparse.ArgumentParser()
ap.add_argument("-video", "--video", required=True, help="path to input video file")
ap.add_argument("-width", "--width", help="width of the window", default=800)
ap.add_argument("-height", "--height", help="height of the window", default=600)
args = vars(ap.parse_args())

VIDEO_PATH = args['video']
WIN_NAME = 'window'
WIN_WIDTH = int(args['width'])
WIN_HEIGHT = int(args['height'])

roi_selected = False
startX, startY, endX, endY = 0,0,0,0
dragging = False
tracker = dlib.correlation_tracker()
tracking = False
skip_frames = 0
pause_frames = False

cv2.namedWindow(WIN_NAME)
cv2.setMouseCallback(WIN_NAME, drag_and_select)
vs = cv2.VideoCapture(VIDEO_PATH)

while True:
    if not pause_frames:
        skip_frames -= 1
        (ret, frame) = vs.read()

        if frame is None:
            break
        if skip_frames > 0:
            continue

        frame = cv2.resize(frame, (WIN_WIDTH, WIN_HEIGHT), cv2.INTER_AREA)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        draw_frame = frame.copy()

        if roi_selected:
            # track if roi is selected and tracking is turned on
            if tracking:
                tracker.update(rgb)
                pos = tracker.get_position()

                startX = int(pos.left())
                startY = int(pos.top())
                endX = int(pos.right())
                endY = int(pos.bottom())
                cv2.rectangle(draw_frame, (startX, startY), (endX, endY), (0,255,0), 2)
                cv2.putText(draw_frame, 'object', (startX, startY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

    if dragging == True:
        # draw the bounding box if dragging
        draw_frame = frame.copy()
        cv2.rectangle(draw_frame, (startX, startY), (endX, endY), (0,255,0), 2)
        cv2.putText(draw_frame, 'object', (startX, startY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

    cv2.putText(draw_frame, 'Tracking: ' + str(tracking), (10, WIN_HEIGHT - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
    cv2.imshow(WIN_NAME, draw_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        skip_frames = 100
    # toggle pause
    if key == ord('p'):
        if pause_frames is True:
            pause_frames = False
        else:
            pause_frames = True
    # toggle tracking
    if key == ord('t'):
        if tracking == False:
            if roi_selected:
                tracking = True
                rect = dlib.rectangle(startX, startY, endX, endY)
                tracker.start_track(rgb, rect)
        elif tracking == True:
            tracking = False

cv2.destroyAllWindows()
vs.release()

