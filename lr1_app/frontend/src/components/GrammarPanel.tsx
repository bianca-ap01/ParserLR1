import React, { useState } from 'react'
import { buildLR1, traceParse } from '../lib/api'
import DataTable from './DataTable'

const EXPR = `E -> E + T | T
T -> T * F | F
F -> ( E ) | id`;

export default function GrammarPanel(){
  const [text, setText] = useState(EXPR)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any|null>(null)
  const [tab, setTab] = useState<'closure'|'action'>('closure')
  const [traceTokens, setTraceTokens] = useState('')
  const [trace, setTrace] = useState<any[]|null>(null)
  const [traceErr, setTraceErr] = useState<string|undefined>()

  async function onBuild(){
    setLoading(true)
    try{
      const res = await buildLR1(text)
      setData(res)
    }finally{ setLoading(false) }
  }

  async function onTrace(){
    setTraceErr(undefined)
    setTrace(null)
    try{
      const tokens = traceTokens.trim()? traceTokens.trim().split(/\s+/): []
      const res = await traceParse(text, tokens.length? tokens: undefined, undefined)
      setTrace(res.steps||[])
    }catch(e:any){ setTraceErr(String(e)) }
  }

  const closureCols = ['state','items']
  const isEps = (t: string) => t === 'ε' || t === 'eps' || (typeof t === 'string' && t.indexOf('�') >= 0)
  const closureRows = (data?.states||[]).map((s:any)=>({
    state: s.state,
    items: s.items.map((it:any)=>{
      const rhs = (it.rhs||[]).filter((t:string)=>!isEps(t))
      const left = rhs.slice(0, it.dot).join(' ')
      const right = rhs.slice(it.dot).join(' ')
      const parts: string[] = []
      if(left) parts.push(left)
      parts.push('·')
      if(right) parts.push(right)
      const body = parts.join(' ')
      return `[${it.lhs} -> ${body}, ${it.la}]`
    }).join('\n')
  }))

  const actionTerms = Array.from(new Set(Object.values(data?.action||{}).flatMap((r:any)=>Object.keys(r)))).sort()
  const gotoNonterms = Array.from(new Set(Object.values(data?.goto||{}).flatMap((r:any)=>Object.keys(r)))).sort()
  const actionCols = ['state', ...actionTerms]
  const gotoCols = ['state', ...gotoNonterms]
  const fixEps = (val: any) => (typeof val === 'string' ? val.replace(/r\[(.+?)\-\>\s*\]/g, (_m, p1) => `r[${p1}-> ε]`) : val)
  const actionRows = Object.entries(data?.action||{}).map(([st,row]:any)=>{
    const patched: any = { state: st }
    for(const k of Object.keys(row||{})) patched[k] = fixEps(row[k])
    return patched
  })
  const gotoRows = Object.entries(data?.goto||{}).map(([st,row]:any)=>({state: st, ...row}))

  const traceCols = ['Stack','Lookahead','Remaining','Action']
  const fixEpsAction = (val: string) => (typeof val==='string' ? val.replace(/(reduce\s+[^>]+->)\s*$/,'$1 ε') : val)
  const traceRows = (trace||[]).map((s:any)=>({
    Stack: (s.stack||[]).join(' '),
    Lookahead: s.lookahead,
    Remaining: (s.remaining||[]).join(' '),
    Action: fixEpsAction(s.action||''),
  }))

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-2">Grammar → LR(1)</h2>
      <textarea className="input h-40" value={text} onChange={e=>setText(e.target.value)}/>
      <div className="mt-2 flex gap-2">
        <button className="btn" onClick={onBuild} disabled={loading}>{loading? 'Construyendo…':'Construir LR(1)'}</button>
      </div>
      {data && (
        <div className="mt-4">
          {Array.isArray(data.grammar_augmented) && data.grammar_augmented.length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold mb-1">Gramática aumentada</h3>
              <pre className="text-sm whitespace-pre-wrap">{data.grammar_augmented.join('\n')}</pre>
            </div>
          )}
          {data.items_nfa?.image && (
            <div className="mb-4">
              <h3 className="font-semibold mb-1">Autómata de ítems LR(1)</h3>
              <img alt="LR(1) items NFA" src={`data:image/png;base64,${data.items_nfa.image}`} />
            </div>
          )}
          {data.items_dfa?.image && (
            <div className="mb-4">
              <h3 className="font-semibold mb-1">DFA de estados LR(1) (colección canónica)</h3>
              <img alt="LR(1) states DFA" src={`data:image/png;base64,${data.items_dfa.image}`} />
            </div>
          )}

          {(Array.isArray(data.nonterminals) || Array.isArray(data.terminals)) && (
            <div className="mb-4">
              <h3 className="text-lg font-bold uppercase border-b border-gray-300 mb-2">Símbolos</h3>
              <div className="text-sm grid md:grid-cols-2 gap-2">
                {Array.isArray(data.terminals) && (<div><div className="font-semibold">Terminales</div><div>{data.terminals.join(', ')}</div></div>)}
                {Array.isArray(data.nonterminals) && (<div><div className="font-semibold">No Terminales</div><div>{data.nonterminals.join(', ')}</div></div>)}
              </div>
            </div>
          )}

          {(data.first || data.follow) && (
            <div className="mb-4 grid md:grid-cols-2 gap-6 text-sm">
              {data.first && (
                <div>
                  <h3 className="text-lg font-bold uppercase border-b border-gray-300 mb-2">FIRST</h3>
                  <pre className="whitespace-pre-wrap">
                    {Object.entries<any>(data.first).map(([k,v])=>`FIRST(${k}) = {${(v||[]).join(', ')}}`).join('\n')}
                  </pre>
                </div>
              )}
              {data.follow && (
                <div>
                  <h3 className="text-lg font-bold uppercase border-b border-gray-300 mb-2">FOLLOW</h3>
                  <pre className="whitespace-pre-wrap">
                    {Object.entries<any>(data.follow).map(([k,v])=>`FOLLOW(${k}) = {${(v||[]).join(', ')}}`).join('\n')}
                  </pre>
                </div>
              )}
            </div>
          )}

          <div className="tabs">
            <div className={`tab ${tab==='closure'?'active':''}`} onClick={()=>setTab('closure')}>Tabla de clausura (estados/ítems)</div>
            <div className={`tab ${tab==='action'?'active':''}`} onClick={()=>setTab('action')}>Tabla de sintaxis (ACTION/GOTO)</div>
          </div>
          {tab==='closure' && (<DataTable columns={closureCols} rows={closureRows} />)}
          {tab==='action' && (
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold mb-1">ACTION</h3>
                <DataTable columns={actionCols} rows={actionRows} />
              </div>
              <div>
                <h3 className="font-semibold mb-1">GOTO</h3>
                <DataTable columns={gotoCols} rows={gotoRows} />
              </div>
            </div>
          )}

          <div className="mt-6">
            <h3 className="font-semibold mb-1">Pila de análisis (tokens separados por espacios)</h3>
            <div className="flex gap-2 items-center mb-2">
              <input className="input" placeholder="Ej: id + id * ( id )" value={traceTokens} onChange={e=>setTraceTokens(e.target.value)} />
              <button className="btn" onClick={onTrace}>Simular</button>
            </div>
            {traceErr && <div className="text-red-600 text-sm">{traceErr}</div>}
            {trace && <DataTable columns={traceCols} rows={traceRows} />}
          </div>
        </div>
      )}
    </div>
  )
}

