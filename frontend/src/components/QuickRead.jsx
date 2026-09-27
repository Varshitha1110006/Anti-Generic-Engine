import { ArrowUpRight } from "lucide-react";

export function QuickRead({ result, onBuild }) {
  return <div className="report-grid" data-testid="analysis-report">
    <div className="score-card glass"><span className="index">DISTINCTION INDEX</span><div className="score">{result.score}<small>/100</small></div><div className="score-bar"><span style={{ width: `${result.score}%` }} /></div><p>{result.verdict}</p></div>
    <div className="diagnosis-card glass"><span className="index">THE READ</span><p className="diagnosis">{result.diagnosis}</p>
      <div className="signal-list">{result.signals.map((signal) => <div className="signal-row" key={signal.label}><span>{signal.label}</span><div className="mini-bar"><i style={{ width: `${signal.value}%` }} /></div><b>{signal.value}</b></div>)}</div>
    </div>
    <div className="unlock-card"><span className="index">NEXT UNLOCKS</span>{result.unlocks.map((unlock, i) => <div className="unlock" key={unlock}><span>0{i + 1}</span>{unlock}<ArrowUpRight size={15} /></div>)}</div>
    <div className="concept-card"><span className="index">DISTINCTIVE CONCEPT / GENERATED</span><p>{result.distinct_concept}</p><button onClick={onBuild} data-testid="save-concept-button">BUILD THE FULL SYSTEM <ArrowUpRight size={16} /></button></div>
  </div>;
}
