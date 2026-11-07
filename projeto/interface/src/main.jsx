import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';

class ErrorBoundary extends React.Component {
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  render(){
    if(this.state.failed) return <main className="mx-auto max-w-xl px-6 py-20"><h1 className="text-2xl font-medium">Não foi possível abrir o painel</h1><p className="mt-4 text-secondary">Recarregue a página. Se o problema continuar, confira a exportação dos dados oficiais.</p><button className="button-secondary mt-6" onClick={()=>window.location.reload()}>Recarregar</button></main>;
    return this.props.children;
  }
}
createRoot(document.getElementById('root')).render(<React.StrictMode><ErrorBoundary><App/></ErrorBoundary></React.StrictMode>);
