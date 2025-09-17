import React, { useState, useEffect } from 'react';
import ChatPane from './components/ChatPane';
import ScorePanel from './components/ScorePanel';
import ProgressBar from './components/ProgressBar';
import Timer from './components/Timer';
import { TimingIndicator, SuspiciousActivityAlert } from './components/TimingIndicator';
import ResumeUpload from './components/ResumeUpload';
import useResponseTiming from './hooks/useResponseTiming';
import { InterviewService } from './services/api';
import './App.css';

interface InterviewState {
  id: number | null;
  state: string;
  currentQuestion: string;
  targetSkill: string;
  difficulty: number;
  turnNumber: number;
  coverageVector: Record<string, number>;
  timeRemaining: number;
  isActive: boolean;
  isComplete: boolean;
}

function App() {
  const [interview, setInterview] = useState<InterviewState>({
    id: null,
    state: 'NOT_STARTED',
    currentQuestion: '',
    targetSkill: '',
    difficulty: 1,
    turnNumber: 0,
    coverageVector: {},
    timeRemaining: 45 * 60, // 45 minutes
    isActive: false,
    isComplete: false
  });

  const [messages, setMessages] = useState<Array<{
    id: number;
    type: 'question' | 'answer';
    content: string;
    timestamp: Date;
  }>>([]);

  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [candidateName, setCandidateName] = useState('');
  const [scores, setScores] = useState<Record<string, number>>({});
  const [suspiciousActivity, setSuspiciousActivity] = useState<string | null>(null);

  const interviewService = new InterviewService();

  // Initialize timing analytics
  const { timingData, startTiming, finishTiming } = useResponseTiming({
    onSuspiciousActivity: (activity) => {
      setSuspiciousActivity(activity);
    },
    onTimingComplete: (data) => {
      console.log('Timing analysis complete:', data);
    }
  });

  const startInterview = async () => {
    setIsLoading(true);
    try {
      const response = await interviewService.startInterview(candidateName);
      
      setInterview({
        id: response.id,
        state: response.state,
        currentQuestion: response.question || '',
        targetSkill: response.target_skill || '',
        difficulty: response.difficulty || 1,
        turnNumber: response.turn_number,
        coverageVector: response.coverage_vector,
        timeRemaining: response.time_remaining || 45 * 60,
        isActive: true,
        isComplete: false
      });

      // Add initial question to messages
      if (response.question) {
        const initialMessage = {
          id: 1,
          type: 'question' as const,
          content: response.question,
          timestamp: new Date()
        };
        setMessages([initialMessage]);

        // Start timing for the first question
        await startTiming(response.id, `q_${response.turn_number}`, response.question);
      }
    } catch (error) {
      console.error('Failed to start interview:', error);
    }
    setIsLoading(false);
  };

  const submitAnswer = async () => {
    if (!interview.id || !currentAnswer.trim()) return;

    setIsLoading(true);
    try {
      // Finish timing analysis for current response
      await finishTiming(currentAnswer);

      // Add answer to messages
      const newAnswer = {
        id: messages.length + 1,
        type: 'answer' as const,
        content: currentAnswer,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, newAnswer]);

      const response = await interviewService.processAnswer(interview.id, currentAnswer);
      
      // Update interview state
      setInterview(prev => ({
        ...prev,
        state: response.state,
        currentQuestion: response.question || '',
        targetSkill: response.target_skill || '',
        difficulty: response.difficulty || 1,
        turnNumber: response.turn_number,
        coverageVector: response.coverage_vector,
        timeRemaining: response.time_remaining || prev.timeRemaining,
        isComplete: response.next_action === 'END_INTERVIEW'
      }));

      // Add new question if not complete
      if (response.question && response.next_action !== 'END_INTERVIEW') {
        const newQuestion = {
          id: messages.length + 2,
          type: 'question' as const,
          content: response.question,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, newQuestion]);

        // Start timing for the new question
        await startTiming(interview.id!, `q_${response.turn_number}`, response.question);
      }

      setCurrentAnswer('');
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
    setIsLoading(false);
  };

  const getSummary = async () => {
    if (!interview.id) return;

    try {
      const summary = await interviewService.getSummary(interview.id);
      // Handle summary display - could show in modal or new page
      console.log('Interview Summary:', summary);
    } catch (error) {
      console.error('Failed to get summary:', error);
    }
  };

  // Timer countdown effect
  useEffect(() => {
    if (interview.isActive && !interview.isComplete && interview.timeRemaining > 0) {
      const timer = setInterval(() => {
        setInterview(prev => ({
          ...prev,
          timeRemaining: Math.max(0, prev.timeRemaining - 1)
        }));
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [interview.isActive, interview.isComplete, interview.timeRemaining]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Excel Interview System</h1>
        {interview.isActive && (
          <div className="interview-info">
            <span>Turn {interview.turnNumber} | {interview.targetSkill.replace('_', ' ')}</span>
            <Timer timeRemaining={interview.timeRemaining} />
          </div>
        )}
      </header>

      <main className="app-main">
        {!interview.isActive ? (
          <div className="start-screen">
            <h2>Welcome to the Excel Interview</h2>
            <p>
              This interview will assess your Excel knowledge across various areas including 
              formulas, data analysis, and chart creation. The session will take approximately 
              30-45 minutes.
            </p>

            <div className="start-layout">
              <div className="start-form">
                <input
                  type="text"
                  placeholder="Enter your name (optional)"
                  value={candidateName}
                  onChange={(e) => setCandidateName(e.target.value)}
                  className="name-input"
                />
                <button 
                  onClick={startInterview}
                  disabled={isLoading}
                  className="start-button"
                >
                  {isLoading ? 'Starting...' : 'Start Interview'}
                </button>
              </div>

              <ResumeUpload 
                onResumeAnalyzed={(analysis) => {
                  console.log('Resume analysis:', analysis);
                  // You can store the analysis and use it to customize the interview
                }}
                className="resume-upload-section"
              />
            </div>
          </div>
        ) : (
          <div className="interview-layout">
            <div className="main-content">
              <ProgressBar 
                coverageVector={interview.coverageVector}
                currentTurn={interview.turnNumber}
                maxTurns={25}
              />
              
              <ChatPane
                messages={messages}
                currentAnswer={currentAnswer}
                onAnswerChange={setCurrentAnswer}
                onSubmit={submitAnswer}
                isLoading={isLoading}
                isComplete={interview.isComplete}
              />
              
              {interview.isComplete && (
                <div className="completion-actions">
                  <button onClick={getSummary} className="summary-button">
                    View Summary Report
                  </button>
                </div>
              )}
            </div>
            
            <div className="sidebar">
              <ScorePanel scores={scores} />
              <TimingIndicator 
                timingData={timingData}
                isVisible={interview.isActive && !interview.isComplete}
                className="mt-4"
              />
            </div>
          </div>
        )}

        {/* Suspicious Activity Alert */}
        {suspiciousActivity && (
          <SuspiciousActivityAlert
            activity={suspiciousActivity}
            onDismiss={() => setSuspiciousActivity(null)}
          />
        )}
      </main>
    </div>
  );
}

export default App;
