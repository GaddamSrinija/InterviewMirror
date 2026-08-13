
  import { useState, useEffect } from "react";
  import { Link } from "react-router-dom";
  import api from "../api/client";
  import LoadingSpinner from "../components/LoadingSpinner";

  export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [repos, setRepos] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      Promise.all([
        api.get("/api/dashboard/stats"),
        api.get("/api/repositories/"),
      ]).then(([statsRes, reposRes]) => {
        setStats(statsRes.data);
        setRepos(reposRes.data);
      }).finally(() => setLoading(false));
    }, []);

    if (loading) return <LoadingSpinner />;

    return (
      <div>
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <Link to="/import" className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
            Import Repository
          </Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Repositories", value: stats?.total_repositories || 0 },
            { label: "Interviews", value: stats?.total_interviews || 0 },
            { label: "Completed", value: stats?.completed_interviews || 0 },
            { label: "Avg Score", value: stats?.average_score || "—" },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-sm text-gray-500">{s.label}</p>
              <p className="text-2xl font-bold mt-1">{s.value}</p>
            </div>
          ))}
        </div>

        <h2 className="text-lg font-semibold mb-4">Your Repositories</h2>
        {repos.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
            No repositories imported yet.{" "}
            <Link to="/import" className="text-primary-600 hover:underline">Import one</Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {repos.map((repo) => (
              <div key={repo.id} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{repo.owner}/{repo.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{repo.description || "No description"}</p>
                    {repo.language && <span className="inline-block mt-2 text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded">{repo.language}</span>}
                  </div>
                  <div className="flex gap-2">
                    <Link to={`/analysis/${repo.id}`} className="text-xs px-3 py-1.5 bg-gray-100 rounded-lg hover:bg-gray-200">Status</Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }
