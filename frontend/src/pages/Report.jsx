  import { useState, useEffect } from "react";
  import { useParams } from "react-router-dom";
  import api from "../api/client";
  import LoadingSpinner from "../components/LoadingSpinner";
  import ScoreChart from "../components/ScoreChart";

  export default function Report() {
    const { sessionId } = useParams();
    const [session, setSession] = useState(null);
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
      api.get(`/api/interviews/${sessionId}`).then((res) => {
        setSession(res.data);
        setLoading(false);
      });
    }, [sessionId]);

    const generateReport = async () => {
      setGenerating(true);
      try {
        const res = await api.post(`/api/reports/${sessionId}/generate`);
        setReport(res.data);
      } catch (err) {
        if (err.response?.status === 409) {
          alert("Report already exists");
        }
      } finally {
        setGenerating(false);
      }
    };

    const downloadReport = async () => {
      if (!report) return;
      try {
        const res = await api.get(`/api/reports/${report.id}/download`, {
          responseType: "blob",
        });
        const blob = new Blob([res.data], { type: "application/pdf" });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `interview_report_${sessionId}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        alert("Failed to download report");
      }
    };

    if (loading) return <LoadingSpinner />;
    if (!session) return <div className="text-center py-20 text-gray-400">Session not found</div>;

    const lastEval = session.questions
      ?.filter((q) => q.answer?.evaluation)
      ?.map((q) => q.answer.evaluation)
      ?.pop();

    return (
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Performance Report</h1>

        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-3xl font-bold text-primary-600">{session.overall_score?.toFixed(1) || "—"}/10</p>
              <p className="text-sm text-gray-500 mt-1">Overall Score</p>
            </div>
            <span className={`text-sm font-medium px-3 py-1 rounded-full ${
              session.status === "completed" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
            }`}>
              {session.status}
            </span>
          </div>
          {session.summary && <p className="text-gray-600 text-sm">{session.summary}</p>}
        </div>

        {lastEval && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Score Breakdown</h2>
            <ScoreChart evaluation={lastEval} />
          </div>
        )}

        <div className="space-y-4 mb-6">
          <h2 className="text-lg font-semibold">Questions & Answers</h2>
          {session.questions?.map((q, i) => (
            <div key={q.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-medium text-gray-400">Q{i + 1}</span>
                {q.difficulty && <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">{q.difficulty}</span>}
              </div>
              <p className="font-medium text-gray-800 mb-2">{q.question_text}</p>
              {q.answer && (
                <>
                  <p className="text-sm text-gray-600 border-l-2 border-primary-200 pl-3 mb-2">{q.answer.answer_text}</p>
                  {q.answer.evaluation && (
                    <div className="mt-2 text-sm">
                      <span className="font-medium text-primary-600">{q.answer.evaluation.score}/10</span>
                      {q.answer.evaluation.strengths?.length > 0 && (
                        <p className="text-green-600 mt-1">Strengths: {q.answer.evaluation.strengths.join(", ")}</p>
                      )}
                      {q.answer.evaluation.weaknesses?.length > 0 && (
                        <p className="text-red-500 mt-1">Improve: {q.answer.evaluation.weaknesses.join(", ")}</p>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">PDF Report</h2>
          {!report ? (
            <button onClick={generateReport} disabled={generating}
              className="w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
              {generating ? "Generating PDF..." : "Generate PDF Report"}
            </button>
          ) : (
            <button onClick={downloadReport}
              className="w-full py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700">
              Download PDF Report
            </button>
          )}
        </div>
      </div>
    );
  }