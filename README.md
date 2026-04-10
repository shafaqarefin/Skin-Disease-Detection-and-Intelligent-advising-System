# 🏥 Skin Disease Analyzer

An AI-powered web application that analyzes skin images and provides disease recommendations using **EfficientNet CV model** combined with **Google Gemini LLM** for intelligent medical insights.

---

## ✨ Features

- 📸 **Image Analysis** - Upload skin images for instant AI analysis
- 🤖 **AI-Powered** - Combines Computer Vision + Large Language Models
- 💬 **Multi-turn Chat** - Ask follow-up questions about your diagnosis
- 👤 **User Authentication** - Secure login/register system
- 📋 **Chat History** - Save and revisit past analysis sessions
- 📱 **Modern UI** - Beautiful responsive interface with Streamlit
- 🐳 **Docker Ready** - Easy deployment with Docker containers

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Testing)

#### Prerequisites
- Python 3.11+
- pip/conda
- Git
- **EfficientNet Models** - Download from [Google Drive](https://drive.google.com/drive/folders/1tReaIM4Gju7Aa64bta5iQT_BmkSNfP2_?usp=sharing) and extract the `model/` folder to the `backend/` directory

#### Download Models
1. Open the [Google Drive link](https://drive.google.com/drive/folders/1tReaIM4Gju7Aa64bta5iQT_BmkSNfP2_?usp=sharing)
2. Download the `model` folder (contains `model_v1.h5`, `model_v2.h5`, `model_v3.h5`)
3. Extract it to your backend directory:
   ```
   backend/
   ├── model/
   │   ├── model_v1.h5
   │   ├── model_v2.h5
   │   └── model_v3.h5
   ```

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API key
echo GEMINI_API_KEY=your_api_key_here > .env

# Run the backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

#### Frontend Setup (in new terminal)
```bash
# Navigate to frontend directory
cd frontend

# Create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
# On Windows Gitbash:
source .\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

The frontend will open at: `http://localhost:8501`

---

### Option 2: Docker Deployment (Production Ready)

⚠️ **Important:** Make sure you've [downloaded the models](#download-models) first and placed them in `backend/model/` before building the Docker image.

#### Build the Image
```bash
cd backend
docker build -t shafaqarefin/skin-disease-api:v1.0 .
```

#### Run with Docker
```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_api_key_here \
  shafaqarefin/skin-disease-api:v1.0
```

#### Push to Docker Hub
```bash
docker login
docker push shafaqarefin/skin-disease-api:v1.0
```

---

## 📖 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "message": "User registered successfully"
}
```

---

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "token": "jwt_token_here"
}
```

---

### Analysis Endpoints

#### Analyze Skin Image
```http
POST /analyze_skin
Content-Type: multipart/form-data

Parameters:
- file: [image file] (Required)
- user_id: 1 (Query parameter, Required)
```

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "disease": "Melanoma",
  "confidence": 0.92,
  "recommendations": "This condition requires immediate professional evaluation. Please consult a dermatologist as soon as possible.",
  "next_steps": "Schedule an appointment with a dermatologist within 1-2 weeks for proper diagnosis and treatment.",
  "tips": "Avoid sun exposure. Use SPF 50+ sunscreen. Monitor changes in size, shape, or color.",
  "system_context": "You are an expert AI dermatology assistant..."
}
```

---

### Chat Endpoints

#### Send Chat Message
```http
POST /chat
Content-Type: application/json

{
  "user_id": 1,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "disease": "Melanoma",
  "confidence": 0.92,
  "message": "Should I see a dermatologist immediately?",
  "history": []
}
```

**Response (200):**
```json
{
  "response": "Yes, you should schedule an appointment with a dermatologist as soon as possible.",
  "history": [
    {
      "role": "user",
      "content": "Should I see a dermatologist immediately?"
    },
    {
      "role": "assistant",
      "content": "Yes, you should schedule an appointment with a dermatologist as soon as possible."
    }
  ]
}
```

---

#### Get User Sessions
```http
GET /auth/sessions/{user_id}
```

**Response (200):**
```json
{
  "user_id": 1,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "disease": "Melanoma",
      "confidence": 0.92,
      "created_at": "2024-04-10T10:30:00",
      "messages": [...]
    }
  ]
}
```

---

#### Get Specific Session
```http
GET /auth/session/{session_id}
```

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "disease": "Melanoma",
  "confidence": 0.92,
  "system_context": "...",
  "messages": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ]
}
```

---

### Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "healthy",
  "message": "API is up and running!"
}
```

---

## 📁 Project Structure

```
Skin Disease Recommendation Project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/
│   │   │   ├── routes.py        # Analysis endpoints
│   │   │   └── auth_routes.py   # Authentication endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Configuration settings
│   │   │   ├── database.py      # Database connection
│   │   │   └── models.py        # SQLAlchemy models
│   │   ├── prompts/
│   │   │   ├── analysis_prompt.py
│   │   │   └── chat_prompt.py
│   │   ├── schemas/
│   │   │   ├── auth.py          # Auth request/response models
│   │   │   └── responses.py     # API response models
│   │   ├── services/
│   │   │   ├── llm_service.py   # Gemini API integration
│   │   │   ├── database_service.py
│   │   │   └── prediction_service.py
│   │   └── utils/
│   ├── model/
│   │   ├── model_v1.h5         # EfficientNet models
│   │   ├── model_v2.h5
│   │   └── model_v3.h5
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app.py                  # Streamlit application
│   └── requirements.txt
├── training/
│   ├── training_v1.ipynb       # Model training notebooks
│   └── training_v2.ipynb
└── README.md
```

---

## 🔧 Configuration

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./test.db
LLM_MODEL=gemini-pro-vision
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | Streamlit |
| **CV Model** | EfficientNet (TensorFlow) |
| **LLM** | Google Gemini API |
| **Database** | SQLite (easily swappable) |
| **Deployment** | Docker |

---

## 🔐 Security Notes

- Never commit `.env` file to version control
- Use environment variables for sensitive data
- API key is passed at runtime, not baked into Docker image
- Implement HTTPS in production
- Use secure session management

---

## 📝 Usage Example

### Via Web Interface
1. Go to `http://localhost:8501`
2. Register or login
3. Upload a skin image
4. Wait for analysis results
5. Ask follow-up questions in the chat

### Via API
```bash
# Analyze an image
curl -X POST "http://localhost:8000/analyze_skin?user_id=1" \
  -F "file=@skin_image.jpg"

# Send a chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "disease": "Melanoma",
    "confidence": 0.92,
    "message": "What should I do?"
  }'
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer

**This application is for educational and informational purposes only.**
- Not a substitute for professional medical advice
- Always consult a qualified dermatologist for diagnosis
- Results should never be used for self-treatment

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ using AI and Computer Vision**
