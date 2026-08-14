
  import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from "recharts";

  export default function ScoreChart({ evaluation }) {
    if (!evaluation) return null;
    const data = [
      { subject: "Technical", score: evaluation.technical_correctness || 0 },
      { subject: "Code Understanding", score: evaluation.code_understanding || 0 },
      { subject: "Architecture", score: evaluation.architecture_understanding || 0 },
      { subject: "Communication", score: evaluation.communication || 0 },
      { subject: "Practical", score: evaluation.practical_thinking || 0 },
    ];

    return (
      <div className="w-full h-64">
        <ResponsiveContainer>
          <RadarChart data={data}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <PolarRadiusAxis domain={[0, 10]} tick={{ fontSize: 10 }} />
            <Radar dataKey="score" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.3} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    );
  }