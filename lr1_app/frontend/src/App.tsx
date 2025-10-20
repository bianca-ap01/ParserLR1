
import React from 'react'
import GrammarPanel from './components/GrammarPanel'
import RegexPanel from './components/RegexPanel'

export default function App(){
  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">LR(1) Toolkit — Sintaxis y Autómatas</h1>
      <GrammarPanel/>
      <RegexPanel/>
    </div>
  )
}