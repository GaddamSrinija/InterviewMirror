
  import { useState } from "react";
  import { useNavigate } from "react-router-dom";
  import api from "../api/client";

  export default function ImportRepo() {
    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
      e.preventDefault();
      setError("");
      setLoading(true);
      try {
        const res = await api.post("/api/repositories/", { github_url: url });
        navigate(`/analysis/${res.data.id}`);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to import repository");
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">Import Repository</h1>
        <p className="text-gray-500 mb-8">Paste a public GitHub repository URL to analyze it.</p>
        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl border border-gray-200 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">GitHub URL</label>
            <input
              type="url" value={url} onChange={(e) => setUrl(e.target.value)} required
              placeholder="https://github.com/owner/repository"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
            {loading ? "Importing..." : "Import & Analyze"}
          </button>
        </form>
      </div>
    );
  }
