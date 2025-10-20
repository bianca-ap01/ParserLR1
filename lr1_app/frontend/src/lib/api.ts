
const API = (path: string) => `http://localhost:8000${path}`

export async function buildLR1(text: string){
  const r = await fetch(API('/lr1/build'),{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})})
  if(!r.ok) throw new Error('LR1 build failed');
  return r.json()
}

export async function regex2nfa(pattern: string){
  const r = await fetch(API('/lex/regex2nfa'),{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pattern})})
  if(!r.ok) throw new Error('regex2nfa failed');
  return r.json()
}

export async function nfa2dfa(nfa:any){
  const r = await fetch(API('/lex/nfa2dfa'),{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(nfa)})
  if(!r.ok) throw new Error('nfa2dfa failed');
  return r.json()
}