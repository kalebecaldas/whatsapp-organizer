import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Reports from './pages/Reports';
import Layout from './components/Layout';
import './App.css';
import BotTest from './pages/BotTest';

function App() {
  console.log('🚀 App.jsx renderizado');
  
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/messages" element={<Dashboard />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/users" element={<Dashboard />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/bottest" element={<BotTest />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  );
}

export default App;
