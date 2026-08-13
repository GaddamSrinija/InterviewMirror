
  import { Link } from "react-router-dom";
  import { useAuth } from "../context/AuthContext";

  export default function Landing() {
    const { user } = useAuth();

    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-primary-950 text-white">
        <nav className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="text-xl font-bold">Interview Mirror</span>
          <div className="flex gap-4">
            {user ? (
              <Link to="/dashboard" className="px-4 py-2 bg-white text-primary-700 rounded-lg text-sm font-medium hover:bg-gray-100">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="px-4 py-2 text-sm hover:text-gray-200">Login</Link>
                <Link to="/register" className="px-4 py-2 bg-white text-primary-700 rounded-lg text-sm font-medium hover:bg-gray-100">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </nav>

        <div className="max-w-4xl mx-auto px-4 pt-24 pb-20 text-center">
          <h1 className="text-5xl font-bold leading-tight mb-6">
            AI that interviews you<br />on your own project
          </h1>
          <p className="text-lg text-primary-200 mb-10 max-w-2xl mx-auto">
            Paste a GitHub repo URL. Our AI analyzes your code, then conducts a personalized
            technical interview based on your actual implementation.
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-3 bg-white text-primary-700 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
          >
            Start Your Interview
          </Link>
        </div>

        <div className="max-w-5xl mx-auto px-4 pb-24">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: "Paste Your Repo", desc: "Link any public GitHub repository. We fetch and analyze every important file." },
              { title: "AI Interviews You", desc: "A Senior Engineer AI asks questions about your architecture, code, and decisions." },
              { title: "Get Your Report", desc: "Receive detailed scores, strengths, weaknesses, and a downloadable PDF report." },
            ].map((item) => (
              <div key={item.title} className="bg-white/10 backdrop-blur rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-primary-200 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }