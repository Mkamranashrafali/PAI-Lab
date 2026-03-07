from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os, cv2, numpy, folium, uuid
from datetime import datetime
from scanner import WildlifeScanner

web = Flask(__name__)
web.config['UPLOAD_FOLDER'] = 'uploads'
web.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

OK_EXT = ('png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov')
engine = WildlifeScanner()

def valid_ext(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in OK_EXT

def make_map(lt, lg, cnt, nm):
    mp = folium.Map(location=[lt, lg], zoom_start=12)
    folium.Marker([lt, lg], popup='Count: ' + str(cnt), tooltip=nm).add_to(mp)
    folium.Circle([lt, lg], radius=500, color='blue', fill=True).add_to(mp)
    return mp._repr_html_()

@web.route('/')
def main_page():
    return render_template('index.html')

@web.route('/api/detect', methods=['POST'])
def process():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file'}), 400
        
        f = request.files['file']
        lt = float(request.form.get('latitude', 40.7128))
        lg = float(request.form.get('longitude', -74.0060))
        
        if f.filename == '' or not valid_ext(f.filename):
            return jsonify({'success': False, 'error': 'Bad file'}), 400
        
        fn = secure_filename(f.filename)
        save_name = str(uuid.uuid4())[:8] + '_' + fn
        path = os.path.join(web.config['UPLOAD_FOLDER'], save_name)
        
        os.makedirs(web.config['UPLOAD_FOLDER'], exist_ok=True)
        f.save(path)
        
        ext = fn.split('.')[-1].lower()
        
        if ext in ('mp4', 'avi', 'mov'):
            vid_out = os.path.join(web.config['UPLOAD_FOLDER'], 'out_' + save_name.replace(ext, 'mp4'))
            done, data, method, types = engine.scan_video(path, vid_out)
            
            if not done:
                return jsonify({'success': False, 'error': 'Failed'}), 500
            
            total = sum(d['count'] for d in data)
            top = max(types, key=types.get) if types else "N/A"
            avg = sum(m['confidence'] for d in data for m in d.get('members', [])) / max(1, sum(len(d.get('members', [])) for d in data))
            
            return jsonify({
                'success': True,
                'animal_count': total,
                'video_path': 'uploads/' + os.path.basename(vid_out),
                'map': make_map(lt, lg, total, fn),
                'timestamp': datetime.now().isoformat(),
                'detection_method': method,
                'confidence': round(avg, 3),
                'species_breakdown': types,
                'dominant_species': top,
                'herd_density': 'Low' if total < 5 else 'Medium' if total < 15 else 'High',
                'location': {'lat': lt, 'lng': lg}
            })
        
        else:
            img, items, method, types = engine.scan_image(path)
            
            if img is None:
                return jsonify({'success': False, 'error': 'Failed'}), 400
            
            img_out = os.path.join(web.config['UPLOAD_FOLDER'], 'out_' + save_name)
            cv2.imwrite(img_out, img)
            
            cnt = len(items)
            top = max(types, key=types.get) if types else "None"
            avg = sum(i['confidence'] for i in items) / max(1, cnt)
            
            return jsonify({
                'success': True,
                'animal_count': cnt,
                'image_path': 'uploads/' + os.path.basename(img_out),
                'map': make_map(lt, lg, cnt, fn),
                'timestamp': datetime.now().isoformat(),
                'detection_method': method,
                'confidence': round(avg, 3),
                'species_breakdown': types,
                'dominant_species': top,
                'herd_density': 'Low' if cnt < 3 else 'Medium' if cnt < 8 else 'High',
                'location': {'lat': lt, 'lng': lg}
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@web.route('/uploads/<name>')
def get_file(name):
    from flask import send_file
    return send_file(os.path.join(web.config['UPLOAD_FOLDER'], name))

if __name__ == '__main__':
    web.run(debug=True, port=3000)
