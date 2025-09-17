"""
Response timing analytics service for detecting copy-paste and measuring authenticity.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
import json
import statistics

@dataclass
class ResponseTiming:
    """Track detailed timing metrics for a response."""
    question_id: str
    question_text: str
    start_time: datetime
    first_keystroke_time: Optional[datetime] = None
    submission_time: Optional[datetime] = None
    keystrokes: List[Dict[str, Any]] = field(default_factory=list)
    paste_events: List[Dict[str, Any]] = field(default_factory=list)
    focus_events: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def time_to_first_keystroke(self) -> Optional[float]:
        """Time in seconds from question display to first keystroke."""
        if self.first_keystroke_time:
            # Ensure both times are timezone-naive for calculation
            start_time = self.start_time.replace(tzinfo=None) if self.start_time.tzinfo else self.start_time
            first_time = self.first_keystroke_time.replace(tzinfo=None) if self.first_keystroke_time.tzinfo else self.first_keystroke_time
            return (first_time - start_time).total_seconds()
        return None
    
    @property
    def total_response_time(self) -> Optional[float]:
        """Total time to complete response in seconds."""
        if self.submission_time:
            # Ensure both times are timezone-naive for calculation
            start_time = self.start_time.replace(tzinfo=None) if self.start_time.tzinfo else self.start_time
            submission_time = self.submission_time.replace(tzinfo=None) if self.submission_time.tzinfo else self.submission_time
            return (submission_time - start_time).total_seconds()
        return None
    
    @property
    def typing_speed(self) -> Optional[float]:
        """Calculate average typing speed in characters per minute."""
        if not self.keystrokes or not self.submission_time or not self.first_keystroke_time:
            return None
        
        # Ensure both times are timezone-naive for calculation
        submission_time = self.submission_time.replace(tzinfo=None) if self.submission_time.tzinfo else self.submission_time
        first_time = self.first_keystroke_time.replace(tzinfo=None) if self.first_keystroke_time.tzinfo else self.first_keystroke_time
        
        typing_duration = (submission_time - first_time).total_seconds()
        if typing_duration <= 0:
            return None
        
        # Count actual typing keystrokes (exclude backspace, etc.)
        typing_events = [k for k in self.keystrokes if k.get('type') == 'character']
        chars_typed = len(typing_events)
        
        return (chars_typed / typing_duration) * 60  # chars per minute
    
    @property
    def paste_count(self) -> int:
        """Number of paste events detected."""
        return len(self.paste_events)
    
    @property
    def focus_loss_count(self) -> int:
        """Number of times user lost focus (tab switching)."""
        return len([f for f in self.focus_events if f.get('type') == 'blur'])
    
    @property
    def authenticity_score(self) -> float:
        """Calculate authenticity score (0-1, higher = more authentic)."""
        score = 1.0
        
        # Penalty for excessive paste events
        if self.paste_count > 0:
            score -= min(0.5, self.paste_count * 0.2)
        
        # Penalty for focus loss (tab switching)
        if self.focus_loss_count > 0:
            score -= min(0.3, self.focus_loss_count * 0.1)
        
        # Penalty for unrealistic typing speed
        if self.typing_speed and self.typing_speed > 200:  # > 200 CPM is suspicious
            score -= 0.3
        
        # Penalty for too quick response (likely copy-paste)
        if self.time_to_first_keystroke and self.time_to_first_keystroke < 2:
            score -= 0.2
        
        # Penalty for very slow first response (likely searching)
        if self.time_to_first_keystroke and self.time_to_first_keystroke > 60:
            score -= 0.2
        
        return max(0.0, score)

class ResponseTimingService:
    """Service for tracking and analyzing response timing patterns."""
    
    def __init__(self):
        self.active_timings: Dict[str, ResponseTiming] = {}
    
    def start_question_timing(self, 
                            interview_id: int, 
                            question_id: str, 
                            question_text: str) -> str:
        """Start timing for a new question."""
        timing_key = f"{interview_id}_{question_id}"
        
        self.active_timings[timing_key] = ResponseTiming(
            question_id=question_id,
            question_text=question_text,
            start_time=datetime.now()
        )
        
        return timing_key
    
    def record_first_keystroke(self, timing_key: str, timestamp: datetime = None):
        """Record the first keystroke time."""
        if timing_key in self.active_timings:
            timing = self.active_timings[timing_key]
            if not timing.first_keystroke_time:
                timing.first_keystroke_time = timestamp or datetime.now()
    
    def record_keystroke(self,
                        timing_key: str, 
                        keystroke_type: str,
                        char: str = None,
                        timestamp: datetime = None):
        """Record individual keystroke events."""
        if timing_key in self.active_timings:
            timing = self.active_timings[timing_key]
            
            # Ensure consistent timezone handling
            if timestamp and timestamp.tzinfo is not None:
                timestamp = timestamp.replace(tzinfo=None)
            
            actual_timestamp = timestamp or datetime.now()
            
            timing.keystrokes.append({
                'type': keystroke_type,  # 'character', 'backspace', 'delete', etc.
                'char': char,
                'timestamp': actual_timestamp
            })
            
            # Set first keystroke time if this is the first typing event
            if not timing.first_keystroke_time and keystroke_type == 'character':
                timing.first_keystroke_time = actual_timestamp
    
    def record_paste_event(self, 
                          timing_key: str, 
                          content_length: int,
                          timestamp: datetime = None):
        """Record paste events with content analysis."""
        if timing_key in self.active_timings:
            timing = self.active_timings[timing_key]
            
            # Ensure consistent timezone handling
            if timestamp and timestamp.tzinfo is not None:
                timestamp = timestamp.replace(tzinfo=None)
                
            timing.paste_events.append({
                'timestamp': timestamp or datetime.now(),
                'content_length': content_length,
                'suspicious': content_length > 100  # Large pastes are suspicious
            })
    
    def record_focus_event(self, 
                          timing_key: str, 
                          event_type: str,
                          timestamp: datetime = None):
        """Record focus/blur events (tab switching detection)."""
        if timing_key in self.active_timings:
            timing = self.active_timings[timing_key]
            
            # Ensure consistent timezone handling
            if timestamp and timestamp.tzinfo is not None:
                timestamp = timestamp.replace(tzinfo=None)
                
            timing.focus_events.append({
                'type': event_type,  # 'focus' or 'blur'
                'timestamp': timestamp or datetime.now()
            })
    
    def finish_response_timing(self, 
                              timing_key: str, 
                              final_answer: str,
                              timestamp: datetime = None) -> ResponseTiming:
        """Complete timing analysis for a response."""
        if timing_key in self.active_timings:
            timing = self.active_timings[timing_key]
            
            # Ensure consistent timezone handling
            if timestamp:
                # Remove timezone info if present to match start_time
                if timestamp.tzinfo is not None:
                    timestamp = timestamp.replace(tzinfo=None)
            
            timing.submission_time = timestamp or datetime.now()
            
            # Analyze final answer for additional insights
            timing.final_answer_length = len(final_answer)
            timing.final_answer_words = len(final_answer.split())
            
            # Remove from active timings and return completed timing
            return self.active_timings.pop(timing_key)
        
        return None
    
    def analyze_interview_patterns(self, 
                                 timings: List[ResponseTiming]) -> Dict[str, Any]:
        """Analyze overall timing patterns for an interview."""
        if not timings:
            return {'error': 'No timing data available'}
        
        # Calculate aggregate metrics
        response_times = [t.total_response_time for t in timings if t.total_response_time]
        first_keystroke_times = [t.time_to_first_keystroke for t in timings if t.time_to_first_keystroke]
        typing_speeds = [t.typing_speed for t in timings if t.typing_speed]
        authenticity_scores = [t.authenticity_score for t in timings]
        
        total_paste_events = sum(t.paste_count for t in timings)
        total_focus_losses = sum(t.focus_loss_count for t in timings)
        
        analysis = {
            'question_count': len(timings),
            'total_paste_events': total_paste_events,
            'total_focus_losses': total_focus_losses,
            'average_authenticity_score': statistics.mean(authenticity_scores) if authenticity_scores else 0,
            
            'response_time_stats': {
                'mean': statistics.mean(response_times) if response_times else 0,
                'median': statistics.median(response_times) if response_times else 0,
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0
            },
            
            'first_keystroke_stats': {
                'mean': statistics.mean(first_keystroke_times) if first_keystroke_times else 0,
                'median': statistics.median(first_keystroke_times) if first_keystroke_times else 0,
            },
            
            'typing_speed_stats': {
                'mean': statistics.mean(typing_speeds) if typing_speeds else 0,
                'median': statistics.median(typing_speeds) if typing_speeds else 0,
            },
            
            'red_flags': []
        }
        
        # Identify red flags
        if total_paste_events > 0:
            analysis['red_flags'].append(f"Paste events detected: {total_paste_events}")
        
        if total_focus_losses > 2:
            analysis['red_flags'].append(f"Frequent tab switching: {total_focus_losses} times")
        
        if analysis['average_authenticity_score'] < 0.7:
            analysis['red_flags'].append(f"Low authenticity score: {analysis['average_authenticity_score']:.2f}")
        
        # Check for unusual patterns
        if typing_speeds:
            max_typing_speed = max(typing_speeds)
            if max_typing_speed > 150:
                analysis['red_flags'].append(f"Unusually fast typing: {max_typing_speed:.0f} CPM")
        
        if first_keystroke_times:
            very_quick_responses = [t for t in first_keystroke_times if t < 1]
            if len(very_quick_responses) > 1:
                analysis['red_flags'].append(f"Multiple instant responses: {len(very_quick_responses)}")
        
        return analysis

# Global service instance
timing_service = ResponseTimingService()
