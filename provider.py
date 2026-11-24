"""Optional synthetic smoke adapter, never called by CI."""
import json,os,urllib.request
from urllib.error import URLError
def gemini(context):
    if os.getenv('CXBRIDGE_FREE_TIER_CONFIRMED')!='yes': raise ValueError('Free tier not confirmed')
    key=os.environ['GEMINI_API_KEY']
    if context!={'intent':'general'}: raise ValueError('Unsupported context')
    model=os.getenv('GEMINI_MODEL','gemini-2.5-flash-lite')
    if not model.replace('-','').replace('.','').isalnum(): raise ValueError('Invalid model')
    body={'contents':[{'parts':[{'text':'Synthetic support routing: general inquiry. Return JSON {"action":"internal"} only.'}]}],'generationConfig':{'responseMimeType':'application/json','maxOutputTokens':100}}
    req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
    try:
        with urllib.request.urlopen(req,timeout=15) as r: result=json.load(r)
        return json.loads(result['candidates'][0]['content']['parts'][0]['text'])
    except (URLError,KeyError,IndexError,TypeError) as e: raise ValueError('Provider unavailable or invalid response') from e
