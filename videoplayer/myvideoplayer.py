#! /usr/bin/env python3

import threading
import cv2

# Bounded buffer to hold frames
class BoundedBuffer:
    def __init__(self, size):
        self.buffer = []
        self.size = size
        self.mutex = threading.Lock()
        self.empty = threading.Semaphore(size)
        self.full = threading.Semaphore(0)

    #producer adds frame to the buffer
    def put(self, frame):
        self.empty.acquire() #wait for space
        self.mutex.acquire() #acquire lock
        self.buffer.append(frame) #add frame to buffer
        self.mutex.release() # release lock
        self.full.release() # signal the buffer isn't empty

    #consumer retrieves a frame from buffer
    def get(self):
        self.full.acquire() #wait for frame to become available
        self.mutex.acquire() #acquire the lock
        frame = self.buffer.pop(0) #get first frame
        self.mutex.release() #release the lock
        self.empty.release() # signale buffer no longer full
        return frame

# Global variables where the buffer size is 60
# as far as I know this is arbitrary at most
# made it 60 because most films are 60 frames/sec
extracted_frames = BoundedBuffer(60)
grayscale_frames = BoundedBuffer(60)

# let's extract the frames!!!
def extract_frames():
    cap = cv2.VideoCapture('clip.mp4') #python make video variable
    while cap.isOpened():
        ret, frame = cap.read() #get frame from bugger
        if not ret: #when frames are all processed the break
            break
        extracted_frames.put(frame)
    extracted_frames.put(None)  # Signal end of frames
    cap.release()

# Function to convert frames to grayscale
def convert_to_grayscale():
    while True:
        frame = extracted_frames.get() #get frame from buffer
        if frame is None:  # Break when all frames are processed
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grayscale_frames.put(gray_frame) #put the grayscale in the buffer now

# Function to display frames
def display_frames():
    while True:
        gray_frame = grayscale_frames.get() #get the gray scae from the buffer
        if gray_frame is None:  # Break when all frames are processed
            break
        cv2.imshow('Hurdle Burp The Rabbit', gray_frame) #display the grayscalled frame
        #42 is the answer to life, love, happiness, everything
        if cv2.waitKey(42) & 0xFF == ord('q'):
            break
    
    #this is present in the last code to close the windows
    cv2.destroyAllWindows()

# Start threads this way we can
extract_thread = threading.Thread(target=extract_frames)
convert_thread = threading.Thread(target=convert_to_grayscale)
display_thread = threading.Thread(target=display_frames)

#start each thread~
extract_thread.start()
convert_thread.start()
display_thread.start()

# Join threads
extract_thread.join() #wait to finish
convert_thread.join() #wait to finish
display_thread.join() #wait to finish... hopefully no race conditions
