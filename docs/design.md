# AI-Powered Excel Mock Interviewer - Design Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Interview State Machine](#interview-state-machine)
4. [Grading System](#grading-system)
5. [LLM Provider Strategy](#llm-provider-strategy)
6. [Data Models](#data-models)
7. [User Interface Design](#user-interface-design)
8. [Performance & Scalability](#performance--scalability)
9. [Security Considerations](#security-considerations)
10. [Future Enhancements](#future-enhancements)

## Executive Summary

The AI-Powered Excel Mock Interviewer is a comprehensive system designed to conduct structured, automated Excel skill assessments. The system combines rule-based validation with LLM-powered evaluation to provide accurate, constructive feedback across different skill levels.

### Key Features
- **Adaptive Interview Flow**: State machine-driven interviews that adjust difficulty based on candidate performance
- **Hybrid Grading**: Combines deterministic formula validation with AI-powered contextual evaluation  
- **Cost-Optimized LLM Strategy**: Intelligent provider switching (Gemini → Groq → Claude) based on complexity and budget
- **Comprehensive Assessment**: Covers foundations, functions, data operations, analysis, and visualization
- **Real-time Interaction**: WebSocket-based streaming for immediate feedback and engaging experience

### Business Value
- **Scalable Screening**: Automate initial Excel skill assessment for technical roles
- **Consistent Evaluation**: Standardized rubrics ensure fair, objective candidate comparison
- **Cost Efficiency**: Smart LLM usage minimizes API costs while maintaining quality
- **Time Savings**: Reduces manual interview time for preliminary skill assessment

## System Architecture

### High-Level Overview
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   LLM Providers │
│   (React)       │     │   (FastAPI)     │     │   (Multi-Model) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────▶│   Database      │◀─────────────┘
                        │   (SQLite)      │
                        └─────────────────┘
```

### Component Architecture

#### Backend Services
- **FastAPI Web Server**: RESTful API with WebSocket streaming
- **Interview Agent**: State machine managing conversation flow
- **Grading Engine**: Hybrid evaluation system
- **Report Generator**: Constructive feedback synthesis
- **Data Layer**: SQLite with SQLAlchemy ORM

#### Frontend Application
- **React SPA**: Modern, responsive user interface
- **Real-time Communication**: WebSocket integration
- **State Management**: React hooks and context
- **Component Library**: Reusable UI components

#### External Integrations
- **Google Gemini**: Primary LLM (cost-effective)
- **Groq**: High-throughput processing
- **Anthropic Claude**: Premium quality for complex cases

### Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | React + Vite | Fast development, modern tooling |
| Backend | FastAPI | High performance, automatic docs |
| Database | SQLite | Simple deployment, adequate for PoC |
| ORM | SQLAlchemy | Mature, flexible data modeling |
| LLM APIs | Multi-provider | Cost optimization, reliability |
| Deployment | Docker + Render | Container portability, easy hosting |

## Interview State Machine

### State Transitions
```
    START
      │
      ▼
  ┌─────────┐
  │ INTRO   │──────┐
  └─────────┘      │
      │            │
      ▼            │
  ┌─────────┐      │
  │CALIBRATE│      │
  └─────────┘      │
      │            │
      ▼            │
  ┌─────────┐      │
  │ CORE_Q  │◀─────┤
  └─────────┘      │
      │            │
      ▼            │
  ┌─────────┐      │
  │DEEP_DIVE│      │
  └─────────┘      │
      │            │
      ▼            │
  ┌─────────┐      │
  │  CASE   │      │
  └─────────┘      │
      │            │
      ▼            │
  ┌─────────┐      │
  │ REVIEW  │      │
  └─────────┘      │
      │            │
      ▼            │
  ┌─────────┐      │
  │ SUMMARY │      │
  └─────────┘      │
      │            │
      ▼            │
     END      ─────┘
```

### State Descriptions

#### 1. INTRO (Introduction)
- **Purpose**: Welcome candidate, explain format, set expectations
- **Duration**: 2-3 turns
- **Actions**: Collect basic info, explain assessment structure
- **Transition**: Automatic to CALIBRATE

#### 2. CALIBRATE (Skill Calibration)
- **Purpose**: Assess baseline skill level
- **Duration**: 3-4 questions
- **Questions**: Foundation skills (references, basic formulas, ranges)
- **Logic**: Determines difficulty trajectory for remaining interview
- **Transition**: To CORE_Q with difficulty level set

#### 3. CORE_Q (Core Questions)
- **Purpose**: Evaluate essential Excel competencies
- **Duration**: 8-12 questions
- **Coverage**: Functions (IF, VLOOKUP, SUMIF, COUNTIF), data operations
- **Adaptive**: Question difficulty adjusts based on performance
- **Transition**: To DEEP_DIVE after comprehensive coverage

#### 4. DEEP_DIVE (Deep Dive)
- **Purpose**: Explore advanced skills and edge cases
- **Duration**: 4-6 questions  
- **Focus**: INDEX/MATCH, advanced IF logic, error handling
- **Condition**: Only for candidates showing proficiency
- **Transition**: To CASE for business application

#### 5. CASE (Case Study)
- **Purpose**: Test applied skills in realistic scenarios
- **Duration**: 2-3 complex problems
- **Format**: Multi-step business problems requiring Excel solutions
- **Assessment**: Problem decomposition, tool selection, efficiency
- **Transition**: To REVIEW for feedback collection

#### 6. REVIEW (Performance Review)  
- **Purpose**: Gather candidate self-assessment
- **Duration**: 2-3 turns
- **Questions**: Confidence levels, challenging areas, preferred functions
- **Value**: Provides insight into self-awareness and metacognition
- **Transition**: To SUMMARY for final evaluation

#### 7. SUMMARY (Summary & Feedback)
- **Purpose**: Deliver comprehensive assessment results
- **Content**: Overall score, skill breakdown, specific feedback
- **Format**: Structured report with actionable recommendations
- **Transition**: END interview session

### Adaptive Logic

#### Difficulty Adjustment
- **Performance Tracking**: Running accuracy score influences next question
- **Threshold-Based**: <60% accuracy → easier questions, >80% → harder questions
- **Skill Coverage**: Ensure all major skill areas assessed regardless of difficulty

#### Question Selection Algorithm
```python
def select_next_question(candidate_state):
    # Get unasked questions in current skill area
    available_questions = get_unasked_questions(
        skill_area=current_skill_area,
        difficulty_range=get_difficulty_range(candidate_state.performance)
    )
    
    # Prioritize based on coverage gaps
    prioritized = prioritize_by_coverage(available_questions, candidate_state.coverage)
    
    # Select highest priority question
    return prioritized[0]
```

## Grading System

### Hybrid Evaluation Architecture

The grading system combines multiple evaluation approaches for comprehensive, accurate assessment:

#### 1. Rule-Based Grader
- **Purpose**: Validate formula syntax and structure
- **Strengths**: Fast, deterministic, handles technical accuracy
- **Coverage**: Function names, parameter counts, syntax correctness
- **Example**: Validates `=VLOOKUP("E123",A2:B101,2,FALSE)` structure

#### 2. LLM-Based Grader  
- **Purpose**: Evaluate conceptual understanding and explanation quality
- **Strengths**: Contextual understanding, flexible evaluation
- **Coverage**: Explanations, reasoning, edge case handling
- **Example**: Assesses explanation of when to use INDEX/MATCH vs VLOOKUP

#### 3. Hybrid Grader (Primary)
- **Purpose**: Combine both approaches for optimal accuracy
- **Logic**: Route questions to appropriate grader based on question type
- **Escalation**: Use premium LLM (Claude) for complex/ambiguous cases
- **Weighting**: 70% technical accuracy, 30% conceptual understanding

### Scoring Rubrics

#### Skill-Based Scoring
Each skill area has specific scoring criteria:

```yaml
references:
  novice: "No understanding of reference types" (0-25%)
  basic: "Knows difference exists but cannot apply" (26-50%) 
  proficient: "Uses both types correctly in simple formulas" (51-85%)
  advanced: "Understands mixed references and complex applications" (86-100%)
```

#### Question Difficulty Weighting
- **Tier 1** (Foundations): 1x multiplier
- **Tier 2** (Functions): 1.5x multiplier  
- **Tier 3** (Advanced/Analysis): 2x multiplier

#### Overall Score Calculation
```
Overall Score = Weighted Average of Skill Scores
Final Grade = (Overall Score) * Interview Completeness Factor
```

### Grading Flow
```
Question Response
      │
      ▼
┌─────────────┐    Yes    ┌─────────────┐
│ Has Formula?│──────────▶│Rule-Based   │
└─────────────┘           │Grader       │
      │ No                └─────────────┘
      ▼                         │
┌─────────────┐                 │
│LLM-Based    │                 │
│Grader       │◀────────────────┘
└─────────────┘    Combine Results
      │                         
      ▼                         
┌─────────────┐                 
│Final Score  │                 
│& Feedback   │                 
└─────────────┘                 
```

## LLM Provider Strategy

### Cost-First Approach

The system implements a cost-optimized LLM strategy with intelligent provider switching:

#### Provider Hierarchy
1. **Google Gemini** (Primary)
   - **Use Case**: Standard questions, general evaluation
   - **Cost**: $0.0015 per 1K tokens (input), $0.002 per 1K tokens (output)
   - **Strengths**: Good balance of cost and quality
   - **Allocation**: 70% of requests

2. **Groq** (Throughput)
   - **Use Case**: High-volume processing, batch operations  
   - **Cost**: $0.10 per 1M tokens (very low cost)
   - **Strengths**: Extremely fast inference, cost-effective
   - **Allocation**: 20% of requests

3. **Anthropic Claude** (Premium)
   - **Use Case**: Complex reasoning, ambiguous cases, final assessments
   - **Cost**: $0.25 per 1K tokens (input), $1.25 per 1K tokens (output) 
   - **Strengths**: Superior reasoning, nuanced evaluation
   - **Allocation**: 10% of requests

### Provider Selection Logic

```python
def select_provider(question_complexity, candidate_level, is_escalation=False):
    if is_escalation or question_complexity == "high":
        return "claude"
    elif candidate_level == "advanced" and question_complexity == "medium":
        return "gemini"
    elif question_complexity == "low":
        return "groq"
    else:
        return "gemini"  # Default
```

### Cost Management

#### Budget Controls
- **Daily Limits**: $50 per day across all providers
- **Provider Limits**: Gemini ($30), Groq ($5), Claude ($15)
- **Request Throttling**: Rate limiting to prevent runaway costs
- **Usage Monitoring**: Track tokens and costs per interview

#### Optimization Strategies
- **Prompt Engineering**: Minimize token usage while maintaining quality
- **Response Caching**: Cache common evaluations to reduce API calls
- **Batch Processing**: Group similar questions for efficient processing
- **Fallback Logic**: Degrade gracefully when providers are unavailable

### Expected Costs Per Interview
- **Average Interview**: 15-20 questions, ~3000 tokens total
- **Cost Breakdown**:
  - Gemini (70%): ~$6.30
  - Groq (20%): ~$0.60  
  - Claude (10%): ~$3.75
- **Total per Interview**: ~$10.65
- **Monthly (100 interviews)**: ~$1,065

## Data Models

### Core Entities

#### Interview
```python
class Interview(Base):
    id: UUID
    candidate_name: str
    start_time: datetime
    end_time: Optional[datetime]
    state: InterviewState
    overall_score: Optional[float]
    skill_scores: JSON  # Dict[str, float]
    metadata: JSON
```

#### Question
```python
class Question(Base):
    id: UUID
    skill: str
    category: str
    difficulty: int  # 1-3
    question_text: str
    expected_answer: str
    validation_rules: List[str]
    metadata: JSON
```

#### Response
```python
class Response(Base):
    id: UUID
    interview_id: UUID
    question_id: UUID
    answer_text: str
    score: float
    feedback: str
    grading_method: str  # "rule_based", "llm_based", "hybrid"
    timestamp: datetime
```

#### Rubric
```python
class Rubric(Base):
    id: UUID
    skill_name: str
    category: str
    difficulty_tier: int
    version: str
    rubric_data: JSON  # Scoring criteria and descriptions
```

### Data Relationships
```
Interview 1 ──── N Response N ──── 1 Question
    │                                   │
    │                                   │
    └── N InterviewSkillScore          └── 1 Rubric
```

### Database Design Principles
- **Denormalization**: Store calculated scores for performance
- **Versioning**: Rubrics and questions support versioning for consistency
- **Audit Trail**: Complete history of responses and scoring decisions
- **Flexibility**: JSON fields allow evolution without schema changes

## User Interface Design

### Design Philosophy
- **Conversational Interface**: Chat-based interaction feels natural and engaging
- **Progressive Disclosure**: Information revealed as interview progresses
- **Real-time Feedback**: Immediate visual cues for progress and performance
- **Accessibility**: WCAG 2.1 AA compliance for inclusive design

### Component Architecture

#### Layout Structure
```
┌─────────────────────────────────────────┐
│              Header Bar                 │
│  [Progress] [Timer] [Score Summary]     │
├─────────────────────────────────────────┤
│                                         │
│              Chat Pane                  │
│          (Main Interaction)             │
│                                         │
├─────────────────────────────────────────┤
│     [Input Field]  [Send Button]       │
└─────────────────────────────────────────┘
```

#### Key Components

##### 1. ChatPane
- **Purpose**: Primary interaction interface
- **Features**: Message bubbles, typing indicators, syntax highlighting
- **Responsive**: Optimized for desktop and mobile
- **Accessibility**: Screen reader support, keyboard navigation

##### 2. ProgressBar  
- **Visualization**: Shows interview completion percentage
- **State Indication**: Current phase highlighted (Calibration, Core Questions, etc.)
- **Adaptive**: Adjusts based on interview path

##### 3. ScorePanel
- **Real-time Updates**: Live score tracking as questions are answered
- **Skill Breakdown**: Visual representation of skill area performance
- **Confidence Indicators**: Shows system confidence in assessments

##### 4. Timer
- **Soft Limits**: Indicates recommended time without hard cutoffs
- **Phase-Aware**: Different time expectations for different interview phases
- **Visual Cues**: Color changes to indicate pacing

### UX Flow

#### Interview Experience
1. **Welcome Screen**: Introduction and expectation setting
2. **Progressive Questions**: Questions appear conversationally 
3. **Immediate Feedback**: Response acknowledgment and light validation
4. **Visual Progress**: Clear indication of interview progression
5. **Final Summary**: Comprehensive results presentation

#### Responsive Design
- **Desktop**: Full layout with all panels visible
- **Tablet**: Collapsible panels, focus on chat
- **Mobile**: Single-column layout, full-screen chat experience

### Accessibility Features
- **Keyboard Navigation**: Full functionality without mouse
- **Screen Reader**: ARIA labels and semantic HTML
- **Color Blind Friendly**: Colors not sole means of conveying information
- **Font Scaling**: Respects user font size preferences

## Performance & Scalability

### Current Performance Characteristics
- **Response Time**: <200ms for rule-based grading, <2s for LLM grading
- **Throughput**: Support for 10 concurrent interviews (PoC limitation)
- **Database**: SQLite adequate for <1000 interviews
- **Memory Usage**: ~100MB per interview session

### Scalability Considerations

#### Immediate Bottlenecks (PoC)
- **SQLite**: Single-threaded database, limited concurrent access
- **In-Memory State**: Interview state not persisted across restarts
- **Single Instance**: No load balancing or horizontal scaling

#### Production Scaling Path
1. **Database Migration**: PostgreSQL for multi-user support
2. **State Management**: Redis for session persistence
3. **Load Balancing**: Multiple FastAPI instances behind nginx
4. **Caching**: Redis cache for questions and rubrics
5. **CDN**: Static asset delivery optimization

#### Performance Optimization
- **Database Indexing**: Query optimization for question selection
- **Connection Pooling**: Efficient database connection management  
- **LLM Response Caching**: Cache common evaluations
- **Background Processing**: Async report generation

### Monitoring & Observability
- **Application Metrics**: Response times, error rates, throughput
- **LLM Usage**: Token consumption, cost tracking, provider performance
- **User Experience**: Interview completion rates, time-to-complete
- **Business Metrics**: Assessment accuracy, candidate satisfaction

## Security Considerations

### Data Protection
- **PII Handling**: Minimal collection, secure storage of candidate information
- **Data Retention**: Configurable retention policies for interview data
- **Encryption**: Data encrypted at rest and in transit
- **Access Control**: Role-based access to interview results

### API Security
- **Authentication**: JWT tokens for API access
- **Rate Limiting**: Prevent abuse of LLM endpoints
- **Input Validation**: Sanitization of all user inputs
- **CORS Policy**: Restricted cross-origin access

### LLM Security
- **API Key Management**: Secure storage and rotation of provider keys
- **Prompt Injection**: Input sanitization to prevent malicious prompts
- **Content Filtering**: Block inappropriate or harmful content
- **Usage Monitoring**: Detect unusual patterns or abuse

### Infrastructure Security
- **Container Security**: Regular image scanning and updates
- **Network Security**: HTTPS only, secure communication
- **Secret Management**: Environment-based configuration
- **Audit Logging**: Complete audit trail of system access

## Future Enhancements

### Short-term Improvements (Next 3 months)
1. **Enhanced Grading**: More sophisticated LLM prompting for nuanced evaluation
2. **Question Pool Expansion**: Additional questions for better coverage
3. **Performance Analytics**: Detailed candidate performance insights  
4. **Mobile Optimization**: Improved mobile interview experience

### Medium-term Features (3-6 months)
1. **Multi-language Support**: Questions and interface in multiple languages
2. **Skill Recommendations**: Personalized learning paths based on gaps
3. **Integration APIs**: Connect with HR systems and candidate management
4. **Advanced Analytics**: Cohort analysis, bias detection, outcome prediction

### Long-term Vision (6-12 months)
1. **Multi-skill Assessment**: Beyond Excel to other technical skills
2. **Video Integration**: Facial recognition and engagement analysis
3. **Collaborative Interviews**: Multi-interviewer support
4. **Advanced AI**: Custom-trained models for domain-specific evaluation

### Technical Debt & Improvements
- **Database Migration**: Move from SQLite to PostgreSQL
- **State Management**: Implement proper session persistence
- **Error Handling**: More robust error recovery and user feedback
- **Testing Coverage**: Comprehensive unit and integration tests
- **Documentation**: API documentation and developer guides

---

## Appendix

### A. API Endpoints
```
POST /interviews/start          # Start new interview
POST /interviews/{id}/turn      # Submit response, get next question  
GET  /interviews/{id}/summary   # Get final assessment
GET  /interviews/{id}/status    # Check interview progress
WebSocket /interviews/{id}/stream # Real-time communication
```

### B. Environment Variables
```
# LLM Provider Configuration
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key  
ANTHROPIC_API_KEY=your_claude_key
PRIMARY_LLM_PROVIDER=gemini

# Application Configuration
DATABASE_URL=sqlite:///./interviews.db
DEBUG=false
CORS_ORIGINS=http://localhost:3000

# Cost Management
DAILY_COST_LIMIT=50.00
PROVIDER_COST_LIMITS='{"gemini": 30.00, "groq": 5.00, "claude": 15.00}'
```

### C. Deployment Configuration
```yaml
# render.yaml
services:
  - type: web
    name: excel-interviewer
    env: docker
    plan: starter
    buildCommand: docker build -t excel-interviewer .
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: GEMINI_API_KEY  
        sync: false
```

### D. Cost Analysis
| Component | Monthly Cost (100 interviews) |
|-----------|-------------------------------|
| LLM APIs | $1,065 |
| Hosting (Render) | $25 |  
| Database | $0 (SQLite) |
| **Total** | **$1,090** |

Cost per interview: ~$10.90
Cost per candidate screened: ~$10.90

This represents significant savings compared to human interviewer time (estimated $200-500 per technical screening interview).

---

*This design document serves as the comprehensive technical specification for the AI-Powered Excel Mock Interviewer system. It should be updated as the system evolves and new requirements emerge.*
