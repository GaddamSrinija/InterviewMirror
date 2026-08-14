
  import { useAuth } from "../context/AuthContext";

  export default function Settings() {
    const { user } = useAuth();

    return (
      <div className="max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Settings</h1>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Profile</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-500">Username</label>
              <p className="font-medium">{user?.username}</p>
            </div>
            <div>
              <label className="block text-sm text-gray-500">Email</label>
              <p className="font-medium">{user?.email}</p>
            </div>
            <div>
              <label className="block text-sm text-gray-500">Member since</label>
              <p className="font-medium">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
