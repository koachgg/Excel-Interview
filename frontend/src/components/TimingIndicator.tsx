/**
 * Component displaying real-time timing analytics and anti-cheating indicators
 */

import React from 'react';
import { AlertTriangle, Clock, Eye, Copy, Zap } from 'lucide-react';

interface TimingData {
  timingKey: string | null;
  timeToFirstKeystroke: number | null;
  pasteCount: number;
  focusLossCount: number;
  isTyping: boolean;
  authenticityScore: number | null;
  redFlags: string[];
}

interface TimingIndicatorProps {
  timingData: TimingData;
  isVisible?: boolean;
  className?: string;
}

export const TimingIndicator: React.FC<TimingIndicatorProps> = ({
  timingData,
  isVisible = true,
  className = ""
}) => {
  if (!isVisible || !timingData.timingKey) return null;

  const getAuthenticityColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAuthenticityLabel = (score: number | null) => {
    if (score === null) return 'Calculating...';
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className={`bg-white border rounded-lg p-4 shadow-sm ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">Response Analytics</h3>
        {timingData.isTyping && (
          <div className="flex items-center text-blue-600 text-xs">
            <Zap className="w-3 h-3 mr-1" />
            Typing...
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-2 gap-3 text-sm">
        {/* Response Time */}
        <div className="flex items-center">
          <Clock className="w-4 h-4 text-gray-400 mr-2" />
          <div>
            <div className="text-xs text-gray-500">First Response</div>
            <div className="font-medium">
              {timingData.timeToFirstKeystroke !== null 
                ? `${timingData.timeToFirstKeystroke.toFixed(1)}s`
                : '—'
              }
            </div>
          </div>
        </div>

        {/* Authenticity Score */}
        <div className="flex items-center">
          <Eye className="w-4 h-4 text-gray-400 mr-2" />
          <div>
            <div className="text-xs text-gray-500">Authenticity</div>
            <div className={`font-medium ${getAuthenticityColor(timingData.authenticityScore)}`}>
              {getAuthenticityLabel(timingData.authenticityScore)}
            </div>
          </div>
        </div>

        {/* Paste Count */}
        <div className="flex items-center">
          <Copy className="w-4 h-4 text-gray-400 mr-2" />
          <div>
            <div className="text-xs text-gray-500">Paste Events</div>
            <div className={`font-medium ${timingData.pasteCount > 0 ? 'text-orange-600' : 'text-gray-700'}`}>
              {timingData.pasteCount}
            </div>
          </div>
        </div>

        {/* Focus Loss */}
        <div className="flex items-center">
          <AlertTriangle className="w-4 h-4 text-gray-400 mr-2" />
          <div>
            <div className="text-xs text-gray-500">Tab Switches</div>
            <div className={`font-medium ${timingData.focusLossCount > 0 ? 'text-red-600' : 'text-gray-700'}`}>
              {timingData.focusLossCount}
            </div>
          </div>
        </div>
      </div>

      {/* Red Flags */}
      {timingData.redFlags.length > 0 && (
        <div className="mt-3 pt-3 border-t">
          <div className="text-xs text-gray-500 mb-1">Alerts</div>
          {timingData.redFlags.map((flag, index) => (
            <div key={index} className="text-xs text-red-600 flex items-center mb-1">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {flag}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

interface SuspiciousActivityAlertProps {
  activity: string;
  onDismiss: () => void;
}

export const SuspiciousActivityAlert: React.FC<SuspiciousActivityAlertProps> = ({
  activity,
  onDismiss
}) => {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss();
    }, 5000); // Auto-dismiss after 5 seconds

    return () => clearTimeout(timer);
  }, [onDismiss]);

  return (
    <div className="fixed top-4 right-4 bg-red-100 border border-red-300 rounded-lg p-3 shadow-lg z-50 max-w-sm">
      <div className="flex items-start">
        <AlertTriangle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <div className="text-sm font-medium text-red-800">Suspicious Activity Detected</div>
          <div className="text-sm text-red-700 mt-1">{activity}</div>
        </div>
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-600 ml-2"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default TimingIndicator;
