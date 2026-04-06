import { useState, useCallback } from 'react';
import { analyzeIssue } from '../api';

export function useAnalysis() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (title, body) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await analyzeIssue(title, body);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { isLoading, result, error, analyze, reset, setResult };
}
