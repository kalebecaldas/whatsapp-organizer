import ChatWindow from '../components/ChatWindow';
import MessageInput from '../components/MessageInput';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard-content">
      <ChatWindow />
      <MessageInput />
    </div>
  );
};

export default Dashboard; 