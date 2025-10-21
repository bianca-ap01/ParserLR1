
import React, { useState } from 'react'
import { buildLR1 } from '../lib/api'
import DataTable from './DataTable'

const EXPR =
`E -> E + T
E -> T
T -> T * F
T -> F
F -> ( E )
F -> id
`;

export default function GrammarPanel(){
  const [text, setText] = useState(EXPR)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any|null>(null)
  const [tab, setTab] = useState<'closure'|'action'|'analysis'|'automata'>('closure')

  async function onBuild(){
    setLoading(true)
    try{
      const res = await buildLR1(text)
      setData(res)
    }finally{ setLoading(false) }
  }

  const closureCols = ['state','items']
  // Inferir no terminales del usuario desde el texto
  const userNonterms = Array.from(new Set(
    text.split('\n')
      .map(ln => ln.trim())
      .filter(ln => ln.includes('->'))
      .map(ln => ln.split('->')[0].trim())
  ));

  // Filtrar ítems de la tabla de clausura para mostrar solo los del usuario
  const closureRows = (data?.states||[]).map((s:any)=>({
    state: s.state,
    items: s.items
      .filter((it:any)=>userNonterms.includes(it.lhs))
      .map((it:any)=>`[${it.lhs} → ${[...it.rhs.slice(0,it.dot),'·',...it.rhs.slice(it.dot)].join(' ')}, ${it.la}]`).join('\n')
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
          {/* Mostrar la gramática aumentada antes de las pestañas */}
          <div className="mb-4">
            <h3 className="font-semibold">Gramática aumentada</h3>
            <pre className="bg-gray-100 p-2 rounded text-sm">
              {(data.grammar_augmented||[]).join('\n')}
            </pre>
          </div>
          <div className="tabs">
            <div className={`tab ${tab==='closure'?'active':''}`} onClick={()=>setTab('closure')}>Tabla de clausura (estados/ítems)</div>
            <div className={`tab ${tab==='action'?'active':''}`} onClick={()=>setTab('action')}>Tabla de sintaxis (ACTION/GOTO)</div>
            <div className={`tab ${tab==='analysis'?'active':''}`} onClick={()=>setTab('analysis')}>Análisis (FIRST / FOLLOW)</div>
            <div className={`tab ${tab==='automata'?'active':''}`} onClick={()=>setTab('automata')}>Autómatas (AFN/AFD)</div>
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
          {tab==='automata' && (
            <div className="mt-2">
              <div className="mt-4 mb-1 text-base font-semibold border-b border-indigo-200 text-indigo-900">Autómatas generados por terminal</div>
              {(data?.nfa && Object.keys(data.nfa).length > 0) ? (
                Object.entries(data.nfa).map(([term, nfa]:any) => (
                  <div key={term} className="mb-6 p-4 border rounded-lg bg-gray-50">
                    <div className="font-semibold text-lg mb-2">Terminal: <span className="font-mono bg-white px-2 py-1 rounded border">{term}</span></div>
                    
                    <div className="mb-4">
                      <div className="font-medium mb-2">AFN:</div>
                      {nfa.error ? (
                        <div className="text-red-600">Error: {nfa.error}</div>
                      ) : nfa.success?.image ? (
                        <div className="space-y-2">
                          <img 
                            src={`data:image/png;base64,${nfa.success.image}`}
                            alt={`AFN para ${term}`}
                            className="max-w-full h-auto border rounded"
                          />
                        </div>
                      ) : (
                        <div className="text-gray-500 italic">No se pudo generar la imagen del autómata.</div>
                      )}
                    </div>

                    <div>
                      <div className="font-medium mb-2">AFD:</div>
                      {data.dfa?.[term]?.error ? (
                        <div className="text-red-600">Error: {data.dfa[term].error}</div>
                      ) : data.dfa[term]?.success?.image ? (
                        <div className="space-y-2">
                          <img 
                            src={`data:image/png;base64,${data.dfa[term].success.image}`}
                            alt={`AFD para ${term}`}
                            className="max-w-full h-auto border rounded"
                          />
                        </div>
                      ) : (
                        <div className="text-gray-500 italic">No se pudo generar la imagen del autómata.</div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-gray-500 italic">No se detectaron reglas léxicas para procesar.</div>
              )}
            </div>
          )}
          {tab==='analysis' && (
            <div className="mt-2">
              <div className="mt-4 mb-1 text-base font-semibold border-b border-blue-200 text-blue-900">Terminales</div>
              <div className="mb-2 flex flex-wrap gap-2">
                {(data?.terminals||[]).map((t: string) => (
                  <span key={t} className="px-2 py-1 rounded bg-blue-100 text-blue-800 text-sm border border-blue-200">{t}</span>
                ))}
              </div>
              <div className="mt-4 mb-1 text-base font-semibold border-b border-green-200 text-green-900">No terminales</div>
              <div className="mb-2 flex flex-wrap gap-2">
                {(data?.nonterminals||[]).map((nt: string) => (
                  <span key={nt} className="px-2 py-1 rounded bg-green-100 text-green-800 text-sm border border-green-200">{nt}</span>
                ))}
              </div>
              <div className="mt-4 mb-1 text-base font-semibold border-b border-purple-200 text-purple-900">FIRST</div>
              <div className="mb-2">
                {(Object.entries(data?.first||{})).map(([X, arr]:any)=> (
                  <div key={X}><strong>FIRST({X})</strong>: {arr.join(', ')}</div>
                ))}
              </div>
              <div className="mt-4 mb-1 text-base font-semibold border-b border-yellow-200 text-yellow-900">FOLLOW</div>
              <div className="mb-2">
                {(Object.entries(data?.follow||{})).map(([A, arr]:any) => (
                  <div key={A}><strong>FOLLOW({A})</strong>: {arr.join(', ')}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}