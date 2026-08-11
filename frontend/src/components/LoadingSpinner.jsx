
  export default function LoadingSpinner({ message }) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
      
        <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        {message && <p className="mt-4 text-sm text-gray-500">{message}</p>}
      </div>
    );
  }