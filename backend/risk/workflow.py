import asyncio
import os
import re
from time import perf_counter
from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from . import provider, tools
from .config import mode
from .db import now, uid
from .models import Evidence, Finding, Report, ResearchRequest, Trace, Usage

class State(TypedDict,total=False):
    request: ResearchRequest
    sources: list[Evidence]
    selection: provider.Selection
    findings: list[Finding]
    recommendations: list[str]
    steps: list[Trace]
    issues: list[str]
    usage: Usage
    report: Report
    start: float
    agent_mode: str

def elapsed(start: float) -> float:
    return round((perf_counter()-start)*1000,2)

async def read_node(state: State, name: Literal["risk_snapshot","retrieve_evidence"], label: str) -> dict:
    start=perf_counter()
    req=state["request"]
    try:
        found=await asyncio.wait_for(tools.invoke(name,req.company,req.question),5)
        issue=[] if found else [f"No matching evidence from {name}."]
        status: Literal["ok","warning","error"]="warning" if issue else "ok"
        detail=f"{len(found)} source records"
    except Exception:
        found=[]
        status="error"
        detail="Tool unavailable or timed out"
        issue=[f"{name} could not be read."]
    return {"sources":state["sources"]+found,"issues":state["issues"]+issue,"steps":state["steps"]+[Trace(node=label,status=status,detail=detail,ms=elapsed(start),tool=name)]}

async def research(state: State) -> dict:
    return await read_node(state,"risk_snapshot","Research")

async def retrieve(state: State) -> dict:
    return await read_node(state,"retrieve_evidence","Retrieval")

def simulated(question: str,sources: list[Evidence]) -> provider.Selection:
    words=set(re.findall(r"[a-z]{4,}",question.lower()))
    ordered=sorted(sources,key=lambda s:-len(words & set(re.findall(r"[a-z]{4,}",(s.title+" "+s.body).lower()))))
    chosen=ordered[:4]
    combined=" ".join(s.body.lower() for s in chosen)
    action="collections" if "distributor" in combined else "operations" if "carrier" in combined or "inventory" in combined else "reconcile"
    return provider.Selection(citations=[s.id for s in chosen],actions=[action,"documentation"] if chosen else [])

async def analyze(state: State) -> dict:
    start=perf_counter()
    sources=state["sources"]
    issues=state["issues"].copy()
    selection=provider.Selection(citations=[],actions=[])
    usage=Usage()
    status: Literal["ok","warning","error"]="ok"
    detail="Deterministic evidence selection"
    if state["agent_mode"]=="live" and sources:
        detail="Structured model selection"
        try:
            selection,usage=await asyncio.wait_for(provider.live_select(state["request"].question,sources),12)
        except Exception:
            issues.append("Live model unavailable or timed out. Evidence is available for manual review.")
            status="error"
            detail="Provider unavailable"
            usage=Usage(input_tokens=None,cached_tokens=None,output_tokens=None,cost_usd=None)
    else:
        selection=simulated(state["request"].question,sources)
    return {"selection":selection,"usage":usage,"issues":issues,"steps":state["steps"]+[Trace(node="Risk analysis",status=status,detail=detail,ms=elapsed(start))]}

def validate(state: State) -> dict:
    start=perf_counter()
    selection=state["selection"]
    by_id={s.id:s for s in state["sources"]}
    ids=list(dict.fromkeys(selection.citations))
    actions=list(dict.fromkeys(selection.actions))
    issues=state["issues"].copy()
    if any(i not in by_id for i in ids) or any(a not in provider.ACTIONS for a in actions):
        issues.append("Unrecognized model references were removed.")
    findings=[Finding(citation=i,text=by_id[i].body) for i in ids if i in by_id][:4]
    if not findings:
        issues.append("No validated findings. A reviewer should inspect the evidence.")
    recommendations=[provider.ACTIONS[a] for a in actions if a in provider.ACTIONS][:2] if findings else []
    return {"findings":findings,"recommendations":recommendations,"issues":issues,"steps":state["steps"]+[Trace(node="Validation",status="warning" if issues else "ok",detail=f"{len(findings)} source-linked findings",ms=elapsed(start))]}

def publish(state: State) -> dict:
    start=perf_counter()
    req=state["request"]
    issues=state["issues"]
    agent_mode=state["agent_mode"]
    steps=state["steps"]+[Trace(node="Report",status="ok",detail="Assembled evidence and review actions",ms=elapsed(start))]
    report=Report(id=uid("RUN"),at=now(),company=req.company,question=req.question,mode=agent_mode,model=os.getenv("OPENAI_MODEL","gpt-4.1-mini") if agent_mode=="live" else "Deterministic fixture",status="failed" if not state["findings"] else "partial" if issues else "complete",findings=state["findings"],sources=state["sources"],recommendations=state["recommendations"],confidence="Limited evidence" if issues else "Corroborated by ledger and documents",uncertainties=issues+["Evidence is limited to the synthetic reporting period. Future outcomes are unknown."],steps=steps,usage=state["usage"],latency_ms=elapsed(state["start"]))
    return {"report":report}

builder=StateGraph(State)
builder.add_sequence([("research",research),("retrieve",retrieve),("analyze",analyze),("validate",validate),("publish",publish)])
builder.add_edge(START,"research")
builder.add_edge("publish",END)
graph=builder.compile()

async def investigate(request: ResearchRequest, *, simulation: bool=False) -> Report:
    result=await graph.ainvoke({"request":request,"sources":[],"steps":[],"issues":[],"start":perf_counter(),"agent_mode":"demo" if simulation else mode()})
    return result["report"]

