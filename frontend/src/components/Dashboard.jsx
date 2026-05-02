import { useEffect, useMemo, useState } from "react";
import { io } from "socket.io-client";
import { Activity, CheckCircle2, Radio, Search, Send, ShieldAlert, ThumbsDown, ThumbsUp, TriangleAlert } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api, SOCKET_URL } from "../services/api.js";
import { HighlightedText } from "./HighlightedText.jsx";

const categories = ["general", "bank", "job", "otp", "crypto", "delivery", "tax", "health"];

export function Dashboard() {
  const [content, setContent] = useState("");
  const [source, setSource] = useState("sms");
  const [category, setCategory] = useState("general");
  const [latest, setLatest] = useState(null);
  const [feed, setFeed] = useState([]);
  const [trending, setTrending] = useState([]);
  const [trends, setTrends] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    refreshDashboard().catch((err) => setError(err.message));
  }, [category]);

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket", "polling"] });
    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("submission:new", (submission) => {
      setFeed((items) => [submission, ...items].slice(0, 8));
      setTrending((items) => mergeById(submission, items).slice(0, 12));
    });
    socket.on("vote:new", ({ submission }) => {
      setTrending((items) => mergeById(submission, items));
      setFeed((items) => mergeById(submission, items));
    });
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    const handle = setTimeout(async () => {
      if (query.trim().length < 2) {
        setResults([]);
        return;
      }
      const data = await api(`/submissions/search?q=${encodeURIComponent(query)}&per_page=6`);
      setResults(data.items);
    }, 300);
    return () => clearTimeout(handle);
  }, [query]);

  async function refreshDashboard() {
    const [trendingData, trendData] = await Promise.all([
      api(`/dashboard/trending?category=${category}`),
      api("/dashboard/risk-trends"),
    ]);
    setTrending(trendingData.items);
    setTrends(trendData.items);
  }

  async function submitContent(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api("/submissions", {
        method: "POST",
        body: { content, source, category },
      });
      setLatest(data.submission);
      setContent("");
      await refreshDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function vote(submission, voteType) {
    const data = await api(`/submissions/${submission.id}/votes`, {
      method: "POST",
      body: { vote_type: voteType },
    });
    setLatest((item) => (item?.id === submission.id ? data.submission : item));
    setTrending((items) => mergeById(data.submission, items));
    setFeed((items) => mergeById(data.submission, items));
  }

  const riskSummary = useMemo(() => {
    const high = trending.filter((item) => item.risk_score >= 70).length;
    const average = trending.length
      ? Math.round(trending.reduce((sum, item) => sum + item.risk_score, 0) / trending.length)
      : 0;
    const reports = trending.reduce((sum, item) => sum + item.scam_votes + item.safe_votes + item.upvotes + item.downvotes, 0);
    return { high, average, reports };
  }, [trending]);

  return (
    <section className="dashboard-grid">
      <form className="panel analyzer" onSubmit={submitContent}>
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Analyze</span>
            <h2>Message inspection</h2>
          </div>
          <button className="primary-button" disabled={loading || !content.trim()}>
            <Send size={16} /> {loading ? "Scanning..." : "Scan"}
          </button>
        </div>
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Paste an email, SMS, WhatsApp text, or social message..."
        />
        <div className="controls-row">
          <label>Source<select value={source} onChange={(event) => setSource(event.target.value)}>
            <option>sms</option><option>email</option><option>whatsapp</option><option>social</option><option>message</option>
          </select></label>
          <label>Category<select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((item) => <option key={item}>{item}</option>)}
          </select></label>
        </div>
        {error ? <p className="error-text">{error}</p> : null}
        {latest ? <SubmissionCard submission={latest} onVote={vote} featured /> : <EmptyState text="Scan a suspicious message to see evidence, risk scoring, and community voting." />}
      </form>

      <aside className="stats-stack">
        <Metric icon={<TriangleAlert size={18} />} label="High risk reports" value={riskSummary.high} />
        <Metric icon={<Activity size={18} />} label="Avg trend risk" value={riskSummary.average} />
        <Metric icon={<ShieldAlert size={18} />} label="Community signals" value={riskSummary.reports} />
        <div className="panel metric realtime"><Radio size={18} /><div><strong>{connected ? "Live" : "Offline"}</strong><span>Socket stream</span></div></div>
        <div className="panel search-panel">
          <div className="search-box"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search reported messages" /></div>
          <div className="mini-list">{results.length ? results.map((item) => <MiniItem key={item.id} item={item} />) : <EmptyState text="Search by phrase, category, or threat pattern." compact />}</div>
        </div>
      </aside>

      <section className="panel chart-panel">
        <div className="panel-heading"><div><span className="eyebrow">Risk trends</span><h2>Average daily risk</h2></div></div>
        {trends.length ? (
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={trends}>
              <defs><linearGradient id="risk" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#e85d4f" stopOpacity={0.55}/><stop offset="95%" stopColor="#e85d4f" stopOpacity={0}/></linearGradient></defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e2d8" />
              <XAxis dataKey="day" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Area type="monotone" dataKey="average_risk" stroke="#e85d4f" fill="url(#risk)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        ) : <EmptyState text="Trend data appears after reports are submitted." />}
      </section>

      <section className="panel list-panel">
        <div className="panel-heading"><div><span className="eyebrow">Trending</span><h2>Most reported scams</h2></div></div>
        <div className="submission-list">
          {trending.length ? trending.map((item) => <SubmissionCard key={item.id} submission={item} onVote={vote} />) : <EmptyState text="No reports yet. Submit a sample to populate the threat feed." />}
        </div>
      </section>

      <section className="panel feed-panel">
        <div className="panel-heading"><div><span className="eyebrow">Live</span><h2>New reports</h2></div></div>
        <div className="mini-list">
          {feed.length ? feed.map((item) => <MiniItem key={item.id} item={item} />) : <EmptyState text="Live events will appear here as users submit and vote." compact />}
        </div>
      </section>
    </section>
  );
}

function SubmissionCard({ submission, onVote, featured = false }) {
  const topReasons = (submission.detector_reasons || []).slice(0, 3);
  return (
    <article className={`submission-card ${featured ? "featured" : ""}`}>
      <div className="card-topline">
        <span className={`risk-badge ${submission.risk_level}`}>{submission.risk_score}</span>
        <span>{submission.risk_level} risk</span>
        <span>{submission.category}</span>
        <span>{submission.source}</span>
      </div>
      <HighlightedText text={submission.content} phrases={submission.suspicious_phrases} />
      <div className="reason-row">
        {submission.suspicious_phrases.slice(0, 5).map((phrase) => <span key={phrase}>{phrase}</span>)}
      </div>
      {topReasons.length ? (
        <div className="evidence-list">
          {topReasons.map((reason) => (
            <div key={`${reason.label}-${reason.weight}`}>
              <strong>+{reason.weight}</strong>
              <span>{reason.explanation || reason.label}</span>
            </div>
          ))}
        </div>
      ) : null}
      <div className="vote-row">
        <button type="button" onClick={() => onVote(submission, "scam")}><TriangleAlert size={15} /> Scam {submission.scam_votes}</button>
        <button type="button" onClick={() => onVote(submission, "safe")}><CheckCircle2 size={15} /> Safe {submission.safe_votes}</button>
        <button type="button" onClick={() => onVote(submission, "upvote")}><ThumbsUp size={15} /> {submission.upvotes}</button>
        <button type="button" onClick={() => onVote(submission, "downvote")}><ThumbsDown size={15} /> {submission.downvotes}</button>
      </div>
    </article>
  );
}

function Metric({ icon, label, value }) {
  return <div className="panel metric">{icon}<div><strong>{value}</strong><span>{label}</span></div></div>;
}

function MiniItem({ item }) {
  return (
    <article className="mini-item">
      <span className={`risk-dot ${item.risk_level}`} />
      <div><strong>{item.risk_score} risk</strong><p>{item.content}</p></div>
    </article>
  );
}

function EmptyState({ text, compact = false }) {
  return <div className={`empty-state ${compact ? "compact" : ""}`}>{text}</div>;
}

function mergeById(nextItem, items) {
  const rest = items.filter((item) => item.id !== nextItem.id);
  return [nextItem, ...rest];
}
