
import React from 'react'

type Props = { columns: string[], rows: any[] }
export default function DataTable({columns, rows}: Props){
  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>{columns.map(c=> <th key={c}>{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r,i)=>(
            <tr key={i}>
              {columns.map(c=> <td key={c}><pre className="whitespace-pre-wrap m-0">{String(r[c] ?? '')}</pre></td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}