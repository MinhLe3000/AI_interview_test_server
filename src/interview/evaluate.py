import google.generativeai as genai
import json
import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Missing GEMINI_API_KEY in environment/.env")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-2.5-flash")  

def score_answer(answer, question, expected_points=None):
    """
    Gửi dữ liệu đến API Gemini để chấm điểm câu trả lời và trả về kết quả JSON.
    """
    expected_points_str = "(không cung cấp)" if not expected_points else str(expected_points)
    prompt = f"""
Bạn là một giám khảo phỏng vấn kỹ thuật AI. Hãy trả lời hoàn toàn bằng **tiếng Việt**.

Câu hỏi phỏng vấn: {question}
Các ý chính mong đợi (Expected Key Points): {expected_points_str}
Câu trả lời của ứng viên: {answer}

Hãy chấm điểm theo các tiêu chí sau:

- correctness: mức độ chính xác so với các ý chính.
- coverage: bao nhiêu ý chính đã được nhắc đến.
- reasoning: có giải thích logic, đưa ra lập luận hay không.
- creativity: có đưa ví dụ hoặc cách diễn đạt riêng không.
- communication: cách trình bày có rõ ràng, mạch lạc không.
- attitude: thái độ tích cực hay tiêu cực.

⚠️ YÊU CẦU QUAN TRỌNG:

- Trả về **đúng định dạng JSON hợp lệ**.
- Không dùng code block (không dùng ```).
- Không dùng "x/10", chỉ dùng số nguyên.
- Không thêm ký tự hoặc text ngoài JSON.

Ví dụ đúng:

{{
 "correctness": 8,
 "coverage": 7,
 "reasoning": 5,
 "creativity": 4,
 "communication": 9,
 "attitude": 10,
 "overall_score": 78,
 "feedback": "Ứng viên trả lời đúng phần lớn ý chính nhưng còn thiếu chi tiết về vai trò của Controller..."
}}
"""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        # Dọn dẹp các ký tự không mong muốn
        raw = raw.replace("```json", "").replace("```", "")
        raw = re.sub(r"(\d+)\/\d+", r"\1", raw)
        
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️ Không thể phân tích JSON từ AI. Dữ liệu thô:\n{raw}")
        return None
    except Exception as e:
        print(f"Lỗi xảy ra khi gọi API: {e}")
        return None

# --- HÀM MỚI ---
def get_overall_feedback(full_interview_log, candidate_name, job_title):
    """
    Gửi toàn bộ nội dung phỏng vấn để AI đưa ra đánh giá tổng thể.
    """
    prompt = f"""
Bạn là một Trưởng phòng Nhân sự (HR Manager) giàu kinh nghiệm, chuyên tổng kết và đánh giá sau phỏng vấn. Hãy trả lời hoàn toàn bằng **tiếng Việt**.

Dưới đây là toàn bộ phần hỏi-đáp của ứng viên **{candidate_name}** cho vị trí **{job_title}**.

--- BẮT ĐẦU NỘI DUNG PHỎNG VẤN ---
{full_interview_log}
--- KẾT THÚC NỘI DUNG PHỎNG VẤN ---

Dựa vào toàn bộ cuộc trao đổi, hãy đưa ra đánh giá tổng thể.

⚠️ YÊU CẦU QUAN TRỌNG:

- Trả về **đúng định dạng JSON hợp lệ**.
- Không dùng code block (không dùng ```).
- Không thêm bất kỳ văn bản nào khác ngoài đối tượng JSON.

Cấu trúc JSON mong muốn:
{{
  "overall_score": <số nguyên từ 0-100, đánh giá chung về mức độ phù hợp>,
  "strengths": "<Một đoạn văn ngắn nêu các điểm mạnh nổi bật của ứng viên trong buổi phỏng vấn>",
  "weaknesses": "<Một đoạn văn ngắn chỉ ra các điểm ứng viên cần cải thiện hoặc các mặt còn thiếu sót>",
  "hiring_recommendation": "<Một câu chốt đề xuất: 'Rất khuyến khích', 'Có tiềm năng, cân nhắc cho vòng sau', hoặc 'Không phù hợp'>"
}}
"""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        raw = raw.replace("```json", "").replace("```", "")
        
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️ Không thể phân tích JSON từ AI (lỗi đánh giá tổng thể). Dữ liệu thô:\n{raw}")
        return None
    except Exception as e:
        print(f"Lỗi xảy ra khi gọi API (đánh giá tổng thể): {e}")
        return None

