"""Offline agent-style tool router. Never auto-messages clients or changes payroll records.
Claude integration is separate and requires credentials; no live calls here.
"""
from dataclasses import dataclass
from typing import Callable
from support_agent import answer, sensitive

ALLOWED_TOOLS={'knowledge_lookup','ticket_handoff','human_approval'}
@dataclass(frozen=True)
class ToolRequest:
    tool:str
    question:str
    ticket_id:str='DEMO-001'

class SafeAgent:
    def __init__(self):self.audit=[]
    def run(self,request:ToolRequest):
        if request.tool not in ALLOWED_TOOLS:raise PermissionError('tool is not allowlisted')
        if sensitive(request.question):
            self.audit.append({'tool':request.tool,'result':'sensitive_block'})
            return {'status':'blocked','requires_human':True,'citations':[]}
        if request.tool=='knowledge_lookup':
            result=answer(request.question)
            self.audit.append({'tool':request.tool,'result':result['status']})
            return result
        if request.tool=='ticket_handoff':
            if not request.ticket_id.startswith('DEMO-'):raise ValueError('Only fictional demo tickets permitted')
            self.audit.append({'tool':request.tool,'result':'draft_ticket'})
            return {'status':'ticket_draft','ticket_id':request.ticket_id,'requires_human':True}
        self.audit.append({'tool':request.tool,'result':'approval_pending'})
        return {'status':'approval_pending','requires_human':True}

def evaluate_agent(queries:list[tuple[str,str]])->dict:
    """Offline deterministic smoke evaluation for content routing, not LLM accuracy."""
    outcomes=[]
    for q,expected_status in queries:
        observed=SafeAgent().run(ToolRequest('knowledge_lookup',q))['status']
        outcomes.append(observed==expected_status)
    return {'evaluated':len(outcomes),'matched':sum(outcomes),'match_rate':round(sum(outcomes)/len(outcomes),3) if outcomes else None,'evaluation_type':'deterministic_fixture'}
