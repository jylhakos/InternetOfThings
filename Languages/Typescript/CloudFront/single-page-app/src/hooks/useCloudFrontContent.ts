import { useState, useEffect } from 'react';
import axios from 'axios';

interface UseCloudFrontContentProps {
  url: string;
  autoFetch?: boolean;
}

interface ContentState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useCloudFrontContent = <T = any>({
  url,
  autoFetch = true
}: UseCloudFrontContentProps) => {
  const [state, setState] = useState<ContentState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const fetchContent = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await axios.get<T>(url, {
        headers: {
          'Cache-Control': 'no-cache',
        }
      });
      setState({
        data: response.data,
        loading: false,
        error: null
      });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred'
      });
    }
  };

  useEffect(() => {
    if (autoFetch && url) {
      fetchContent();
    }
  }, [url, autoFetch]);

  return {
    ...state,
    refetch: fetchContent
  };
};