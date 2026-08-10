
  import { useState } from "react";
  import { Link, useNavigate } from "react-router-dom";
  import { useAuth } from "../context/AuthContext";

  export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
      e.preventDefault();
      setError("");
      setLoading(true);
      try {
        await login(email, password);
        navigate("/dashboard");
      } catch (err) {
        setError(err.response?.data?.detail || "Login failed");
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-2">Welcome back</h1>
          <p className="text-center text-gray-500 mb-8">Sign in to Interview Mirror</p>
          {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}
          <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>
          <p className="text-center mt-4 text-sm text-gray-500">
            No account? <Link to="/register" className="text-primary-600 hover:underline">Register</Link>
          </p>
        </div>
      </div>
    );
  }
