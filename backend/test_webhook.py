#!/usr/bin/env python3
"""
Test script to simulate WhatsApp webhook calls
This allows testing the backend message handling logic without Venom bot
"""

import requests
import json
import time
import random
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:5001"

def simulate_whatsapp_message(phone_number, message_text, is_from_me=False):
    """Simulate a WhatsApp message webhook call"""
    
    # Create webhook payload similar to what Venom bot sends
    webhook_data = {
        "event": "onmessage",
        "data": {
            "key": {
                "remoteJid": f"{phone_number}@s.whatsapp.net",
                "fromMe": is_from_me,
                "id": f"test_msg_{int(time.time())}_{random.randint(1000, 9999)}"
            },
            "message": {
                "conversation": message_text
            },
            "messageTimestamp": int(time.time()),
            "pushName": "Test User" if not is_from_me else "Bot"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📤 Sent message: {message_text}")
        print(f"   From: {phone_number}")
        print(f"   Response: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        print()
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return False

def test_conversation_flow():
    """Test a complete conversation flow"""
    
    test_phone = "5511999999999"
    
    print("🧪 Starting WhatsApp message simulation test...")
    print("=" * 50)
    
    # Test 1: Initial greeting from user
    print("1️⃣ Testing initial user message...")
    simulate_whatsapp_message(test_phone, "Olá, gostaria de agendar uma consulta")
    time.sleep(2)
    
    # Test 2: User provides name
    print("2️⃣ Testing user provides name...")
    simulate_whatsapp_message(test_phone, "Meu nome é João Silva")
    time.sleep(2)
    
    # Test 3: User provides phone
    print("3️⃣ Testing user provides phone...")
    simulate_whatsapp_message(test_phone, "Meu telefone é 11988887777")
    time.sleep(2)
    
    # Test 4: User provides CPF
    print("4️⃣ Testing user provides CPF...")
    simulate_whatsapp_message(test_phone, "Meu CPF é 12345678901")
    time.sleep(2)
    
    # Test 5: User confirms appointment
    print("5️⃣ Testing user confirms appointment...")
    simulate_whatsapp_message(test_phone, "Sim, confirmo o agendamento")
    time.sleep(2)
    
    print("✅ Test conversation completed!")
    print("Check the frontend at http://localhost:3001 to see if messages appear")

def test_multiple_conversations():
    """Test multiple conversations simultaneously"""
    
    print("🧪 Testing multiple conversations...")
    print("=" * 50)
    
    conversations = [
        ("5511111111111", "Maria Santos"),
        ("5522222222222", "Pedro Oliveira"),
        ("5533333333333", "Ana Costa")
    ]
    
    for phone, name in conversations:
        print(f"📱 Testing conversation with {name} ({phone})...")
        simulate_whatsapp_message(phone, f"Oi, sou {name}, quero agendar consulta")
        time.sleep(1)
        simulate_whatsapp_message(phone, f"Meu nome é {name}")
        time.sleep(1)
        print()

def check_backend_status():
    """Check if backend is running and responsive"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and responsive")
            return True
        else:
            print(f"⚠️ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is not responding: {e}")
        return False

def main():
    """Main test function"""
    
    print("🤖 WhatsApp Message Simulation Test")
    print("=" * 40)
    
    # Check if backend is running
    if not check_backend_status():
        print("❌ Backend is not running. Please start the backend first.")
        print("   Run: cd backend && python app.py")
        return
    
    print()
    print("Choose test option:")
    print("1. Single conversation flow")
    print("2. Multiple conversations")
    print("3. Custom message")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_conversation_flow()
    elif choice == "2":
        test_multiple_conversations()
    elif choice == "3":
        phone = input("Enter phone number (e.g., 5511999999999): ").strip()
        message = input("Enter message: ").strip()
        simulate_whatsapp_message(phone, message)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main() 