# correlation_object_tracker
Dlib's correlation-based object tracker: http://blog.dlib.net/2015/02/dlib-1813-released.html

The input is a bounding box of the object and then the tracker automatically tracks the object based on the correlation of pixels.

#### NOTE: SELECT THE BOUNDING BOX BY DRAGGING FROM TOP LEFT TO BOTTOM RIGHT OF THE OBJECT, OTHERWISE IT'LL THROW AN ERROR.

## Usage:
Single object tracking:

  `python video_object_track.py -video video.mp4 -width 800 -height 600`
  
Multi object tracking:

  `python multi_video_object_track.py -video video.mp4 -width 800 -height 600`
  
  The default width is 800 and height is 600.
  
  Run the script, press 'p' to pause the video when you want, then select the bounding box(es) by dragging with the mouse and press 't' to start tracking. Press 't' again to stop tracking.
  
## Controls:
  <li> Press 'p' to pause/unpause the video.</li>
  <li> Press 's' to skip frames.</li>
  <li> Press 't' to toggle tracking.</li>
  <li> Press 'q' to quit.</li>
  <li> Drag with mouse to select a bounding box. </li>
