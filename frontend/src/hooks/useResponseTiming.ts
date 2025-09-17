/**
 * React hook for tracking response timing and anti-cheating measures
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface TimingData {
  timingKey: string | null;
  timeToFirstKeystroke: number | null;
  pasteCount: number;
  focusLossCount: number;
  isTyping: boolean;
  authenticityScore: number | null;
  redFlags: string[];
}

interface UseResponseTimingOptions {
  onSuspiciousActivity?: (activity: string) => void;
  onTimingComplete?: (data: TimingData) => void;
}

export const useResponseTiming = (options: UseResponseTimingOptions = {}) => {
  const [timingData, setTimingData] = useState<TimingData>({
    timingKey: null,
    timeToFirstKeystroke: null,
    pasteCount: 0,
    focusLossCount: 0,
    isTyping: false,
    authenticityScore: null,
    redFlags: []
  });

  const startTimeRef = useRef<Date | null>(null);
  const firstKeystrokeRef = useRef<Date | null>(null);
  const isRecordingRef = useRef(false);

  // API calls to backend timing service
  const recordKeystroke = useCallback(async (keystrokeType: string, char?: string) => {
    if (!timingData.timingKey) return;

    try {
      await fetch('/api/timing/record-keystroke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timing_key: timingData.timingKey,
          keystroke_type: keystrokeType,
          char: char,
          timestamp: new Date().toISOString()
        })
      });
    } catch (error) {
      console.error('Error recording keystroke:', error);
    }
  }, [timingData.timingKey]);

  const recordPasteEvent = useCallback(async (contentLength: number) => {
    if (!timingData.timingKey) return;

    try {
      const response = await fetch('/api/timing/record-paste', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timing_key: timingData.timingKey,
          content_length: contentLength,
          timestamp: new Date().toISOString()
        })
      });

      const result = await response.json();
      
      setTimingData(prev => ({
        ...prev,
        pasteCount: prev.pasteCount + 1,
        redFlags: result.warning 
          ? [...prev.redFlags, `Large paste detected (${contentLength} chars)`]
          : prev.redFlags
      }));

      if (result.warning) {
        options.onSuspiciousActivity?.(`Paste detected: ${contentLength} characters`);
      }
    } catch (error) {
      console.error('Error recording paste:', error);
    }
  }, [timingData.timingKey, options]);

  const recordFocusEvent = useCallback(async (eventType: 'focus' | 'blur') => {
    if (!timingData.timingKey) return;

    try {
      await fetch('/api/timing/record-focus', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timing_key: timingData.timingKey,
          event_type: eventType,
          timestamp: new Date().toISOString()
        })
      });

      if (eventType === 'blur') {
        setTimingData(prev => ({
          ...prev,
          focusLossCount: prev.focusLossCount + 1,
          redFlags: [...prev.redFlags, 'Tab switching detected']
        }));
        options.onSuspiciousActivity?.('Tab switching detected');
      }
    } catch (error) {
      console.error('Error recording focus event:', error);
    }
  }, [timingData.timingKey, options]);

  // Start timing for a new question
  const startTiming = useCallback(async (interviewId: number, questionId: string, questionText: string) => {
    try {
      const response = await fetch('/api/timing/start-timing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interview_id: interviewId,
          question_id: questionId,
          question_text: questionText
        })
      });

      const result = await response.json();
      
      setTimingData({
        timingKey: result.timing_key,
        timeToFirstKeystroke: null,
        pasteCount: 0,
        focusLossCount: 0,
        isTyping: false,
        authenticityScore: null,
        redFlags: []
      });

      startTimeRef.current = new Date();
      firstKeystrokeRef.current = null;
      isRecordingRef.current = true;

    } catch (error) {
      console.error('Error starting timing:', error);
    }
  }, []);

  // Finish timing and get analysis
  const finishTiming = useCallback(async (finalAnswer: string) => {
    if (!timingData.timingKey) return null;

    try {
      const response = await fetch('/api/timing/finish-timing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timing_key: timingData.timingKey,
          final_answer: finalAnswer,
          timestamp: new Date().toISOString()
        })
      });

      const result = await response.json();
      
      const finalTimingData = {
        ...timingData,
        authenticityScore: result.analysis.authenticity_score,
        timeToFirstKeystroke: result.analysis.time_to_first_keystroke
      };

      setTimingData(finalTimingData);
      options.onTimingComplete?.(finalTimingData);
      
      isRecordingRef.current = false;
      return result.analysis;

    } catch (error) {
      console.error('Error finishing timing:', error);
      return null;
    }
  }, [timingData, options]);

  // Event handlers for input monitoring
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isRecordingRef.current) return;

    // Record first keystroke time
    if (!firstKeystrokeRef.current && event.key.length === 1) {
      firstKeystrokeRef.current = new Date();
      if (startTimeRef.current) {
        const timeToFirst = (firstKeystrokeRef.current.getTime() - startTimeRef.current.getTime()) / 1000;
        setTimingData(prev => ({ ...prev, timeToFirstKeystroke: timeToFirst }));
      }
    }

    // Record keystroke
    const keystrokeType = event.key.length === 1 ? 'character' : 
                         event.key === 'Backspace' ? 'backspace' : 'special';
    
    recordKeystroke(keystrokeType, event.key);
    
    setTimingData(prev => ({ ...prev, isTyping: true }));
    
    // Clear typing indicator after delay
    setTimeout(() => {
      setTimingData(prev => ({ ...prev, isTyping: false }));
    }, 1000);

  }, [recordKeystroke]);

  const handlePaste = useCallback((event: ClipboardEvent) => {
    if (!isRecordingRef.current) return;

    const pastedText = event.clipboardData?.getData('text') || '';
    recordPasteEvent(pastedText.length);
  }, [recordPasteEvent]);

  const handleFocus = useCallback(() => {
    if (isRecordingRef.current) {
      recordFocusEvent('focus');
    }
  }, [recordFocusEvent]);

  const handleBlur = useCallback(() => {
    if (isRecordingRef.current) {
      recordFocusEvent('blur');
    }
  }, [recordFocusEvent]);

  // Set up global event listeners
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('paste', handlePaste);
    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('paste', handlePaste);
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
    };
  }, [handleKeyDown, handlePaste, handleFocus, handleBlur]);

  return {
    timingData,
    startTiming,
    finishTiming,
    isRecording: isRecordingRef.current
  };
};

export default useResponseTiming;
