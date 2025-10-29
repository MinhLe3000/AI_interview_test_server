from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import sys

# Import các module từ thư mục src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from interview.generate_questions import process_file, read_env
from interview.ask import run_interactive_interview_from_json
from interview.evaluate import main as evaluate_interview

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Thay đổi trong production

# Cấu hình upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Tạo các thư mục cần thiết
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('outputs/interview_logs', exist_ok=True)
os.makedirs('outputs/evaluate_results', exist_ok=True)
os.makedirs('interview_question', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/upload_cv', methods=['GET', 'POST'])
def upload_cv():
    """Trang upload CV và tạo câu hỏi"""
    if request.method == 'POST':
        # Kiểm tra file upload
        if 'cv_file' not in request.files:
            flash('Không có file được chọn', 'error')
            return redirect(request.url)
        
        file = request.files['cv_file']
        if file.filename == '':
            flash('Không có file được chọn', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Lưu file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Lấy thông tin từ form
            job_title = request.form.get('job_title', '').strip()
            level = request.form.get('level', '').strip()
            
            if not job_title or not level:
                flash('Vui lòng nhập đầy đủ thông tin vị trí và level', 'error')
                return redirect(request.url)
            
            try:
                # Tạo câu hỏi phỏng vấn
                read_env()  # Đọc API key
                output_dir = Path('interview_question')
                output_dir.mkdir(exist_ok=True)
                
                # Tạo tên file output dựa trên file CV thực tế (có UUID)
                base_name = Path(unique_filename).stem
                questions_file = output_dir / f"{base_name}.questions.json"
                
                # Gọi hàm tạo câu hỏi
                from interview.generate_questions import process_file
                process_file(Path(file_path), job_title, level, output_dir)
                
                # Tìm file câu hỏi đã được tạo (có thể có tên khác do UUID)
                actual_questions_file = None
                for file in output_dir.glob("*.questions.json"):
                    if file.stem.startswith(base_name.split('_')[0]):  # Tìm file có UUID tương ứng
                        actual_questions_file = file.name
                        break
                
                if actual_questions_file:
                    questions_file = actual_questions_file
                
                # Kiểm tra file đã được tạo
                if actual_questions_file and (output_dir / actual_questions_file).exists():
                    flash(f'Đã tạo thành công câu hỏi phỏng vấn cho {job_title} - {level}', 'success')
                    return redirect(url_for('interview', questions_file=actual_questions_file))
                else:
                    flash('Có lỗi xảy ra khi tạo câu hỏi phỏng vấn', 'error')
                    
            except Exception as e:
                flash(f'Lỗi: {str(e)}', 'error')
        else:
            flash('File không được hỗ trợ. Vui lòng chọn file PNG, JPG, PDF', 'error')
    
    return render_template('upload_cv.html')

@app.route('/interview')
def interview():
    """Trang phỏng vấn"""
    questions_file = request.args.get('questions_file')
    if not questions_file:
        flash('Không tìm thấy file câu hỏi', 'error')
        return redirect(url_for('index'))
    
    # Đọc câu hỏi từ file
    questions_path = os.path.join('interview_question', questions_file)
    try:
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        return render_template('interview.html', questions=questions, questions_file=questions_file)
    except FileNotFoundError:
        flash('Không tìm thấy file câu hỏi', 'error')
        return redirect(url_for('index'))
    except json.JSONDecodeError:
        flash('File câu hỏi không hợp lệ', 'error')
        return redirect(url_for('index'))

@app.route('/submit_interview', methods=['POST'])
def submit_interview():
    """Xử lý kết quả phỏng vấn"""
    data = request.get_json()
    
    # Tạo file kết quả phỏng vấn
    interview_results = {
        "candidate_name": data.get('candidate_name', 'Anonymous'),
        "id": data.get('candidate_id', 'Anonymous'),
        "interview_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "responses": data.get('responses', [])
    }
    
    # Lưu file kết quả
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"responses_{interview_results['candidate_name'].replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join('outputs/interview_logs', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(interview_results, f, ensure_ascii=False, indent=4)
    
    # Chạy đánh giá
    try:
        evaluate_interview(filepath)
        flash('Phỏng vấn hoàn thành và đã được đánh giá', 'success')
        return jsonify({
            'success': True,
            'message': 'Phỏng vấn hoàn thành',
            'results_file': filename.replace('.json', '_results.json')
        })
    except Exception as e:
        flash(f'Lỗi khi đánh giá: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/results')
def results():
    """Trang hiển thị kết quả"""
    results_dir = 'outputs/evaluate_results'
    results_files = []
    
    if os.path.exists(results_dir):
        for file in os.listdir(results_dir):
            if file.endswith('.json'):
                results_files.append(file)
    
    return render_template('results.html', results_files=results_files)

@app.route('/view_result/<filename>')
def view_result(filename):
    """Xem chi tiết kết quả"""
    try:
        filepath = os.path.join('outputs/evaluate_results', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        return render_template('view_result.html', result=result_data, filename=filename)
    except FileNotFoundError:
        flash('Không tìm thấy file kết quả', 'error')
        return redirect(url_for('results'))
    except json.JSONDecodeError:
        flash('File kết quả không hợp lệ', 'error')
        return redirect(url_for('results'))

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download file"""
    return send_from_directory('outputs/evaluate_results', filename, as_attachment=True)

@app.route('/api/questions/<filename>')
def get_questions(filename):
    """API để lấy câu hỏi"""
    try:
        filepath = os.path.join('interview_question', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        return jsonify(questions)
    except FileNotFoundError:
        return jsonify({'error': 'File không tồn tại'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'File không hợp lệ'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
