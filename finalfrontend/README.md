# WhatsApp Organizer Frontend

A modern WhatsApp-like dashboard for managing conversations and messages, built with React and Vite.

## Features

- 📱 WhatsApp-like interface design
- 💬 Real-time message management
- 🔍 Search conversations
- 📋 Conversation list with unread indicators
- ✨ Modern UI with responsive design
- 🎯 Context-based state management

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Navigation
- **Axios** - HTTP client for API calls
- **Lucide React** - Icon library
- **CSS** - Styling with WhatsApp-inspired design

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd finalfrontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser and visit `http://localhost:3001`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Sidebar.jsx     # Conversation list
│   ├── Header.jsx      # Chat header
│   ├── ChatWindow.jsx  # Message display
│   └── MessageInput.jsx # Message input
├── context/            # React Context for state management
│   └── ChatContext.jsx # Chat state and actions
├── pages/              # Page components
│   └── Dashboard.jsx   # Main dashboard page
├── utils/              # Utility functions
│   └── api.js         # API integration
├── App.jsx            # Main app component
└── main.jsx           # App entry point
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend Integration

The frontend is prepared for backend integration with the following API endpoints:

- `GET /api/conversations` - Get all conversations
- `GET /api/conversations/:id` - Get specific conversation
- `GET /api/conversations/:id/messages` - Get messages for conversation
- `POST /api/conversations/:id/messages` - Send a message
- `PUT /api/conversations/:id/messages/read` - Mark messages as read

## Features in Detail

### Sidebar
- Displays list of conversations
- Search functionality
- Unread message indicators
- Active conversation highlighting

### Chat Window
- Message bubbles with timestamps
- Different styles for sent/received messages
- Auto-scroll to latest message
- Empty state when no conversation selected

### Message Input
- Auto-resizing textarea
- Send button appears when typing
- Emoji and attachment buttons (ready for implementation)
- Voice message button

### Header
- Contact information display
- Action buttons (search, call, video, menu)
- Welcome message when no conversation selected

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
