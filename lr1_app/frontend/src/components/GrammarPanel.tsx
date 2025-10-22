import React, { useState } from 'react'
import { buildLR1 } from '../lib/api'
import DataTable from './DataTable'

const EXPR = `START: E
NONTERMINALS: E T F
TERMINALS: id + * ( )
PRODUCTIONS:
  E -> E + T | T
  T -> T * F | F
  F -> ( E ) | id
LEXER:
  id:      /[a-zA-Z_]\\w*/
  '+':     /\\+/
  '*':     /\\*/
  '(':     /\\(/
  ')':     /\\)/
  WS:      /\\s+/ skip`;

export default function GrammarPanel(){
  const [text, setText] = useState(EXPR)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any|null>(null)
  const [tab, setTab] = useState<'closure'|'action'>('closure')

  async function onBuild(){
    setLoading(true)
    try{
      const res = await buildLR1(text)
      setData(res)
    }finally{ setLoading(false) }
  }

  const closureCols = ['state','items']
  const closureRows = (data?.states||[]).map((s:any)=>({
    state: s.state,
    items: s.items.map((it:any)=>{
      const left = it.rhs.slice(0, it.dot).join(' ')
      const right = it.rhs.slice(it.dot).join(' ')
      const body = [left, '·', right].filter(Boolean).join(' ').trim()
      return `[${it.lhs} -> ${body}, ${it.la}]`
    }).join('\n')
  }))

  const actionTerms = Array.from(new Set(Object.values(data?.action||{}).flatMap((r:any)=>Object.keys(r)))).sort()
  const gotoNonterms = Array.from(new Set(Object.values(data?.goto||{}).flatMap((r:any)=>Object.keys(r)))).sort()
  const actionCols = ['state', ...actionTerms]
  const gotoCols = ['state', ...gotoNonterms]
  const actionRows = Object.entries(data?.action||{}).map(([st,row]:any)=>({state: st, ...row}))
  const gotoRows = Object.entries(data?.goto||{}).map(([st,row]:any)=>({state: st, ...row}))

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
          {(Array.isArray(data.nonterminals) || Array.isArray(data.terminals)) && (
            <div className="mb-4">
              <h3 className="font-semibold mb-1">Símbolos</h3>
              <div className="text-sm">
                {Array.isArray(data.nonterminals) && (<div><b>No terminales:</b> {data.nonterminals.join(', ')}</div>)}
                {Array.isArray(data.terminals) && (<div><b>Terminales:</b> {data.terminals.join(', ')}</div>)}
              </div>
            </div>
          )}
          {(data.first || data.follow) && (
            <div className="mb-4 grid md:grid-cols-2 gap-4 text-sm">
              {data.first && (
                <div>
                  <h3 className="font-semibold mb-1">FIRST</h3>
                  <pre className="whitespace-pre-wrap">
                    {Object.entries<any>(data.first).map(([k,v])=>`${k}: {${(v||[]).join(', ')}}`).join('\n')}
                  </pre>
                </div>
              )}
              {data.follow && (
                <div>
                  <h3 className="font-semibold mb-1">FOLLOW</h3>
                  <pre className="whitespace-pre-wrap">
                    {Object.entries<any>(data.follow).map(([k,v])=>`${k}: {${(v||[]).join(', ')}}`).join('\n')}
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
        </div>
      )}
    </div>
  )
}
