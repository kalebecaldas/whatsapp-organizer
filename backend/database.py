import sqlite3
import json
import os
from datetime import datetime
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
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_phone_number 
                    ON messages(phone_number)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON messages(timestamp)
                ''')
                
                conn.commit()
                logger.info("✅ Database initialized successfully")
                
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
                
                conn.commit()
                logger.info(f"✅ Message saved for {phone_number}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error saving message: {e}")
            return False
    
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
                conn.commit()
                logger.info("✅ All messages cleared")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error clearing messages: {e}")
            return False

# Global database instance
db = Database() 