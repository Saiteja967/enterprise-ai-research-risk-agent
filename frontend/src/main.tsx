import {createRoot} from 'react-dom/client'
import {useState} from 'react'
import {api} from './api'
import type {Report} from './types'
function Slice(){const [report,set]=useState<Report>();return <main><h1>Meridian research workspace</h1><button onClick={async()=>set(await api<Report>('reports',{company:'ABC',question:'Analyze receivables aging and distributor settlement changes.',confirm:true}))}>Run and save research</button>{report?.findings.map(f=><p key={f.citation}>{f.text} [{f.citation}]</p>)}</main>}
createRoot(document.getElementById('root')!).render(<Slice/>)

