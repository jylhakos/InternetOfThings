export class DownloadError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public originalError?: any
  ) {
    super(message);
    this.name = 'DownloadError';
  }
}

export const handleDownloadError = (error: any): DownloadError => {
  if (error.response) {
    // Server responded with error status
    const statusCode = error.response.status;
    switch (statusCode) {
      case 403:
        return new DownloadError('Access denied. Please check your permissions.', statusCode, error);
      case 404:
        return new DownloadError('File not found.', statusCode, error);
      case 429:
        return new DownloadError('Too many requests. Please try again later.', statusCode, error);
      default:
        return new DownloadError(`Server error: ${statusCode}`, statusCode, error);
    }
  } else if (error.request) {
    // Network error
    return new DownloadError('Network error. Please check your connection.', undefined, error);
  } else {
    // Other error
    return new DownloadError('An unexpected error occurred.', undefined, error);
  }
};