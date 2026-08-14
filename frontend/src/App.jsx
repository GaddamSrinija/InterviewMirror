
  import { Routes, Route } from "react-router-dom";
  import Layout from "./components/Layout";
  import ProtectedRoute from "./components/ProtectedRoute";
  import Landing from "./pages/Landing";
  import Login from "./pages/Login";
  import Register from "./pages/Register";
  import Dashboard from "./pages/Dashboard";
  import ImportRepo from "./pages/ImportRepo";
  import AnalysisProgress from "./pages/AnalysisProgress";
  import Interview from "./pages/Interview";
  import Report from "./pages/Report";
  import History from "./pages/History";
  import Settings from "./pages/Settings";

  export default function App() {
    return (
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/import" element={<ImportRepo />} />
            <Route path="/analysis/:repoId" element={<AnalysisProgress />} />
            <Route path="/interview/:sessionId" element={<Interview />} />
            <Route path="/report/:sessionId" element={<Report />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
      </Routes>
    );
  }