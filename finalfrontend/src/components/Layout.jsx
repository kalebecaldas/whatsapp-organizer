import { ChatProvider } from '../context/ChatContext';
import { useLocation } from 'react-router-dom';
import Menu from './Menu';
import Sidebar from './Sidebar';
import Header from './Header';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();
  
  // Sidebar só nas páginas que precisam (não na página Messages)
  const pagesWithSidebar = []; // Removido '/messages' pois ela terá sua própria sidebar
  const shouldShowSidebar = pagesWithSidebar.includes(location.pathname);

  return (
    <ChatProvider>
      <div className="layout">
        <Menu />
        {shouldShowSidebar && <Sidebar />}
        <div className={`main-content ${!shouldShowSidebar ? 'full-width' : ''}`}>
          <Header />
          <div className="page-content">
            {children}
          </div>
        </div>
      </div>
    </ChatProvider>
  );
};

export default Layout; 