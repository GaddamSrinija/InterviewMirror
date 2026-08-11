
  import { useState, useEffect, useRef } from "react";
  import { useParams, useNavigate, useLocation } from "react-router-dom";
  import api from "../api/client";
  import ScoreChart from "../components/ScoreChart";

  export default function Interview() {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [session, setSession] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [lastEvaluation, setLastEvaluation] = useState(null);
    const [answer, setAnswer] = useState("");
    const [agentMessages, setAgentMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [ended, setEnded] = useState(false);
    const [summary, setSummary] = useState(null);
    const [overallScore, setOverallScore] = useState(null);
    const messagesEnd = useRef(null);

    useEffect(() => {
      if (location.state?.firstStep) {
        const step = location.state.firstStep;
        if (step.question) setCurrentQuestion(step.question);
        if (step.agent_messages) setAgentMessages(step.agent_messages);
      } else {
        api.get(`/api/interviews/${sessionId}`).then((res) => {
          setSession(res.data);
          if (res.data.status === "completed") {
            setEnded(true);
            setSummary(res.data.summary);
            setOverallScore(res.data.overall_score);
          }
        });
      }
    }, [sessionId]);

    useEffect(() => {
      messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
    }, [agentMessages, currentQuestion]);

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!answer.trim() || loading) return;
      setLoading(true);
      setLastEvaluation(null);
      try {
        const res = await api.post(`/api/interviews/${sessionId}/answer`, { answer_text: answer });
        setAnswer("");
        if (res.data.evaluation) setLastEvaluation(res.data.evaluation);
        if (res.data.agent_messages) setAgentMessages((prev) => [...prev, ...res.data.agent_messages]);
        if (res.data.question) setCurrentQuestion(res.data.question);
        if (res.data.interview_ended) {
          setEnded(true);
          setSummary(res.data.summary);
          setOverallScore(res.data.overall_score);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (ended) {
      return (
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold mb-4">Interview Complete</h1>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            {overallScore && <p className="text-3xl font-bold text-primary-600 mb-2">{overallScore.toFixed(1)}/10</p>}
            {summary && <p className="text-gray-600 mb-6">{summary}</p>}
            {lastEvaluation && <ScoreChart evaluation={lastEvaluation} />}
            <button onClick={() => navigate(`/report/${sessionId}`)}
              className="mt-4 w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">
              View Report
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Technical Interview</h1>

        <div className="space-y-3 mb-6">
          {agentMessages.map((msg, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-gray-400 animate-pulse-slow">
              <span className="w-2 h-2 bg-primary-400 rounded-full" />
              {msg.message}
            </div>
          ))}
        </div>

        {currentQuestion && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded">{currentQuestion.question_type || "question"}</span>
              {currentQuestion.difficulty && <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{currentQuestion.difficulty}</span>}
            </div>
            <p className="text-gray-800 leading-relaxed">{currentQuestion.question_text}</p>
            {currentQuestion.related_file && (
              <p className="mt-2 text-xs text-gray-400">Related: {currentQuestion.related_file}</p>
            )}
          </div>
        )}

        {lastEvaluation && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <p className="text-sm font-medium text-blue-700">Previous answer score: {lastEvaluation.score}/10</p>
            <ScoreChart evaluation={lastEvaluation} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <textarea
            value={answer} onChange={(e) => setAnswer(e.target.value)}
            rows={5} placeholder="Type your answer here..."
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none
  resize-none"
          />
          <button type="submit" disabled={loading || !answer.trim()}
            className="w-full py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
            {loading ? "AI is thinking..." : "Submit Answer"}
          </button>
        </form>
        <div ref={messagesEnd} />
      </div>
    );
  }