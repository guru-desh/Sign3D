import cv2
import os

def get_available_ports(num):
    ports = []
    for i in range(num):
        cap = cv2.VideoCapture('/dev/video' + str(i))
        if cap.isOpened():
            filename = 'feeds/camera' + str(i) + '.avi'
            fourcc = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
            ports.append((i, fourcc))
    return ports

def setup_cam(ports):
    cap_obj = []
    for port in ports:
        file = '/dev/video' + str(port[0])
        cap = cv2.VideoCapture('/dev/video' + str(port[0]))
        cap_obj.append((cap, port[1]))
    return cap_obj

def make_frames(caps):
    rets = []
    frames = []
    recording = []
    for cap in caps:
        assert cap[0].isOpened()
        ret, frame = cap[0].read()
        rets.append(ret)
        frames.append(frame)
        recording.append(cap[0])
    return rets, frames, recording

def show_frames(frames, recording):
    for i, frame in enumerate(frames):
        str_frame = 'frame' + str(i)
        cv2.imshow(winname = str_frame, mat = frame)
        recording[i].write(frame)

       
if __name__ == "__main__":
    if not os.path.exists('feeds'):
        os.makedirs('feeds')
    ports = get_available_ports(1000)
    cap_objs = setup_cam(ports)
    ready = input("Ready to Record.")
    while True:
        rets, frames, recording = make_frames(cap_objs)
        show_frames(frames, recording)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()