/**
 * Resume upload component for personalized interviews
 */

import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';

interface ResumeUploadProps {
  onResumeAnalyzed?: (analysis: any) => void;
  className?: string;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({
  onResumeAnalyzed,
  className = ""
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!allowedTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF, DOCX, or TXT file');
        return;
      }

      // Validate file size (5MB max)
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const base64Content = btoa(e.target?.result as string);
          
          const response = await fetch('/api/upload-resume-simple', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              filename: file.name,
              content: base64Content
            }),
          });

          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }

          const result = await response.json();
          setUploadResult(result);
          onResumeAnalyzed?.(result);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Upload failed');
          console.error('Resume upload error:', err);
        } finally {
          setUploading(false);
        }
      };
      
      reader.onerror = () => {
        setError('Failed to read file');
        setUploading(false);
      };
      
      reader.readAsBinaryString(file);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploading(false);
    }
  };

  const clearUpload = () => {
    setFile(null);
    setUploadResult(null);
    setError(null);
  };

  return (
    <div className={`bg-white border rounded-lg p-4 ${className}`}>
      <div className="flex items-center mb-3">
        <FileText className="w-5 h-5 text-blue-600 mr-2" />
        <h3 className="text-sm font-medium text-gray-700">Resume Upload (Optional)</h3>
      </div>

      {!uploadResult ? (
        <div>
          <p className="text-xs text-gray-500 mb-3">
            Upload your resume to get personalized interview questions based on your Excel experience
          </p>

          {!file ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <span className="text-sm text-blue-600 hover:text-blue-800">
                  Choose file or drag & drop
                </span>
              </label>
              <p className="text-xs text-gray-500 mt-1">PDF, DOCX, or TXT (max 5MB)</p>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  <FileText className="w-4 h-4 text-gray-500 mr-2" />
                  <span className="text-sm font-medium">{file.name}</span>
                </div>
                <button
                  onClick={clearUpload}
                  className="text-gray-400 hover:text-gray-600 text-xs"
                >
                  Remove
                </button>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="bg-blue-600 text-white text-xs px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {uploading ? 'Analyzing...' : 'Upload & Analyze'}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center text-red-600 text-xs mt-2">
              <AlertCircle className="w-4 h-4 mr-1" />
              {error}
            </div>
          )}
        </div>
      ) : (
        <div className="bg-green-50 rounded-lg p-3">
          <div className="flex items-center text-green-700 mb-2">
            <CheckCircle className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Resume Analyzed Successfully!</span>
          </div>
          
          <div className="text-xs space-y-1">
            <div>
              <span className="font-medium">Experience Level:</span>{' '}
              <span className="capitalize">{uploadResult.analysis?.experience_level || 'Unknown'}</span>
            </div>
            <div>
              <span className="font-medium">Skills Found:</span>{' '}
              {uploadResult.analysis?.skills_count || 0} Excel-related skills
            </div>
            {uploadResult.analysis?.domains?.length > 0 && (
              <div>
                <span className="font-medium">Domains:</span>{' '}
                {uploadResult.analysis.domains.join(', ')}
              </div>
            )}
            <div>
              <span className="font-medium">Personalized Questions:</span>{' '}
              {uploadResult.analysis?.personalized_questions?.length || 0} generated
            </div>
          </div>

          <button
            onClick={clearUpload}
            className="text-blue-600 text-xs mt-2 hover:text-blue-800"
          >
            Upload Different Resume
          </button>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
