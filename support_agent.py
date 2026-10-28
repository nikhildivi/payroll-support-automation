"""Safe read-only HR/payroll support answer drafting, offline by default.
Optional Claude Messages API integration requires deliberate opt-in and a user API key.
Do not send real payroll or HR client data to this demo.
"""
from __future__ import annotations
import json,os,re,urllib.request
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DOCS={
 'DOC-01':('onboarding','New client onboarding requires an approved intake checklist, document review and a human specialist before payroll activation.'),
 'DOC-02':('payroll','Payroll change requests must go to an authorized payroll specialist and should never be executed by this assistant.'),
 'DOC-03':('sales','Sales discovery starts with workforce size, supported states, existing software and timeline. Do not promise pricing or product coverage.'),
 'DOC-04':('security','Do not submit Social Security numbers, bank account details, pay rates or employee records into demo AI prompts.'),
 'DOC-05':('support','For unresolved urgent payroll questions, escalate to the authorized support team with a ticket reference.'),
}
STOP={'and','the','for','with','your','a','an','to','is','i','how','can','do','we','what','are','on'}
def tokens(s):return set(x for x in re.findall('[a-z]+',s.lower()) if len(x)>2 and x not in STOP)
def retrieve(question,top_k=2):
 q=tokens(question)
 scores=[]
 for id,(topic,text) in DOCS.items():
  sim=len(q & tokens(topic+' '+text))
  if sim:scores.append((sim,id,text))
 scores.sort(key=lambda x:(-x[0],x[1]));return [{'id':id,'content':content,'score':s} for s,id,content in scores[:top_k]]
def sensitive(text):
 return bool(re.search(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9,16}\b|\b(?:ssn|social security number|bank account|routing number)\s*[:#]?\s*\d+',text,re.I))
def answer(question):
 if not question or len(question)>800:raise ValueError('Question must be between 1 and 800 characters')
 if sensitive(question):return {'status':'blocked_sensitive_data','answer':'Do not enter payroll or personal data into this tool. Contact a specialist.','citations':['DOC-04'],'requires_human':True}
 matches=retrieve(question)
 if not matches:return {'status':'no_evidence','answer':'I do not have a verified source for this question. Escalate to a human specialist.','citations':[],'requires_human':True}
 best=matches[0]
 return {'status':'draft_for_review','answer':best['content'],'citations':[m['id'] for m in matches],'requires_human':True}

def safe_claude_draft(question,api_key,model):
 """Live external API call; NEVER called automatically. Must use synthetic/non-sensitive prompts only."""
 if sensitive(question):raise ValueError('Sensitive data disallowed')
 data=answer(question)
 if data['status']!='draft_for_review':return data
 if not api_key or not model:raise ValueError('API key and model are required')
 sources='\n'.join(f"[{d['id']}] {d['content']}" for d in retrieve(question))
 payload={'model':model,'max_tokens':350,'system':'Draft a brief answer ONLY from the provided fictional reference passages. Cite passage IDs. If unsupported, say unknown. No account changes or private data. All output is a draft for a human to review.',
 'messages':[{'role':'user','content':f'Question: {question}\nReference passages:\n{sources}'}]}
 req=urllib.request.Request('https://api.anthropic.com/v1/messages',data=json.dumps(payload).encode(),
 headers={'x-api-key':api_key,'anthropic-version':'2023-06-01','content-type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=15) as resp:body=json.load(resp)
 blocks=[item.get('text','') for item in body.get('content',[]) if item.get('type')=='text']
 return {'status':'claude_draft_for_review','answer':'\n'.join(blocks),'citations':[d['id'] for d in retrieve(question)],'requires_human':True}

app=FastAPI(title='Support Drafting / Claude-ready Sandbox')
class Query(BaseModel):question:str=Field(min_length=1,max_length=800)
@app.post('/support/draft')
def draft(query:Query):
 try:return answer(query.question)
 except ValueError as e:raise HTTPException(422,str(e))
if __name__=='__main__':print(json.dumps(answer('How should a new customer be onboarded?'),indent=2))
