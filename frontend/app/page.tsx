"use client";
import React, { useState } from "react";

const BRAND_COLOR = "#18130f"; // goldish black
const ACCENT_COLOR = "#FFD700"; // gold accent

export default function Home() {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/generate-spec", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea }),
      });
    
      const data = await res.json();
    
      if (!res.ok) {
        throw new Error(data.detail || "Failed to generate spec");
      }
    
      setResult(data);
    } catch (err: any) {
      console.error("Request failed:", err);
      setError(err.message || "Unknown error");
    }
       finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (result) {
      const jsonString = JSON.stringify(result, null, 2);
      const blob = new Blob([jsonString], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "devspec_synth_agent_spec.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <main style={{
      minHeight: "100vh",
      background: `linear-gradient(135deg, ${BRAND_COLOR} 80%, ${ACCENT_COLOR} 100%)`,
      color: ACCENT_COLOR,
      fontFamily: "Inter, sans-serif",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: 24,
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        ::selection { background: ${ACCENT_COLOR}22; }
      `}</style>
      <h1 style={{ fontWeight: 700, fontSize: 40, marginBottom: 8, color: ACCENT_COLOR }}>
        DevSpec Synth Agent
      </h1>
      <p style={{ color: "#fff", opacity: 0.8, marginBottom: 32, fontSize: 18, maxWidth: 500, textAlign: "center" }}>
        Instantly turn your product idea into a full-stack technical spec. Enter your idea below:
      </p>
      <form onSubmit={handleSubmit} style={{ width: "100%", maxWidth: 500, display: "flex", flexDirection: "column", gap: 16 }}>
        <input
          type="text"
          value={idea}
          onChange={e => setIdea(e.target.value)}
          placeholder="e.g. Pricing simulator that shows upgrade risk if a feature is removed."
          style={{
            padding: 16,
            borderRadius: 8,
            border: `1px solid ${ACCENT_COLOR}`,
            fontSize: 18,
            fontFamily: "Inter, sans-serif",
            outline: "none",
            marginBottom: 8,
            background: BRAND_COLOR,
            color: ACCENT_COLOR,
          }}
          required
        />
        <button
          type="submit"
          disabled={loading || !idea.trim()}
          style={{
            background: ACCENT_COLOR,
            color: BRAND_COLOR,
            fontWeight: 600,
            fontSize: 18,
            border: "none",
            borderRadius: 8,
            padding: "14px 0",
            cursor: loading ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
        >
          {loading ? "Generating..." : "Generate Spec"}
        </button>
      </form>
      {error && <div style={{ color: "#ff4d4f", marginTop: 24 }}>{error}</div>}
      {result && (
        <div style={{
          background: "#222",
          color: ACCENT_COLOR,
          borderRadius: 12,
          padding: 24,
          marginTop: 32,
          maxWidth: 700,
          width: "100%",
          boxShadow: "0 4px 32px #0006",
          overflowX: "auto",
        }}>
          <button
            onClick={handleDownload}
            style={{
              background: ACCENT_COLOR,
              color: BRAND_COLOR,
              fontWeight: 600,
              fontSize: 16,
              border: "none",
              borderRadius: 8,
              padding: "10px 15px",
              cursor: "pointer",
              marginTop: 20,
            }}
          >
            Download JSON
          </button>
        </div>
      )}
    </main>
  );
}
