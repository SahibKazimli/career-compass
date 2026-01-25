import { useState, useEffect } from "react";
import { Briefcase, TrendingUp, BookOpen } from "lucide-react";
import { getRecommendations } from "../services/api";
import type { Recommendation } from "../types";

const difficultyColors = {
  Easy: "bg-emerald-100 text-emerald-700",
  Medium: "bg-amber-100 text-amber-700",
  Hard: "bg-red-100 text-red-700",
};

export function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchRecs() {
      try {
        // Using user_id 1 for demo
        const data = await getRecommendations(1);
        setRecommendations(data.recommendations || []);
      } catch (err) {
        setError("Could not load recommendations. Upload a resume first.");
      } finally {
        setLoading(false);
      }
    }
    fetchRecs();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <p className="text-muted-foreground">Loading recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Career Recommendations</h1>
        <p className="text-muted-foreground">Personalized career paths based on your resume.</p>
      </div>

      {recommendations.length === 0 ? (
        <div className="bg-white p-8 rounded-xl border border-border text-center">
          <p className="text-muted-foreground">No recommendations yet. Upload your resume first!</p>
        </div>
      ) : (
        <div className="space-y-6">
          {recommendations.map((rec, index) => (
            <div key={index} className="bg-white p-6 rounded-xl border border-border shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Briefcase className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">{rec.title}</h3>
                    <p className="text-sm text-muted-foreground">{rec.estimated_salary_range}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${difficultyColors[rec.transition_difficulty]}`}>
                  {rec.transition_difficulty}
                </span>
              </div>

              <p className="text-sm text-foreground mb-4">{rec.match_reason}</p>

              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm font-medium text-foreground">Your Relevant Skills</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {rec.relevant_existing_skills.map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-emerald-50 text-emerald-700 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <BookOpen className="w-4 h-4 text-amber-600" />
                    <span className="text-sm font-medium text-foreground">Skills to Develop</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {rec.skills_to_develop.map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-amber-50 text-amber-700 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-foreground mb-2">First Steps:</p>
                <ol className="list-decimal list-inside space-y-1">
                  {rec.first_steps.map((step, i) => (
                    <li key={i} className="text-sm text-muted-foreground">{step}</li>
                  ))}
                </ol>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}