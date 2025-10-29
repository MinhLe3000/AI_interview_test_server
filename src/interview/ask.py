import json
import os
from datetime import datetime

def run_interactive_interview_from_json(input_filename="../../interview_question/Tuan_CV_trs.questions.json"):
    """
    Đọc câu hỏi từ file JSON, chạy phỏng vấn tương tác và lưu kết quả.
    """
    
    # 1. Đọc câu hỏi từ file nguồn (cố gắng theo nhiều cách để tránh lỗi path tương đối)
    from pathlib import Path
    script_dir = Path(__file__).parent
    candidates = []
    # 1) Nếu người dùng truyền vào đường dẫn tuyệt đối/tương đối → chuẩn hoá
    if input_filename:
        candidates.append(Path(input_filename).expanduser())
    # 2) Thử path tương đối so với file script (outputs nằm cùng thư mục dự án con)
    try_name = Path(input_filename).name if input_filename else "Tuan_CV_trs.questions.json"
    candidates.append(script_dir.parent.parent / "interview_question" / try_name)
    # 3) Thử path tương đối so với CWD (trường hợp chạy từ gốc workspace)
    candidates.append(Path.cwd() / "interview_question" / try_name)

    questions = None
    last_error = None
    for cand in candidates:
        try:
            with open(cand, 'r', encoding='utf-8') as f:
                questions = json.load(f)
                input_filename = str(cand)
                break
        except FileNotFoundError as e:
            last_error = e
            continue
        except json.JSONDecodeError:
            print(f"❌ LỖI: File '{cand}' không phải là định dạng JSON hợp lệ.")
            return

    if questions is None:
        tried = "\n - ".join(str(p) for p in candidates)
        print(
            "❌ LỖI: Không tìm thấy file câu hỏi ở các vị trí đã thử:\n - " + tried +
            "\nVui lòng chạy BƯỚC 1 để tạo file câu hỏi (generate_questions.py)."
        )
        return

    print("\n" + "="*60)
    print("      BẮT ĐẦU PHỎNG VẤN TƯƠNG TÁC TỪ FILE JSON")
    print("="*60 + "\n")
    
    # Thiết lập thông tin chung cho kết quả
    interview_results = {
        "candidate_name": input("Nhập tên ứng viên (hoặc tên của bạn): ").strip() or "Anonymous",
        "id": input("Nhập id ứng viên: ").strip() or "Anonymous",
        "interview_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "responses": []
    }

    # 2. Lặp và thu thập câu trả lời
    for q_data in questions:
        q_id = q_data.get('id', 'N/A')
        question_text = q_data['question']
        
        print(f"\n--- Câu Hỏi #{q_id} ({q_data.get('category', 'Khác')}) ---")
        print(f"Hỏi: {question_text}")
        
        # Lặp để đảm bảo người dùng nhập nội dung
        while True:
            response = input("Trả Lời: ")
            if response.strip():
                break
            print("Vui lòng nhập câu trả lời (không được để trống).")
            
        # Lưu trữ câu trả lời
        response_entry = q_data.copy() # Sao chép dữ liệu câu hỏi ban đầu
        response_entry['response'] = response # Thêm câu trả lời
        response_entry['time_recorded'] = datetime.now().strftime("%H:%M:%S")
        interview_results['responses'].append(response_entry)

    print("\n" + "="*60)
    print("            KẾT THÚC PHỎNG VẤN")
    print("="*60 + "\n")

    # 3. Lưu Kết Quả vào File JSON
    # Lưu dưới thư mục outputs/interview_logs của dự án (từ thư mục gốc)
    OUTPUT_DIR = str((Path(__file__).parent.parent.parent / "outputs" / "interview_logs").resolve())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"responses_{interview_results['candidate_name'].replace(' ', '_')}_{interview_results['id']}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interview_results, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã lưu thành công {len(questions)} câu trả lời vào file:")
        print(f"   Đường dẫn: {filepath}")
        
    except Exception as e:
        print(f"❌ LỖI trong quá trình lưu file: {e}")

# Chạy BƯỚC 2 để bắt đầu phỏng vấn
if __name__ == "__main__":
    run_interactive_interview_from_json()