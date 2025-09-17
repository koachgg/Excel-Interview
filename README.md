---
title: Excel Interview AI
emoji: 📊
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.36.1
app_file: app.py
pinned: false
license: mit
python_version: 3.11
---

# 🎯 Excel Interview AI System

## ⚡ Quick Start

🚀 **System Ready!** Both backend and frontend are running:
- **Backend**: `http://127.0.0.1:8000` (API + Docs at `/docs`)
- **Frontend**: `http://localhost:5174/` (React Interview Interface)

### 🖥️ What You Built

An **AI-Powered Excel Interview Chatbot** that conducts structured technical interviews with:
- ⏱️ **Timed Interview Sessions** with real-time countdown
- 🤖 **AI Interviewer Agent** asking adaptive Excel questions  
- 🎯 **Hybrid Grading** (technical accuracy + communication skills)
- 📊 **Comprehensive Reports** with detailed performance analysis
- 🔒 **Anti-Cheating Measures** with timing analytics and behavior monitoring

---

## 🚀 Quick Wins Implemented

### 1. 📄 Resume-Based Personalization
- **Upload PDF/DOCX resumes** for skill extraction
- **Personalized question generation** based on claimed experience
- **Domain-specific questions** (Finance, Analytics, Operations, etc.)
- **Skill verification** questions that cross-reference resume claims

**API Endpoints:**
```bash
POST /api/upload-resume     # Upload and analyze resume
GET  /api/resume-parsing-status  # Check parsing availability
```

### 2. ⏱️ Response Timing Analytics
- **Time-to-first-keystroke** measurement  
- **Typing speed analysis** (chars per minute)
- **Response authenticity scoring** (0-1 scale)
- **Behavioral pattern detection** 

**Metrics Tracked:**
- Time from question display to first keystroke
- Overall response time per question
- Typing rhythm and speed patterns
- Pause analysis for authenticity

### 3. 🚨 Paste Detection & Anti-Cheating
- **Real-time paste event monitoring**
- **Tab switching detection** (focus/blur events)
- **Content length analysis** for suspicious pastes
- **Authenticity score calculation** with red flag system

**Security Features:**
- Clipboard content monitoring
- Window focus tracking
- Suspicious activity alerts
- Behavioral authenticity scoring

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend│    │   SQLite DB     │
│                 │◄───┤                  │◄───┤                 │
│ • Chat Interface│    │ • Interview Agent│    │ • Sessions      │
│ • Timer         │    │ • LLM Integration│    │ • Transcripts   │
│ • Anti-cheat    │    │ • Timing Service │    │ • Scoring       │
│ • Resume Upload │    │ • Report Gen     │    │ • Analytics     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

#### 🤖 Interview Agent (`agents/interviewer.py`)
- State machine for interview flow
- Skill coverage tracking
- Adaptive difficulty adjustment
- Question generation and follow-ups

#### 📊 Hybrid Grading System (`agents/grader.py`)
- Technical accuracy assessment
- Communication skills evaluation
- Real-time feedback generation
- Comprehensive scoring matrix

#### ⏱️ Timing Service (`services/timing_service.py`)
- Response time tracking
- Authenticity scoring
- Behavioral analysis
- Anti-cheating detection

#### 📄 Resume Parser (`services/resume_parser.py`)
- PDF/DOCX text extraction
- Excel skill identification
- Experience level classification
- Personalized question generation

---

## 📋 Interview Flow

1. **📤 Resume Upload** (Optional)
   - Extract skills and experience
   - Generate personalized questions
   - Set appropriate difficulty level

2. **🎬 Interview Start**
   - Create session in database
   - Initialize timing analytics
   - Start countdown timer

3. **💬 Conversational Q&A**
   - AI asks adaptive Excel questions
   - Real-time answer evaluation
   - Follow-up questions based on performance
   - Timing and behavior monitoring

4. **📈 Live Feedback**
   - Immediate response grading
   - Authenticity scoring
   - Red flag detection
   - Progress indicators

5. **📋 Final Report**
   - Comprehensive skill assessment
   - Timing analytics summary
   - Behavioral authenticity report
   - Recommendations and feedback

