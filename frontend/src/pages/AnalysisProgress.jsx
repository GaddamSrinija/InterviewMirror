
  import { useState, useEffect } from "react";
  import { useParams, useNavigate } from "react-router-dom";
  import api from "../api/client";
  import LoadingSpinner from "../components/LoadingSpinner";

  export default function AnalysisProgress() {
    const { repoId } = useParams();
    const navigate = useNavigate();
    const [job, setJob] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
      const poll = setInterval(async () => {
        try {
          const res = await api.get(`/api/repositories/${repoId}/analysis`);
          setJob(res.data);
          if (res.data.status === "completed" || res.data.status === "failed") {
            clearInterval(poll);
          }
        } catch {
          setError("Failed to fetch analysis status");
          clearInterval(poll);
        }
      }, 2000);
      return () => clearInterval(poll);
    }, [repoId]);

    const startInterview = async () => {
      try {
        const res = await api.post("/api/interviews/start", { repository_id: parseInt(repoId) });
        const targetSessionId = res.data.session_id || res.data.question?.session_id || repoId;
        navigate(`/interview/${targetSessionId}`, { state: { firstStep: res.data } });
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to start interview");
      }
    };

    if (error) return <div className="text-red-600 text-center py-20">{error}</div>;
    if (!job) return <LoadingSpinner message="Loading analysis status..." />;

    return (
      <div className="max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Repository Analysis</h1>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <span className={`text-sm font-medium px-2 py-1 rounded ${
              job.status === "completed" ? "bg-green-100 text-green-700" :
              job.status === "failed" ? "bg-red-100 text-red-700" :
              "bg-yellow-100 text-yellow-700"
            }`}>
              {job.status}
            </span>
            <span className="text-sm text-gray-500">{job.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div className="bg-primary-600 h-2 rounded-full transition-all duration-500" style={{ width: `${job.progress}%` }} />
          </div>
          {job.current_step && (
            <p className="text-sm text-gray-500 animate-pulse-slow">{job.current_step}</p>
          )}
          {job.status === "failed" && job.error_message && (
            <p className="text-sm text-red-600 mt-2">{job.error_message}</p>
          )}
          {job.status === "completed" && (
            <button onClick={startInterview} className="mt-6 w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
              Start Interview
            </button>
          )}
        </div>
      </div>
    );
  }
