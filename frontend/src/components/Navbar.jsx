
  import { Link, useNavigate } from "react-router-dom";
  import { useAuth } from "../context/AuthContext";

  export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
      logout();
      navigate("/");
    };

    return (
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/dashboard" className="text-xl font-bold text-primary-700">
            Interview Mirror
          </Link>
          <div className="flex items-center gap-6">
            <Link to="/dashboard" className="text-sm text-gray-600 hover:text-primary-600">
              Dashboard
            </Link>
            <Link to="/import" className="text-sm text-gray-600 hover:text-primary-600">
              Import
            </Link>
            <Link to="/history" className="text-sm text-gray-600 hover:text-primary-600">
              History
            </Link>
            <Link to="/settings" className="text-sm text-gray-600 hover:text-primary-600">
              Settings
            </Link>
            <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
              <span className="text-sm text-gray-500">{user?.username}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
    );
  }
