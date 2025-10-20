
import React, { useState } from 'react'
import { regex2nfa, nfa2dfa } from '../lib/api'
import DataTable from './DataTable'

export default function RegexPanel(){
  const [pattern, setPattern] = useState('a(b|c)*')
  const [nfa, setNfa] = useState<any|null>(null)
  const [dfa, setDfa] = useState<any|null>(null)

  async function onAFN(){
    const res = await regex2nfa(pattern)
    setNfa(res)
    setDfa(null)
  }
  async function onAFD(){
    if(!nfa) return
    const res = await nfa2dfa(nfa)
    setDfa(res)
  }

  const nfaCols = ['src','sym','dst']
  const nfaRows = (nfa?.transitions||[])
  const eclosureCols = ['state','closure']
  const eclosureRows = nfa? Object.entries(nfa.eclosure).map(([k,v]:any)=>({state:k, closure:`{${v.join(',')}}`})) : []

  const dfaCols = ['state', ...(dfa?.alphabet||[])]
  const dfaRows = dfa?.transitions||[]

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-2">Regex → AFN-ε → AFD</h2>
      <div className="flex gap-2 items-center">
        <input className="input" value={pattern} onChange={e=>setPattern(e.target.value)} placeholder="ER: a(b|c)*"/>
        <button className="btn" onClick={onAFN}>Construir AFN-ε</button>
        <button className="btn" onClick={onAFD} disabled={!nfa}>AFN→AFD</button>
      </div>

      {nfa && (
        <div className="mt-4 grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-semibold mb-1">AFN-ε (transiciones)</h3>
            <DataTable columns={nfaCols} rows={nfaRows}/>
          </div>
          <div>
            <h3 className="font-semibold mb-1">ε-closure</h3>
            <DataTable columns={eclosureCols} rows={eclosureRows}/>
          </div>
        </div>
      )}

      {dfa && (
        <div className="mt-4">
          <h3 className="font-semibold mb-1">AFD (tabla de transición)</h3>
          <DataTable columns={dfaCols} rows={dfaRows}/>
        </div>
      )}
    </div>
  )
}