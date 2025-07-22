import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "messages.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        message_text TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        from_field TEXT DEFAULT 'user',
                        session_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create conversations table for better reporting
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        assigned_to TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        closed_at DATETIME,
                        procedure_type TEXT,
                        transfer_count INTEGER DEFAULT 0,
                        message_count INTEGER DEFAULT 0,
                        avg_response_time INTEGER DEFAULT 0
                    )
                ''')
                
                # Create agents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS agents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE,
                        status TEXT DEFAULT 'offline',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_active DATETIME
                    )
                ''')
                
                # Create conversation_metrics table for detailed analytics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER,
                        date DATE,
                        messages_count INTEGER DEFAULT 0,
                        response_time_avg INTEGER DEFAULT 0,
                        satisfaction_score REAL DEFAULT 0,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                    )
                ''')
                
                # Create indexes for faster queries
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone_number ON messages(phone_number)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_status ON conversations(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_phone ON conversations(phone_number)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_status ON agents(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_date ON conversation_metrics(date)')
                
                conn.commit()
                logger.info("✅ Database initialized successfully with reporting tables")
                
        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
            raise
    
    def save_message(self, phone_number: str, message_text: str, direction: str, 
                    from_field: str = "user", session_data: Optional[Dict] = None, 
                    timestamp: Optional[str] = None) -> bool:
        """Save a message to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                session_json = json.dumps(session_data) if session_data else None
                
                if timestamp:
                    cursor.execute('''
                        INSERT INTO messages (phone_number, message_text, direction, from_field, session_data, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (phone_number, message_text, direction, from_field, session_json, timestamp))
                else:
                    cursor.execute('''
                        INSERT INTO messages (phone_number, message_text, direction, from_field, session_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (phone_number, message_text, direction, from_field, session_json))
                
                # Update conversation metrics
                self._update_conversation_metrics(phone_number)
                
                conn.commit()
                logger.info(f"✅ Message saved for {phone_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error saving message: {e}")
            return False
    
    def _update_conversation_metrics(self, phone_number: str):
        """Update conversation metrics when a message is saved"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get or create conversation
                cursor.execute('''
                    SELECT id FROM conversations 
                    WHERE phone_number = ? AND status = 'active'
                ''', (phone_number,))
                
                result = cursor.fetchone()
                if result:
                    conversation_id = result[0]
                else:
                    # Create new conversation
                    cursor.execute('''
                        INSERT INTO conversations (phone_number, status)
                        VALUES (?, 'active')
                    ''', (phone_number,))
                    conversation_id = cursor.lastrowid
                
                # Update message count
                cursor.execute('''
                    UPDATE conversations 
                    SET message_count = (
                        SELECT COUNT(*) FROM messages WHERE phone_number = ?
                    )
                    WHERE id = ?
                ''', (phone_number, conversation_id))
                
                # Calculate average response time
                cursor.execute('''
                    UPDATE conversations 
                    SET avg_response_time = (
                        SELECT AVG(
                            CAST(
                                (julianday(m2.timestamp) - julianday(m1.timestamp)) * 24 * 60 * 60 
                                AS INTEGER
                            )
                        )
                        FROM messages m1
                        JOIN messages m2 ON m1.phone_number = m2.phone_number
                        WHERE m1.phone_number = ? 
                        AND m1.direction = 'received' 
                        AND m2.direction = 'sent'
                        AND m2.timestamp > m1.timestamp
                    )
                    WHERE id = ?
                ''', (phone_number, conversation_id))
                
        except Exception as e:
            logger.error(f"❌ Error updating conversation metrics: {e}")
    
    def get_messages(self, limit: int = 100) -> List[Dict]:
        """Get all messages ordered by timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM messages 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                messages = []
                for row in cursor.fetchall():
                    message = {
                        'id': row['id'],
                        'phone_number': row['phone_number'],
                        'message_text': row['message_text'],
                        'direction': row['direction'],
                        'from': row['from_field'],
                        'timestamp': row['timestamp'],
                        'session_data': json.loads(row['session_data']) if row['session_data'] else None,
                        'created_at': row['created_at']
                    }
                    messages.append(message)
                
                return messages
                
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    def get_messages_by_phone(self, phone_number: str, limit: int = 50) -> List[Dict]:
        """Get messages for a specific phone number"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE phone_number = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (phone_number, limit))
                
                messages = []
                for row in cursor.fetchall():
                    message = {
                        'id': row['id'],
                        'phone_number': row['phone_number'],
                        'message_text': row['message_text'],
                        'direction': row['direction'],
                        'from': row['from_field'],
                        'timestamp': row['timestamp'],
                        'session_data': json.loads(row['session_data']) if row['session_data'] else None,
                        'created_at': row['created_at']
                    }
                    messages.append(message)
                
                return messages
                
        except Exception as e:
            logger.error(f"❌ Error getting messages for {phone_number}: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get message statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total messages
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                
                # Messages today
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE DATE(timestamp) = DATE('now')
                ''')
                messages_today = cursor.fetchone()[0]
                
                # Unique phone numbers
                cursor.execute('SELECT COUNT(DISTINCT phone_number) FROM messages')
                unique_phones = cursor.fetchone()[0]
                
                # Messages by direction
                cursor.execute('''
                    SELECT direction, COUNT(*) as count 
                    FROM messages 
                    GROUP BY direction
                ''')
                direction_stats = dict(cursor.fetchall())
                
                return {
                    'total_messages': total_messages,
                    'messages_today': messages_today,
                    'unique_phones': unique_phones,
                    'direction_stats': direction_stats
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {
                'total_messages': 0,
                'messages_today': 0,
                'unique_phones': 0,
                'direction_stats': {}
            }
    
    def get_reporting_data(self, period: str = '24h', filters: Optional[Dict] = None) -> Dict:
        """Get comprehensive reporting data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate date range based on period
                now = datetime.now()
                if period == '24h':
                    start_date = now - timedelta(days=1)
                elif period == '7d':
                    start_date = now - timedelta(days=7)
                elif period == '30d':
                    start_date = now - timedelta(days=30)
                elif period == '90d':
                    start_date = now - timedelta(days=90)
                else:
                    start_date = now - timedelta(days=1)
                
                # Get conversation statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                        SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed,
                        SUM(CASE WHEN transfer_count > 0 THEN 1 ELSE 0 END) as transferred
                    FROM conversations 
                    WHERE created_at >= ?
                ''', (start_date.isoformat(),))
                
                conv_stats = cursor.fetchone()
                
                # Get message statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN direction = 'received' THEN 1 ELSE 0 END) as received,
                        SUM(CASE WHEN direction = 'sent' THEN 1 ELSE 0 END) as sent,
                        AVG(avg_response_time) as avg_response_time
                    FROM messages m
                    JOIN conversations c ON m.phone_number = c.phone_number
                    WHERE m.timestamp >= ?
                ''', (start_date.isoformat(),))
                
                msg_stats = cursor.fetchone()
                
                # Get agent performance
                cursor.execute('''
                    SELECT 
                        name,
                        COUNT(c.id) as conversations,
                        AVG(c.avg_response_time) as avg_time,
                        AVG(cm.satisfaction_score) as satisfaction
                    FROM agents a
                    LEFT JOIN conversations c ON a.name = c.assigned_to
                    LEFT JOIN conversation_metrics cm ON c.id = cm.conversation_id
                    WHERE a.status = 'online'
                    GROUP BY a.id, a.name
                ''')
                
                agents_performance = []
                for row in cursor.fetchall():
                    agents_performance.append({
                        'name': row[0],
                        'conversations': row[1] or 0,
                        'avgTime': f"{int(row[2] or 0)}s",
                        'satisfaction': round(row[3] or 4.5, 1)
                    })
                
                # Get daily trends
                cursor.execute('''
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(DISTINCT phone_number) as conversations,
                        COUNT(*) as messages
                    FROM messages 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                    LIMIT 7
                ''', (start_date.isoformat(),))
                
                daily_trends = []
                for row in cursor.fetchall():
                    daily_trends.append({
                        'date': row[0],
                        'conversations': row[1],
                        'messages': row[2]
                    })
                
                return {
                    'conversations': {
                        'total': conv_stats[0] or 0,
                        'active': conv_stats[1] or 0,
                        'closed': conv_stats[2] or 0,
                        'transferred': conv_stats[3] or 0
                    },
                    'messages': {
                        'total': msg_stats[0] or 0,
                        'received': msg_stats[1] or 0,
                        'sent': msg_stats[2] or 0,
                        'avgResponseTime': f"{int(msg_stats[3] or 0)}s"
                    },
                    'agents': {
                        'online': len(agents_performance),
                        'total': len(agents_performance),
                        'performance': agents_performance
                    },
                    'trends': {
                        'daily': daily_trends,
                        'weekly': [],  # TODO: Implement weekly aggregation
                        'monthly': []   # TODO: Implement monthly aggregation
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting reporting data: {e}")
            return {
                'conversations': {'total': 0, 'active': 0, 'closed': 0, 'transferred': 0},
                'messages': {'total': 0, 'received': 0, 'sent': 0, 'avgResponseTime': '0s'},
                'agents': {'online': 0, 'total': 0, 'performance': []},
                'trends': {'daily': [], 'weekly': [], 'monthly': []}
            }
    
    def migrate_old_messages(self, old_messages: List[Dict]) -> bool:
        """Migrate old messages from Redis or other format"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for msg in old_messages:
                    # Normalize the 'from' field
                    from_field = msg.get('from', 'user')
                    if from_field == 'bot':
                        from_field = 'agent'
                    
                    session_data = msg.get('session_data')
                    session_json = json.dumps(session_data) if session_data else None
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO messages 
                        (phone_number, message_text, direction, from_field, session_data, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        msg.get('phone_number', ''),
                        msg.get('message_text', ''),
                        msg.get('direction', 'received'),
                        from_field,
                        session_json,
                        msg.get('timestamp', datetime.now().isoformat())
                    ))
                
                conn.commit()
                logger.info(f"✅ Migrated {len(old_messages)} messages")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error migrating messages: {e}")
            return False
    
    def clear_messages(self) -> bool:
        """Clear all messages (for testing)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM messages')
                cursor.execute('DELETE FROM conversations')
                cursor.execute('DELETE FROM conversation_metrics')
                conn.commit()
                logger.info("✅ All messages cleared")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error clearing messages: {e}")
            return False

# Global database instance
db = Database() 