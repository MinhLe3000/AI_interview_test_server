# AI-Powered Interview Question Generator & Evaluation System

An intelligent system that generates personalized interview questions from CV files using Google Gemini AI and provides automated evaluation of candidate responses.

## 🚀 Features

- **CV Processing**: Supports both PDF and image formats (PNG, JPG, JPEG, BMP, TIFF)
- **Smart Question Generation**: Creates 9 tailored interview questions based on CV content and job requirements
- **Interactive Interview**: Conducts real-time interviews with candidates
- **AI-Powered Evaluation**: Automatically scores responses across multiple criteria
- **Multi-language Support**: Vietnamese and English interface support
- **Flexible Job Levels**: Supports Intern, Fresher, Junior, Senior, and Lead levels

## 📋 System Overview

The system consists of three main components:

1. **Question Generator** (`generate_questions.py`) - Extracts CV content and generates interview questions
2. **Interactive Interview** (`ask.py`) - Conducts the actual interview session
3. **Response Evaluator** (`evaluate.py`) - Scores candidate responses using AI

## 🛠️ Prerequisites

- **Python 3.9+**
- **Google Gemini API Key** - Get yours from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Tesseract OCR** - For text extraction from images and PDFs

## 🔧 Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd interview-ai-main
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
# Copy the template
cp env_template.txt .env

# Edit .env file and add your API key
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**⚠️ Security Note:** Never commit the `.env` file to version control. It's already included in `.gitignore`.

### Installing Tesseract OCR

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

## 📦 Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Generate_questions_Altered
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Optional: Install PDF processing dependencies:**
```bash
# For enhanced PDF processing
pip install pdf2image
# Install poppler for pdf2image
# macOS: brew install poppler
# Ubuntu: sudo apt-get install poppler-utils
```

2. **Place CV files:**
Put your CV files (PDF or images) in the `CV/` directory.

## 🎯 Usage

### Step 1: Generate Interview Questions

Generate personalized interview questions from CV files:

```bash
# Basic usage
python generate_questions.py --job "Data Scientist" --level "Senior"

# With custom directories
python generate_questions.py --job "Software Engineer" --level "Junior" --cv_dir CV --out interview_question

# Interactive mode (if parameters not provided)
python generate_questions.py
```

**Parameters:**
- `--job`: Target job position (e.g., "Data Scientist", "Software Engineer")
- `--level`: Candidate level ("Intern", "Fresher", "Junior", "Senior", "Lead")
- `--cv_dir`: Directory containing CV files (default: "CV")
- `--out`: Output directory for generated questions (default: "interview_question")

**Output:** JSON file with 9 structured interview questions in `interview_question/` directory.

### Step 2: Conduct Interactive Interview

Run the interview session with generated questions:

```bash
python ask.py
```

The script will:
- Automatically find the latest generated questions file
- Prompt for candidate name
- Present each question sequentially
- Record responses with timestamps
- Save results to `outputs/interview_logs/`

### Step 3: Evaluate Responses

Score candidate responses using AI evaluation:

```bash
# Chấm điểm tất cả file phỏng vấn trong interview_logs
cd src/interview
python evaluate.py

```

**Features:**
- ✨ **Tự động xử lý tất cả file**: Script sẽ tự động tìm và chấm điểm tất cả file JSON trong `outputs/interview_logs/`
- 🔍 **Thông báo tiến trình**: Hiển thị danh sách file được tìm thấy và tiến trình xử lý
- 🛡️ **Xử lý lỗi**: Tiếp tục xử lý file khác nếu một file gặp lỗi
- 📊 **Kết quả riêng biệt**: Mỗi file phỏng vấn sẽ có file kết quả chấm điểm riêng
- 🎯 **Đánh giá tổng thể**: AI phân tích toàn bộ cuộc phỏng vấn để đưa ra đánh giá tổng thể, điểm mạnh, điểm cần cải thiện và khuyến nghị tuyển dụng

**Evaluation Criteria:**
- **Correctness**: Accuracy compared to expected key points
- **Coverage**: How many key points were addressed
- **Reasoning**: Logical explanation and argumentation
- **Creativity**: Examples and unique expressions
- **Communication**: Clarity and coherence
- **Attitude**: Positive or negative attitude

**Output:** Detailed scoring results saved to `outputs/evaluate_results/`

