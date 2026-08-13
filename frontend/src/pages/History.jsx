
  import { useState, useEffect } from "react";
  import { Link } from "react-router-dom";
  import api from "../api/client";
  import LoadingSpinner from "../components/LoadingSpinner";

  export default function History() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      api.get("/api/history/").then((res) => {
        setSessions(res.data);
      }).finally(() => setLoading(false));
    }, []);

    if (loading) return <LoadingSpinner />;

    return (
      <div>
        <h1 className="text-2xl font-bold mb-6">Interview History</h1>
        {sessions.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
            No interviews yet. <Link to="/import" className="text-primary-600 hover:underline">Import a repo</Link> to start.
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.map((s) => (
              <Link key={s.id} to={s.status === "completed" ? `/report/${s.id}` : `/interview/${s.id}`}
                className="block bg-white rounded-xl border border-gray-200 p-5 hover:border-primary-300 transition">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Interview #{s.id}</p>
                    <p className="text-sm text-gray-500 mt-1">{new Date(s.started_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {s.overall_score && <span className="text-lg font-bold text-primary-600">{s.overall_score.toFixed(1)}</span>}
                    <span className={`text-xs font-medium px-2 py-1 rounded ${
                      s.status === "completed" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                    }`}>
                      {s.status}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    );
  }
