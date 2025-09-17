interface ScorePanelProps {
  scores: Record<string, number>;
}

const ScorePanel = ({ scores }: ScorePanelProps) => {
  const categories = {
    foundations: 'Basic Foundations',
    functions: 'Excel Functions', 
    data_ops: 'Data Operations',
    analysis: 'Data Analysis',
    charts: 'Charts & Visualization'
  };

  return (
    <div className="score-panel">
      <h3>Current Performance</h3>
      
      <div className="score-categories">
        {Object.entries(categories).map(([key, label]) => (
          <div key={key} className="score-item">
            <div className="score-label">{label}</div>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ width: `${scores[key] || 0}%` }}
              />
              <span className="score-value">
                {scores[key] ? `${Math.round(scores[key])}%` : 'Not tested'}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="overall-score">
        <h4>Overall Score</h4>
        <div className="overall-value">
          {Object.keys(scores).length > 0 
            ? `${Math.round(Object.values(scores).reduce((a, b) => a + b, 0) / Object.keys(scores).length)}%`
            : 'In Progress...'}
        </div>
      </div>
    </div>
  );
};

export default ScorePanel;