**Kết quả bao gồm:**
- **Điểm từng câu hỏi**: Chi tiết điểm số cho từng câu trả lời
- **Điểm trung bình**: Điểm trung bình của toàn bộ cuộc phỏng vấn
- **Đánh giá tổng thể**: Phân tích AI về điểm mạnh, điểm cần cải thiện
- **Khuyến nghị tuyển dụng**: Gợi ý về việc có nên tuyển dụng ứng viên hay không

## 📁 Project Structure

```
Generate_questions_Altered/
├── CV/                          # Input CV files
├── CV mẫu/                      # Sample CV images
├── interview_question/          # Generated interview questions
│   └── *.questions.json        # Question files
├── outputs/
│   ├── interview_logs/         # Interview session recordings
│   └── evaluate_results/      # AI evaluation results
├── generate_questions.py       # Question generation script
├── ask.py                      # Interactive interview script
├── evaluate.py                 # Response evaluation script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Technical Details

### Question Generation Process

1. **Text Extraction**: 
   - PDFs: Uses `pypdf` for text extraction, falls back to OCR if needed
   - Images: Uses Tesseract OCR for text recognition
   - Fallback: Direct image analysis with Gemini Vision API

2. **Question Structure**:
   - **Questions 1-3**: Opening questions (self-introduction, strengths/weaknesses, motivation)
   - **Questions 4-5**: Behavioral questions (teamwork, challenges, motivation)
   - **Questions 6-8**: Technical questions (tailored to job and seniority level)
   - **Questions 9-10**: CV-based questions (specific project experience)
   - **Question 11**: Creative/hypothetical scenario

3. **AI Models**: Uses Google Gemini 2.5 Flash for both text and vision processing

### Supported File Formats

- **Images**: PNG, JPG, JPEG, BMP, TIFF, TIF
- **Documents**: PDF

### Output Formats

- **Questions**: JSON format with structured question data
- **Interviews**: JSON format with timestamps and responses
- **Evaluations**: JSON format with detailed scoring breakdown

## 🚨 Troubleshooting

### Common Issues

1. **"Missing GEMINI_API_KEY"**
   - Ensure your `.env` file contains a valid API key
   - Check that the key has proper permissions

2. **"TesseractNotFoundError"**
   - Install Tesseract OCR following the platform-specific instructions
   - Ensure Tesseract is in your system PATH

3. **"No supported CV files found"**
   - Check that CV files are in the correct directory
   - Verify file extensions are supported

4. **"Model did not return valid JSON"**
   - The AI response will be saved as `.raw.txt` for inspection
   - Try running the generation again

### Performance Tips

- For large PDFs, consider using `pdf2image` for better OCR results
- Ensure good image quality for better text extraction
- Use specific job titles and levels for more targeted questions

## 📊 Example Output

### Generated Questions Structure
```json
[
  {
    "id": 1,
    "question": "Hãy giới thiệu bản thân và trình bày về kinh nghiệm làm việc của bạn.",
    "category": "opening",
    "purpose": "Đánh giá khả năng trình bày và tự tin"
  },
  {
    "id": 2,
    "question": "Khi làm việc với Data Science ở cấp Senior, bạn sẽ thiết kế một hệ thống ML pipeline như thế nào để đảm bảo scalability và maintainability?",
    "category": "technical",
    "purpose": "Đánh giá kiến thức kỹ thuật và khả năng thiết kế hệ thống",
    "focus": "ML pipeline design"
  }
]
```

### Evaluation Results Structure
```json
{
  "summary": {
    "candidate_name": "John Doe",
    "interview_date": "2024-01-15 14:30:00",
    "average_overall_score": 78.5,
    "questions_scored": 9
  },
  "details": {
    "1": {
      "correctness": 8,
      "coverage": 7,
      "reasoning": 6,
      "creativity": 5,
      "communication": 9,
      "attitude": 10,
      "overall_score": 75,
      "feedback": "Ứng viên trình bày rõ ràng nhưng cần cải thiện phần ví dụ cụ thể..."
    }
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful language processing
- Tesseract OCR for text extraction capabilities
- The open-source community for various Python libraries

---

**Note**: This system is designed for educational and assessment purposes. Always ensure compliance with data privacy regulations when processing candidate information.