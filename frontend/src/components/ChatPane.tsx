import React from 'react';

interface Message {
  id: number;
  type: 'question' | 'answer';
  content: string;
  timestamp: Date;
}

interface ChatPaneProps {
  messages: Message[];
  currentAnswer: string;
  onAnswerChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  isComplete: boolean;
}

const ChatPane: React.FC<ChatPaneProps> = ({
  messages,
  currentAnswer,
  onAnswerChange,
  onSubmit,
  isLoading,
  isComplete
}) => {
  return (
    <div className="chat-pane">
      <div className="messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.type === 'question' ? 'question' : 'answer'}`}
          >
            <div className="message-header">
              <span className="message-type">
                {message.type === 'question' ? 'Interviewer' : 'You'}
              </span>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">
              {message.content}
            </div>
          </div>
        ))}
      </div>

      {!isComplete && (
        <div className="answer-input">
          <textarea
            value={currentAnswer}
            onChange={(e) => onAnswerChange(e.target.value)}
            placeholder="Type your answer here..."
            disabled={isLoading}
            rows={4}
          />
          <button
            onClick={onSubmit}
            disabled={isLoading || !currentAnswer.trim()}
            className="submit-button"
          >
            {isLoading ? 'Submitting...' : 'Submit Answer'}
          </button>
        </div>
      )}

      {isComplete && (
        <div className="completion-message">
          <p>Interview completed! Thank you for your responses.</p>
        </div>
      )}
    </div>
  );
};

export default ChatPane;
