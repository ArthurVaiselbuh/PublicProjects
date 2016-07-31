#motion_detection V2.
import argparse
import cv2
import logging
import datetime
from ConfigParser import SafeConfigParser
from event import Event

def _generate_args():
    """
    Generate args from command line arguments.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True,
        help="path to the .ini configuration file")
    ap.add_argument("-v", "--verbose", action="store_true")
    return ap.parse_args()

class MotionCam(object):
    def __init__(self, args):
        self._camera = cv2.VideoCapture(0)
        self.motion = Event()
        #get capture args
        self._camera.set(cv2.cv.CV_CAP_PROP_FPS, args.getint("capture", "fps"))
        self._camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, args.getint("capture", "resolution_x"))
        self._camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, args.getint("capture", "resolution_y"))
        self._min_area = args.getint("capture", 'min_area')

        #detection
        self._min_motion_frames = args.getint("detection", 'min_motion_frames')
        self._delta_thresh = args.getfloat("detection", "delta_thresh")

        #notifications
        self._notify_delta = args.getfloat("notify", "notify_delta")

        #general        
        self.show_video = args.getboolean("general", "show_video")
        self._warmup = args.getint("detection", "warmup_frames")

        self.occupied = False

    def exec_(self):
        """
        Enter the main loop
        """
        #warm camera up(let it adjust to light and such):
        for i in xrange(self._warmup):
            print "warming up", i
            self._camera.read()
        #How many frames in a row werent captured:
        error_frames = 0
        motion_counter = 0
        self._last_emit = datetime.datetime.now()
        #Average background
        avg = None

        while True:
            (grabbed, frame) = self._camera.read()

            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if not grabbed:
                error_frames += 1
                if error_frames > 3:
                    logging.warning("Error grabbing image in more than 3 frames in a row.")
                if error_frames > 20:
                    logging.critical("Error in grabbing over 20 frames. Stopping.")
                    break
                continue
            error_frames = 0
            timestamp = datetime.datetime.now()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
         
            # if the average frame is None, initialize it
            if avg is None:
                logging.info("Starting background model...")
                avg = gray.copy().astype("float")
                continue
         
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta, self._delta_thresh, 255,
                cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
         
            # loop over the contours
            self.occupied = False
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self._min_area:
                    continue
         
                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.occupied = True
         
            # draw the text and timestamp on the frame
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            text = "Occupied" if self.occupied else "Unoccupied"
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)
            # check to see if the room is occupied
            if self.occupied:
                # check to see if enough time has passed between uploads
                if (timestamp - self._last_emit).seconds >= self._notify_delta:
                    # increment the motion counter
                    motion_counter += 1
         
                    # check to see if the number of frames with consistent motion is
                    # high enough
                    if motion_counter >= self._min_motion_frames:
                        if True:#Change to notify
                            # write the image to temporary file
                            #t = TempImage()
                            #cv2.imwrite(t.path, frame)
                            self.motion.emit()
         
                        # update the last uploaded timestamp and reset the motion counter
                        self._last_emit = datetime.datetime.now()
                        motion_counter = 0
         
            # otherwise, the room is not occupied
            else:
                motion_counter = 0
                # accumulate the weighted average between the current frame and
                # previous frames, then compute the difference between the current
                # frame and running average
                # only do this for non accupied frames, so avg will represent average background
                cv2.accumulateWeighted(gray, avg, 0.5)
            # check to see if the frames should be displayed to screen
            if self.show_video:
                # display the security feed
                cv2.imshow("Security Feed", frame)
                cv2.imshow("Thresh", thresh)
                cv2.imshow("Frame Delta", frameDelta)
                cv2.imshow("Average", avg)
                key = cv2.waitKey(1) & 0xFF
         
                # if the `q` key is pressed, break from the lop
                if key == ord("q"):
                    break
            


def main():
    args = _generate_args()
    cp = SafeConfigParser()
    cp.read(args.conf)
    #cp.read(r"c:\users\arthur\documents\python scripts\motion_detection\config.ini")
    #configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(filename="motionV2.log", level=level)
    camera = MotionCam(cp)

    def on_motion():
        print "motion!"

    camera.motion.connect(on_motion)
    camera.exec_()


if __name__ == '__main__':
    main()


