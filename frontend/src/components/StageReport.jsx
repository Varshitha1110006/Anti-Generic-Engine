import { useEffect, useState } from "react";
import { Check } from "lucide-react";

export const STAGE_NAMES = ["UNDERSTAND", "PERSONALITY", "CHALLENGE GENERIC", "VISUALIZE", "TEST CONSISTENCY", "LAUNCH"];

export function BuildProgress() {
  const [step, setStep] = useState(0);
  useEffect(() => { const t = setInterval(() => setStep((s) => Math.min(s + 1, 5)), 11000); return () => clearInterval(t); }, []);
  return <div className="build-progress" data-testid="build-progress">
    <div className="stage-rail">{STAGE_NAMES.map((name, i) => <div key={name} className={i < step ? "stage-tab done" : i === step ? "stage-tab active pulsing" : "stage-tab"}><span>{String(i + 1).padStart(2, "0")}</span>{name}{i < step && <Check size={13} />}</div>)}</div>
    <p className="build-note">The engine is reasoning through stage {String(step + 1).padStart(2, "0")} of 06. Each stage reads the ones before it — this usually takes one to two minutes.</p>
  </div>;
}

export function StageReport({ stages, activeStage, onSelect }) {
  const stage = stages[activeStage];
  return <>
    <div className="stage-rail">{stages.map((s, index) => <button className={activeStage === index ? "stage-tab active" : "stage-tab"} onClick={() => onSelect(index)} key={s.key} data-testid={`stage-tab-${s.key}`}><span>{String(index + 1).padStart(2, "0")}</span>{s.name}{activeStage > index && <Check size={13} />}</button>)}</div>
    <div className="stage-detail glass" data-testid="active-stage-detail">
      <div className="stage-title"><span className="index">STAGE {String(activeStage + 1).padStart(2, "0")} / STRUCTURED OUTPUT</span><h3>{stage.name}</h3><p>{stage.summary}</p></div>
      <div className="decision-grid">{stage.decisions?.map((decision) => <div className="decision" key={decision.label}><span>{decision.label}</span><p>{decision.value}</p></div>)}</div>
      <div className="tension-row">
        <div><span className="index">TENSIONS TO RESOLVE</span>{stage.tensions?.map((tension) => <p key={tension}>↳ {tension}</p>)}</div>
        <div className="next-question"><span className="index">NEXT QUESTION</span><p>{stage.next_question}</p></div>
      </div>
    </div>
  </>;
}
