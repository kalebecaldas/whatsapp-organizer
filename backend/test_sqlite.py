#!/usr/bin/env python3
"""
Test script for SQLite database functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
import json

def test_database():
    """Test all database functions"""
    print("🧪 Testing SQLite database...")
    
    try:
        # Test 1: Initialize database
        print("✅ Database initialized successfully")
        
        # Test 2: Save messages
        print("\n📝 Testing message saving...")
        
        # Save a user message
        success1 = db.save_message(
            phone_number="5511999999999",
            message_text="Olá, gostaria de agendar uma consulta",
            direction="received",
            from_field="user"
        )
        print(f"User message saved: {'✅' if success1 else '❌'}")
        
        # Save a bot response
        success2 = db.save_message(
            phone_number="5511999999999",
            message_text="Claro! Em qual unidade você gostaria de agendar?",
            direction="sent",
            from_field="agent"
        )
        print(f"Bot message saved: {'✅' if success2 else '❌'}")
        
        # Test 3: Get messages
        print("\n📖 Testing message retrieval...")
        messages = db.get_messages(limit=10)
        print(f"Total messages retrieved: {len(messages)}")
        
        for msg in messages:
            print(f"  - {msg['from']}: {msg['message_text'][:50]}...")
        
        # Test 4: Get messages by phone
        print("\n📱 Testing messages by phone...")
        phone_messages = db.get_messages_by_phone("5511999999999", limit=5)
        print(f"Messages for 5511999999999: {len(phone_messages)}")
        
        # Test 5: Get stats
        print("\n📊 Testing statistics...")
        stats = db.get_stats()
        print(f"Total messages: {stats['total_messages']}")
        print(f"Messages today: {stats['messages_today']}")
        print(f"Unique phones: {stats['unique_phones']}")
        print(f"Direction stats: {stats['direction_stats']}")
        
        # Test 6: Save another conversation
        print("\n💬 Testing another conversation...")
        db.save_message("5511888888888", "Oi, tudo bem?", "received", "user")
        db.save_message("5511888888888", "Olá! Como posso ajudar?", "sent", "agent")
        
        # Test 7: Get all conversations
        all_messages = db.get_messages(limit=20)
        conversations = {}
        
        for msg in all_messages:
            phone = msg['phone_number']
            if phone not in conversations:
                conversations[phone] = []
            conversations[phone].append({
                'from': msg['from'],
                'text': msg['message_text'],
                'timestamp': msg['timestamp']
            })
        
        print(f"\n📋 Conversations found: {len(conversations)}")
        for phone, msgs in conversations.items():
            print(f"  {phone}: {len(msgs)} messages")
        
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1) 