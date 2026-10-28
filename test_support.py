import pytest
from fastapi.testclient import TestClient
from support_agent import answer,retrieve,tokens,sensitive,safe_claude_draft,app

def test_lookup():assert any(d['id']=='DOC-01' for d in retrieve('new client onboarding'))
def test_payroll():assert 'DOC-02' in answer('payroll change request')['citations']
def test_no_evidence():assert answer('quantum rockets') ['status']=='no_evidence'
def test_sensitive_ssn():assert sensitive('my SSN is 123-45-6789')
def test_sensitive_bank():assert sensitive('bank account 123456789')
def test_doesnt_flag_normal():assert not sensitive('what is onboarding timeline')
def test_block_sensitive():assert answer('SSN 123-45-6789')['status']=='blocked_sensitive_data'
def test_no_call():assert answer('help with onboarding')['status']=='draft_for_review'
def test_human_gate():assert answer('payroll change')['requires_human']
def test_citations():assert answer('need onboarding help')['citations']
def test_limit_empty():
 with pytest.raises(ValueError):answer('')
def test_limit_long():
 with pytest.raises(ValueError):answer('a'*900)
def test_api():assert TestClient(app).post('/support/draft',json={'question':'how do we handle onboarding?'}).status_code==200
def test_api_bad():assert TestClient(app).post('/support/draft',json={'question':''}).status_code==422
def test_claude_requires_key():
 with pytest.raises(ValueError):safe_claude_draft('onboarding',None,None)
def test_claude_block():
 with pytest.raises(ValueError):safe_claude_draft('ssn 123-45-6789','fake','fake')
def test_max_retrieval():assert len(retrieve('payroll client onboarding sales security',2))<=2