---

## 🔧 Technical Features

### Backend (`server/`)
- **FastAPI** with automatic API documentation
- **SQLAlchemy** with SQLite for data persistence
- **LLM Provider Abstraction** (OpenAI/Anthropic/Mock)
- **RESTful API** + **WebSocket** support
- **Comprehensive logging** and error handling

### Frontend (`frontend/`)
- **React + TypeScript** with modern hooks
- **Real-time chat interface** with WebSocket
- **Responsive design** with Tailwind CSS
- **Anti-cheating monitoring** with event tracking
- **File upload** for resume processing

### Security & Monitoring
- **Paste event detection**
- **Tab switching monitoring**
- **Typing pattern analysis**
- **Response time analytics**
- **Authenticity scoring algorithm**

---

## 🔮 Advanced Features Roadmap

### 🎥 **Multi-Modal Assessment** (2-3 hours)
```typescript
// Voice Recognition
- Speech-to-text for verbal responses
- Voice pattern analysis for confidence
- Accent and pronunciation assessment
- Real-time transcription

// Video Monitoring  
- Webcam integration for proctoring
- Eye tracking for focus detection
- Facial expression analysis
- Head movement monitoring

// Live Excel Integration
- Screen sharing for practical demos
- Real-time Excel file collaboration
- Formula building exercises
- Live data analysis challenges
```

### 🔒 **Enterprise Proctoring** (Full day)
```python
# AI-Powered Cheat Detection
- Computer vision for behavior analysis
- Multiple monitor detection
- Mobile device usage identification
- Unauthorized software detection

# Advanced Security
- Biometric authentication
- Session recording and replay
- Suspicious activity ML models
- Integration with proctoring services (ProctorU, etc.)

# Behavioral Analytics
- Micro-expression analysis
- Stress level detection
- Confidence scoring
- Attention span measurement
```

### 📊 **Advanced Analytics** (3-4 hours)
```python
# Performance Intelligence
- Skill progression tracking over time
- Comparative analysis with peer groups
- Industry benchmarking
- Predictive performance modeling

# Interview Intelligence
- Question difficulty optimization
- Success rate analytics per question type
- Time allocation optimization
- Personalization effectiveness metrics

# Reporting Dashboard
- Interactive performance visualizations
- Drill-down analytics by skill category
- Export to PDF/Excel
- Integration with HR systems
```

### 🌐 **Production Deployment** (2-3 hours)
```yaml
# Containerization
- Docker Compose for multi-service orchestration
- Environment-specific configurations
- Auto-scaling based on load
- Health check and monitoring

# Cloud Infrastructure
- AWS/Azure deployment scripts
- Load balancing and CDN
- Database clustering and backup
- SSL/TLS certificate management

# CI/CD Pipeline
- Automated testing and deployment
- Environment promotion workflows
- Database migration management
- Performance monitoring
```

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation
```bash
# Clone repository
git clone <repository-url>
cd excel-interviewer

# Backend setup
cd server
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Environment setup
cp .env.example .env
# Configure LLM provider or use MOCK for development
```

### Running the System
```bash
# Terminal 1: Backend
cd server
venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm run dev
```

---

## 🎯 Usage Examples

### Starting an Interview
```javascript
// Basic interview start
POST /interviews
{
  "candidate_name": "John Doe"
}

// With resume personalization
POST /api/upload-resume
// Upload PDF/DOCX file
// Get personalized questions and suggested difficulty
```

### Monitoring Response Authenticity
```javascript
// The system automatically tracks:
- Time to first keystroke: 2.3 seconds
- Typing speed: 45 CPM (normal range)
- Paste events: 0 (authentic)
- Tab switches: 1 (moderate risk)
- Authenticity score: 0.85 (high confidence)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** for the excellent async web framework
- **React** for the powerful frontend capabilities  
- **SQLAlchemy** for robust database ORM
- **OpenAI/Anthropic** for LLM integration
- **Tailwind CSS** for beautiful, responsive design

---

**Built with ❤️ for technical interview excellence**
