export default function LoadingSpinner({ size = 'medium', color = 'blue' }) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  const colorClasses = {
    blue: 'text-blue-600',
    gray: 'text-gray-600',
    white: 'text-white',
    green: 'text-green-600',
    red: 'text-red-600',
  };

  return (
    <div className="flex justify-center items-center">
      <svg
        className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </div>
  );
}

export function FullPageLoader() {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-75 flex justify-center items-center z-50">
      <div className="text-center">
        <LoadingSpinner size="large" color="blue" />
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

export function ComponentLoader({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <LoadingSpinner size="large" color="blue" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
}
