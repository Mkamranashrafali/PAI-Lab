import cv2, numpy, os, subprocess

class WildlifeScanner:
    ANIMALS = {14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe'}
    
    def __init__(self):
        self.model = cv2.dnn.readNet("models/model.weights", "models/model.cfg")
        with open("models/labels.names") as f:
            self.names = [x.strip() for x in f]
        layers = self.model.getLayerNames()
        self.outputs = [layers[i-1] for i in self.model.getUnconnectedOutLayers()]
        self.method = "YOLO"
    
    def detect(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0,0,0), True, crop=False)
        self.model.setInput(blob)
        outs = self.model.forward(self.outputs)
        
        boxes, confs, classes = [], [], []
        for o in outs:
            for row in o:
                scores = row[5:]
                cid = numpy.argmax(scores)
                c = scores[cid]
                if c > 0.5 and cid in self.ANIMALS:
                    cx, cy = int(row[0]*w), int(row[1]*h)
                    bw, bh = int(row[2]*w), int(row[3]*h)
                    if bw > 15 and bh > 15:
                        boxes.append([cx-bw//2, cy-bh//2, bw, bh])
                        confs.append(float(c))
                        classes.append(cid)
        
        keep = cv2.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)
        return [{'box': boxes[i], 'confidence': confs[i], 'species': self.ANIMALS.get(classes[i], 'unknown')} for i in range(len(boxes)) if i in keep]
    
    def scan_image(self, path):
        img = cv2.imread(path)
        if img is None:
            return None, [], "ERR", {}
        
        items = self.detect(img)
        result = img.copy()
        counts = {}
        
        for d in items:
            x, y, w, h = d['box']
            sp = d['species']
            conf = d['confidence']
            counts[sp] = counts.get(sp, 0) + 1
            
            cv2.rectangle(result, (x, y), (x+w, y+h), (0,255,0), 3)
            cv2.putText(result, sp.upper() + ' ' + str(int(conf*100)) + '%', (x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        cv2.putText(result, 'Total: ' + str(len(items)), (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        return result, items, self.method, counts
    
    def scan_video(self, src, dst):
        vid = cv2.VideoCapture(src)
        if not vid.isOpened():
            return False, [], self.method, {}
        
        fps = int(vid.get(cv2.CAP_PROP_FPS)) or 30
        w = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        tmp = dst.replace('.mp4', '.avi')
        out = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'XVID'), fps, (w, h))
        
        if not out.isOpened():
            vid.release()
            return False, [], self.method, {}
        
        frames = []
        totals = {}
        n = 0
        
        while True:
            ok, frame = vid.read()
            if not ok:
                break
            
            items = self.detect(frame)
            sp_cnt = {}
            
            for d in items:
                x, y, bw, bh = d['box']
                sp = d['species']
                sp_cnt[sp] = sp_cnt.get(sp, 0) + 1
                totals[sp] = totals.get(sp, 0) + 1
                cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0,255,0), 2)
                cv2.putText(frame, sp, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            
            frames.append({'frame': n, 'count': len(items), 'species': sp_cnt, 'members': [{'confidence': d['confidence']} for d in items]})
            out.write(frame)
            n += 1
        
        vid.release()
        out.release()
        
        final = dst if dst.endswith('.mp4') else dst + '.mp4'
        subprocess.run(['ffmpeg', '-i', tmp, '-c:v', 'libx264', '-crf', '28', final, '-y', '-loglevel', 'error'], timeout=600)
        
        if os.path.exists(final):
            try: os.remove(tmp)
            except: pass
            return True, frames, self.method, totals
        return False, [], self.method, {}
