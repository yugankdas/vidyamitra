import React from 'react'
import ReactDOM from 'react-dom/client'
import { HeroDemo } from '@/components/ui/demo'
import './index.css'

const heroRoot = document.getElementById('hero-root')
if (heroRoot) {
  ReactDOM.createRoot(heroRoot).render(
    <React.StrictMode>
      <HeroDemo />
    </React.StrictMode>,
  )
}