def main(input_filepath):
    """
    Hàm chính để đọc tệp đầu vào, xử lý và ghi kết quả ra tệp đầu ra.
    """
    # --- 1. Đọc dữ liệu đầu vào ---
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp '{input_filepath}'.")
        return
    except json.JSONDecodeError as e:
        print(f"Lỗi: Tệp JSON đầu vào không hợp lệ. Chi tiết: {e}")
        return

    # --- 2. Xử lý và chấm điểm ---
    results = {}
    print(f"Bắt đầu chấm điểm cho tệp: {os.path.basename(input_filepath)}")

    # Hai định dạng đầu vào được hỗ trợ:
    # A) Định dạng cũ: {question, expected_key_points, candidate_answers}
    # B) Định dạng interview_logs: {candidate_name, interview_date, responses: [{id, question, response, ...}]}
    if isinstance(data, dict) and "responses" in data:
        # Định dạng interview_logs: chấm điểm từng câu trả lời
        responses = data.get("responses", [])
        per_question_results = {}
        for item in responses:
            qid = item.get("id")
            qtext = item.get("question", "")
            ans = item.get("response", "")
            print(f"Đang chấm điểm câu hỏi #{qid}...")
            res = score_answer(ans, qtext, None)
            if res:
                per_question_results[str(qid)] = res
        # Tính điểm tổng hợp đơn giản (trung bình overall_score nếu có)
        overall_scores = [v.get("overall_score", 0) for v in per_question_results.values() if isinstance(v.get("overall_score", None), (int, float))]
        summary = {
            "candidate_name": data.get("candidate_name"),
            "interview_date": data.get("interview_date"),
            "average_overall_score": round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0,
            "questions_scored": len(per_question_results)
        }
        
        # --- ĐÁNH GIÁ TỔNG THỂ ---
        print("Đang tạo đánh giá tổng thể...")
        
        # Tạo chuỗi nội dung phỏng vấn đầy đủ
        full_interview_log = ""
        for item in responses:
            qid = item.get("id")
            question = item.get("question", "")
            answer = item.get("response", "")
            full_interview_log += f"Câu hỏi {qid}: {question}\n"
            full_interview_log += f"Trả lời: {answer}\n\n"
        
        # Lấy thông tin ứng viên và vị trí
        candidate_name = data.get("candidate_name", "Ứng viên")
        candidate_id = data.get("id", "N/A")
        job_title = "Vị trí ứng tuyển"  # Có thể cải thiện bằng cách lưu job_title trong file interview
        
        # Gọi AI để đánh giá tổng thể
        overall_feedback = get_overall_feedback(full_interview_log, candidate_name, job_title)
        
        if overall_feedback:
            summary["overall_feedback"] = overall_feedback
            print("✅ Đã tạo đánh giá tổng thể")
        else:
            print("⚠️ Không thể tạo đánh giá tổng thể")
            summary["overall_feedback"] = {
                "overall_score": summary["average_overall_score"],
                "strengths": "Không thể đánh giá",
                "weaknesses": "Không thể đánh giá", 
                "hiring_recommendation": "Cần xem xét thêm"
            }
        results = {
            "summary": summary,
            "details": per_question_results
        }
    else:
        # Định dạng cũ
        try:
            question = data["question"]
            expected_key_points = data.get("expected_key_points", None)
            candidate_answers = data["candidate_answers"]
        except (KeyError) as e:
            print(f"Lỗi: Tệp JSON đầu vào không hợp lệ hoặc thiếu khóa cần thiết. Chi tiết: {e}")
            return
        for name, ans in candidate_answers.items():
            print(f"Đang chấm điểm cho {name}...")
            result = score_answer(ans, question, expected_key_points)
            if result:
                results[name] = result
            else:
                print(f"⚠️ Bỏ qua {name} do phản hồi không hợp lệ.")

    # --- 3. Sắp xếp kết quả ---
    sorted_ranking = sorted(results.items(), key=lambda x: x[1].get("overall_score", 0), reverse=True)

    # --- 4. Hiển thị kết quả tóm tắt trên Console ---
    print("\n=== BẢNG ĐIỂM ===")
    
    # Hiển thị kết quả theo định dạng khác nhau
    if isinstance(results, dict) and "summary" in results:
        # Định dạng interview_logs với đánh giá tổng thể
        summary = results["summary"]
        candidate_name = summary.get("candidate_name", "Ứng viên")
        avg_score = summary.get("average_overall_score", 0)
        
        print(f"Ứng viên: {candidate_name}")
        print(f"Điểm trung bình: {avg_score} / 100")
        print(f"Số câu hỏi đã chấm: {summary.get('questions_scored', 0)}")
        
        # Hiển thị đánh giá tổng thể nếu có
        if "overall_feedback" in summary:
            feedback = summary["overall_feedback"]
            print(f"\n=== ĐÁNH GIÁ TỔNG THỂ ===")
            print(f"Điểm tổng thể: {feedback.get('overall_score', 'N/A')} / 100")
            print(f"Điểm mạnh: {feedback.get('strengths', 'N/A')}")
            print(f"Điểm cần cải thiện: {feedback.get('weaknesses', 'N/A')}")
            print(f"Khuyến nghị: {feedback.get('hiring_recommendation', 'N/A')}")
    else:
        # Định dạng cũ
        for name, result in sorted_ranking:
            score = result.get("overall_score", 0)
            print(f"{name}: {score} / 100")

    # --- 5. Ghi kết quả chi tiết ra tệp JSON ---
    # Lưu dưới thư mục outputs/evaluate_results của dự án (từ thư mục gốc)
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent.parent / "outputs" / "evaluate_results"
    os.makedirs(str(output_dir), exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

    # Tạo tên tệp đầu ra dựa trên tệp đầu vào
    base_name = os.path.basename(input_filepath)
    file_name_without_ext = os.path.splitext(base_name)[0]
    output_filename = f"{file_name_without_ext}_results.json"
    output_filepath = os.path.join(str(output_dir), output_filename)

    # Chuyển đổi danh sách đã sắp xếp thành từ điển để lưu trữ
    final_results_dict = dict(sorted_ranking)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(final_results_dict, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Đã lưu kết quả chi tiết vào: {output_filepath}")

def process_all_interview_logs():
    """
    Xử lý tất cả các file JSON trong thư mục interview_logs
    """
    script_dir = Path(__file__).parent
    interview_logs_dir = script_dir.parent.parent / "outputs" / "interview_logs"
    
    if not interview_logs_dir.exists():
        print(f"❌ Lỗi: Không tìm thấy thư mục interview_logs: {interview_logs_dir}")
        return
    
    # Tìm tất cả file JSON trong thư mục interview_logs
    json_files = list(interview_logs_dir.glob("*.json"))
    
    if not json_files:
        print(f"❌ Không tìm thấy file JSON nào trong thư mục: {interview_logs_dir}")
        return
    
    print(f"🔍 Tìm thấy {len(json_files)} file JSON để chấm điểm:")
    for file in json_files:
        print(f"   - {file.name}")
    
    print("\n" + "="*60)
    print("         BẮT ĐẦU CHẤM ĐIỂM TẤT CẢ FILE")
    print("="*60)
    
    # Xử lý từng file
    for json_file in json_files:
        print(f"\n📝 Đang xử lý: {json_file.name}")
        print("-" * 40)
        try:
            main(str(json_file))
            print(f"✅ Hoàn thành: {json_file.name}")
        except Exception as e:
            print(f"❌ Lỗi khi xử lý {json_file.name}: {e}")
    
    print("\n" + "="*60)
    print("         KẾT THÚC CHẤM ĐIỂM TẤT CẢ FILE")
    print("="*60)

if __name__ == "__main__":
    process_all_interview_logs()