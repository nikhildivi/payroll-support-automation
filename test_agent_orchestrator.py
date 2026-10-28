import pytest
from agent_orchestrator import SafeAgent,ToolRequest,evaluate_agent

def test_lookup():assert SafeAgent().run(ToolRequest('knowledge_lookup','onboarding help'))['requires_human']
def test_ticket():assert SafeAgent().run(ToolRequest('ticket_handoff','help'))['status']=='ticket_draft'
def test_approval():assert SafeAgent().run(ToolRequest('human_approval','payroll'))['status']=='approval_pending'
def test_disallowed():
 with pytest.raises(PermissionError):SafeAgent().run(ToolRequest('send_email','send payroll records'))
def test_sensitive():assert SafeAgent().run(ToolRequest('knowledge_lookup','ssn 123-45-6789'))['status']=='blocked'
def test_fake_ticket():
 with pytest.raises(ValueError):SafeAgent().run(ToolRequest('ticket_handoff','hello','REAL-123'))
def test_audit():
 a=SafeAgent();a.run(ToolRequest('knowledge_lookup','onboarding'));assert len(a.audit)==1

def test_eval():assert evaluate_agent([('onboarding help','draft_for_review'),('quantum rockets','no_evidence')])['matched']==2
