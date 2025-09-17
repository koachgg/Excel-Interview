interface ProgressBarProps {
  coverageVector: Record<string, number>;
  currentTurn: number;
  maxTurns: number;
}

const ProgressBar = ({ coverageVector, currentTurn, maxTurns }: ProgressBarProps) => {
  const skillCategories = [
    { key: 'foundations', skills: ['references', 'ranges', 'formatting'], color: '#3b82f6' },
    { key: 'functions', skills: ['if_functions', 'vlookup', 'index_match', 'countif', 'sumif'], color: '#10b981' },
    { key: 'data_ops', skills: ['sorting', 'filtering', 'pivot_tables'], color: '#f59e0b' },
    { key: 'analysis', skills: ['whatif_analysis', 'goal_seek', 'statistics'], color: '#ef4444' },
    { key: 'charts', skills: ['charts'], color: '#8b5cf6' }
  ];

  const calculateCategoryProgress = (skills: string[]) => {
    const covered = skills.filter(skill => coverageVector[skill] > 0).length;
    return skills.length > 0 ? (covered / skills.length) * 100 : 0;
  };

  const overallProgress = (currentTurn / maxTurns) * 100;

  return (
    <div className="progress-bar">
      <div className="progress-header">
        <h4>Interview Progress</h4>
        <span>{currentTurn}/{maxTurns} questions</span>
      </div>

      <div className="overall-progress">
        <div className="progress-track">
          <div 
            className="progress-fill"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      <div className="skill-categories">
        {skillCategories.map(category => {
          const progress = calculateCategoryProgress(category.skills);
          return (
            <div key={category.key} className="category-progress">
              <div className="category-label">
                {category.key.replace('_', ' ').toUpperCase()}
              </div>
              <div className="category-bar">
                <div 
                  className="category-fill"
                  style={{ 
                    width: `${progress}%`,
                    backgroundColor: category.color 
                  }}
                />
              </div>
              <span className="category-percentage">
                {Math.round(progress)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressBar;
