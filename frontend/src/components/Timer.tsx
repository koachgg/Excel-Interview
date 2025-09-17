interface TimerProps {
  timeRemaining: number;
}

const Timer = ({ timeRemaining }: TimerProps) => {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerColor = (): string => {
    if (timeRemaining > 900) return '#10b981'; // Green > 15 min
    if (timeRemaining > 300) return '#f59e0b'; // Yellow > 5 min
    return '#ef4444'; // Red <= 5 min
  };

  return (
    <div className="timer" style={{ color: getTimerColor() }}>
      <span className="timer-label">Time:</span>
      <span className="timer-value">{formatTime(timeRemaining)}</span>
    </div>
  );
};

export default Timer;
