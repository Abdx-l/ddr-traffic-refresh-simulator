"""Cycle-accounted memory scheduling experiment with reproducible traffic."""
from dataclasses import dataclass
from collections import deque
import argparse, csv, json, random, statistics

@dataclass(frozen=True)
class Request:
    id: int
    arrival: int
    bank: int
    row: int
    write: bool

@dataclass
class Timing:
    rcd: int = 3
    rp: int = 3
    ras: int = 7
    cas: int = 3
    burst: int = 2
    rfc: int = 12
    refi: int = 120

def generate(count=1000, seed=42, workload="mixed", banks=4):
    rng=random.Random(seed)
    for i in range(count):
        address=i if workload=="sequential" else rng.randrange(4096)
        if workload=="mixed" and rng.random()<0.6: address=(i//32)*16+i%16
        yield Request(i,i*2,address%banks,(address//banks)//16,rng.random()<0.35)

def simulate(requests, policy="fcfs", timing=None, banks=4):
    if policy not in ("fcfs","frfcfs"): raise ValueError("unknown policy")
    t=timing or Timing()
    if min(t.rcd,t.rp,t.ras,t.cas,t.burst,t.rfc,t.refi)<1: raise ValueError("positive timing required")
    incoming=deque(sorted(requests,key=lambda r:(r.arrival,r.id)))
    pending=[]; rows=[None]*banks; activated=[-10**9]*banks
    now=0; next_refresh=t.refi; refresh_wait=0; records=[]
    while incoming or pending:
        while incoming and incoming[0].arrival<=now: pending.append(incoming.popleft())
        if now>=next_refresh:
            close_wait=max([max(0,t.ras-(now-activated[b])) for b in range(banks) if rows[b] is not None] or [0])
            penalty=close_wait+(t.rp if any(r is not None for r in rows) else 0)+t.rfc
            now+=penalty;refresh_wait+=penalty;rows=[None]*banks
            next_refresh=now+t.refi
            continue
        if not pending:
            now=incoming[0].arrival
            continue
        # FR-FCFS picks the oldest row hit; FCFS strictly follows arrival order.
        index=0
        if policy=="frfcfs":
            index=next((i for i,r in enumerate(pending) if rows[r.bank]==r.row),0)
        r=pending.pop(index)
        if not 0<=r.bank<banks: raise ValueError("bank outside configured range")
        start=now;hit=rows[r.bank]==r.row
        if not hit:
            if rows[r.bank] is not None:
                now+=max(0,t.ras-(now-activated[r.bank]))+t.rp
            activated[r.bank]=now;rows[r.bank]=r.row;now+=t.rcd
        now+=t.cas+t.burst
        records.append(dict(id=r.id,arrival=r.arrival,start=start,finish=now,bank=r.bank,row=r.row,write=r.write,row_hit=hit,latency=now-r.arrival))
    latency=[r["latency"] for r in records]
    return records,dict(policy=policy,requests=len(records),cycles=now,throughput=len(records)/max(1,now),row_hit_rate=sum(r["row_hit"] for r in records)/max(1,len(records)),mean_latency=statistics.mean(latency) if latency else 0,p95_latency=sorted(latency)[min(len(latency)-1,int(len(latency)*.95))] if latency else 0,refresh_wait=refresh_wait)

def main():
    p=argparse.ArgumentParser();p.add_argument("--count",type=int,default=1000);p.add_argument("--seed",type=int,default=42);p.add_argument("--workload",choices=["sequential","random","mixed"],default="mixed");p.add_argument("--output",default="trace.csv")
    a=p.parse_args();requests=list(generate(a.count,a.seed,a.workload))
    summaries=[]
    for policy in ("fcfs","frfcfs"):
        rows,summary=simulate(requests,policy);summaries.append(summary)
        with open(policy+"-"+a.output,"w",newline="") as f:
            if rows: w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    print(json.dumps(summaries,indent=2))
if __name__=="__main__":main()
