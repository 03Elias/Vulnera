import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Submit from './page/Submitpage';
import './page/submit.css';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Submit/>
  </StrictMode>,
)
