interface InterviewResponse {
  id: number;
  state: string;
  question?: string;
  target_skill?: string;
  difficulty?: number;
  turn_number: number;
  coverage_vector: Record<string, number>;
  time_remaining?: number;
  next_action: string;
}

interface SummaryResponse {
  interview_id: number;
  candidate_name?: string;
  total_score: number;
  performance_level: {
    level: string;
    description: string;
  };
  scores_by_skill: Record<string, number>;
  scores_by_category: Record<string, number>;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  transcript_excerpts: Array<{
    question: string;
    answer: string;
    skill: string;
    score: string;
    reason: string;
  }>;
  interview_metadata: {
    duration_minutes: number;
    total_turns: number;
    coverage_completeness: number;
    grading_confidence: number;
  };
}

export class InterviewService {
  private baseURL = 'http://127.0.0.1:8000';

  async startInterview(candidateName?: string): Promise<InterviewResponse> {
    const response = await fetch(`${this.baseURL}/interviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        candidate_name: candidateName
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to start interview: ${response.statusText}`);
    }

    return response.json();
  }

  async processAnswer(interviewId: number, answer: string): Promise<InterviewResponse> {
    const response = await fetch(`${this.baseURL}/turn`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        interview_id: interviewId,
        answer: answer
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to process answer: ${response.statusText}`);
    }

    return response.json();
  }

  async getSummary(interviewId: number): Promise<SummaryResponse> {
    const response = await fetch(`${this.baseURL}/summary/${interviewId}`);

    if (!response.ok) {
      throw new Error(`Failed to get summary: ${response.statusText}`);
    }

    return response.json();
  }

  // WebSocket connection for real-time streaming (optional)
  connectWebSocket(interviewId: number): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsURL = `${protocol}//${window.location.host}/stream/${interviewId}`;
    
    return new WebSocket(wsURL);
  }
}
