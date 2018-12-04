import argparse
import multiprocessing as mp
import cv2
import dlib

# mouse callback to drag and select the bounding box
def drag_and_select(event, x, y, flags, param):
    global dragging, startX, startY, endX, endY

    if event == cv2.EVENT_LBUTTONDOWN:
        (startX, startY) = (x, y)
        dragging = True
    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False

        (endX, endY) = x, y
        boxes.append((startX, startY, endX, endY))
    
    (endX, endY) = x, y

# callback for starting process
def tracker_callback(box, rgb, objectNumber, inputQueue, outputQueue):
    # create and start a tracker
    tracker = dlib.correlation_tracker()
    rect = dlib.rectangle(box[0], box[1], box[2], box[3])
    tracker.start_track(rgb, rect)

    while True:
        rgb = inputQueue.get()
        if rgb is not None:
            tracker.update(rgb)
            pos = tracker.get_position()

            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            
            outputQueue.put((objectNumber, (startX, startY, endX, endY)))

# draw the bounding boxes
def draw_box(frame, x1, y1, x2, y2, objNum):
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
    cv2.putText(frame, 'object {}'.format(objNum), (x1, y1 - 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-video", "--video", required=True, help="path to input video file")
    ap.add_argument("-width", "--width", help="width of the window", default=800)
    ap.add_argument("-height", "--height", help="height of the window", default=600)
    args = vars(ap.parse_args())

    VIDEO_PATH = args['video']
    WIN_NAME = 'window'
    WIN_WIDTH = int(args['width'])
    WIN_HEIGHT = int(args['height'])

    startX, startY, endX, endY = 0,0,0,0
    boxes = []
    dragging = False
    tracking = False
    skip_frames = 0
    pause_frames = False

    inputQueues = []
    outputQueues = []
    last_queue_length = 0

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

            if tracking:
                for iQ in inputQueues:
                    iQ.put(rgb)

                for oQ in outputQueues:
                    (objNum, (x1, y1, x2, y2)) = oQ.get()
                    draw_box(draw_frame, x1, y1, x2, y2, objNum)

                    # update the box's coordinates
                    boxes[objNum] = (x1, y1, x2, y2)

        if dragging is True:
            # draw the bounding box if dragging
            draw_frame = frame.copy()

            # draw all previous boxes
            for i, (x1, y1, x2, y2) in enumerate(boxes):
                draw_box(draw_frame, x1, y1, x2, y2, i)

            # draw the current box that is being dragged
            cv2.rectangle(draw_frame, (startX, startY), (endX, endY), (0,255,0), 2)
            cv2.putText(draw_frame, 'object', (startX, startY - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

        cv2.putText(draw_frame, 'Tracking: ' + str(tracking), (10, WIN_HEIGHT - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
        cv2.imshow(WIN_NAME, draw_frame)

        # handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):
            skip_frames = 100
        if key == ord('p'):
            # toggle pause
            if pause_frames is True:
                pause_frames = False
            else:
                pause_frames = True
        if key == ord('t'):
            # toggle tracking
            if tracking is False:
                tracking = True
                if inputQueues or len(boxes) > last_queue_length:
                    for i, box in enumerate(boxes[last_queue_length:]):
                        i = last_queue_length + i
                        iQ = mp.Queue()
                        oQ = mp.Queue()
                        inputQueues.append(iQ)
                        outputQueues.append(oQ)

                        p = mp.Process(target=tracker_callback, args=(box, rgb, i, iQ, oQ))
                        p.daemon = True
                        p.start()

                last_queue_length = len(inputQueues)

            elif tracking is True:
                tracking = False

    cv2.destroyAllWindows()
    vs.release()
