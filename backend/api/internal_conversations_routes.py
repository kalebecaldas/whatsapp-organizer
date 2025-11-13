from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from database import db
from flask_socketio import emit
from datetime import datetime
import json
import logging
import sqlite3
import os

logger = logging.getLogger(__name__)

internal_bp = Blueprint("internal_conversations", __name__)

# Global variable to store socketio instance
socketio = None

def init_internal_socketio(sio):
    global socketio
    socketio = sio

def get_db_connection():
    """Get database connection"""
    db_path = os.getenv("DB_PATH", "messages.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@internal_bp.route("/internal-conversations", methods=["GET"])
@cross_origin()
def get_internal_conversations():
    """Get all internal conversations for the current user"""
    try:
        user_id = request.args.get('user_id', 'current-user')  # TODO: Get from auth
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversations where user is a member
        cursor.execute('''
            SELECT DISTINCT ic.*, 
                   (SELECT COUNT(*) FROM internal_messages im 
                    WHERE im.conversation_id = ic.id) as message_count,
                   (SELECT content FROM internal_messages im 
                    WHERE im.conversation_id = ic.id 
                    ORDER BY im.timestamp DESC LIMIT 1) as last_message,
                   (SELECT timestamp FROM internal_messages im 
                    WHERE im.conversation_id = ic.id 
                    ORDER BY im.timestamp DESC LIMIT 1) as last_message_time
            FROM internal_conversations ic
            INNER JOIN internal_conversation_members icm ON ic.id = icm.conversation_id
            WHERE icm.user_id = ?
            ORDER BY ic.updated_at DESC
        ''', (user_id,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row['id'],
                'name': row['name'],
                'type': row['type'],
                'description': row['description'],
                'avatar': row['avatar'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'message_count': row['message_count'] or 0,
                'last_message': row['last_message'],
                'last_message_time': row['last_message_time']
            })
        
        conn.close()
        return jsonify({'conversations': conversations})
        
    except Exception as e:
        logger.error(f"❌ Error getting internal conversations: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations", methods=["POST"])
@cross_origin()
def create_internal_conversation():
    """Create a new internal conversation (direct or group)"""
    try:
        data = request.get_json()
        name = data.get('name')
        conversation_type = data.get('type', 'direct')
        description = data.get('description')
        member_ids = data.get('member_ids', [])
        creator_id = data.get('creator_id', 'current-user')  # TODO: Get from auth
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        if conversation_type == 'direct' and len(member_ids) != 1:
            return jsonify({'error': 'Direct conversation must have exactly one other member'}), 400
        
        if conversation_type == 'group' and len(member_ids) < 1:
            return jsonify({'error': 'Group conversation must have at least one member'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create conversation
        cursor.execute('''
            INSERT INTO internal_conversations (name, type, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, conversation_type, description, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conversation_id = cursor.lastrowid
        
        # Add creator as admin
        cursor.execute('''
            INSERT INTO internal_conversation_members (conversation_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, creator_id, 'admin', datetime.now().isoformat()))
        
        # Add other members
        for member_id in member_ids:
            cursor.execute('''
                INSERT INTO internal_conversation_members (conversation_id, user_id, role, joined_at)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, member_id, 'member', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_conversation_update', {
                'type': 'created',
                'conversation_id': conversation_id
            })
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'message': 'Conversation created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error creating internal conversation: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>", methods=["GET"])
@cross_origin()
def get_internal_conversation(conversation_id):
    """Get details of a specific internal conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversation
        cursor.execute('''
            SELECT * FROM internal_conversations WHERE id = ?
        ''', (conversation_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Get members
        cursor.execute('''
            SELECT user_id, role, joined_at FROM internal_conversation_members
            WHERE conversation_id = ?
        ''', (conversation_id,))
        
        members = []
        for member_row in cursor.fetchall():
            members.append({
                'user_id': member_row['user_id'],
                'role': member_row['role'],
                'joined_at': member_row['joined_at']
            })
        
        conn.close()
        
        return jsonify({
            'id': row['id'],
            'name': row['name'],
            'type': row['type'],
            'description': row['description'],
            'avatar': row['avatar'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'members': members
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting internal conversation: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>", methods=["PUT"])
@cross_origin()
def update_internal_conversation(conversation_id):
    """Update an internal conversation"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update conversation
        updates = []
        params = []
        
        if name:
            updates.append('name = ?')
            params.append(name)
        
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        
        if not updates:
            conn.close()
            return jsonify({'error': 'No fields to update'}), 400
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        params.append(conversation_id)
        
        cursor.execute(f'''
            UPDATE internal_conversations
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_conversation_update', {
                'type': 'updated',
                'conversation_id': conversation_id
            })
        
        return jsonify({'success': True, 'message': 'Conversation updated successfully'})
        
    except Exception as e:
        logger.error(f"❌ Error updating internal conversation: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>", methods=["DELETE"])
@cross_origin()
def delete_internal_conversation(conversation_id):
    """Delete an internal conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM internal_conversations WHERE id = ?', (conversation_id,))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_conversation_update', {
                'type': 'deleted',
                'conversation_id': conversation_id
            })
        
        return jsonify({'success': True, 'message': 'Conversation deleted successfully'})
        
    except Exception as e:
        logger.error(f"❌ Error deleting internal conversation: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>/members", methods=["POST"])
@cross_origin()
def add_member(conversation_id):
    """Add a member to an internal conversation"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if member already exists
        cursor.execute('''
            SELECT id FROM internal_conversation_members
            WHERE conversation_id = ? AND user_id = ?
        ''', (conversation_id, user_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User is already a member'}), 400
        
        # Add member
        cursor.execute('''
            INSERT INTO internal_conversation_members (conversation_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, user_id, 'member', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_conversation_update', {
                'type': 'member_added',
                'conversation_id': conversation_id,
                'user_id': user_id
            })
        
        return jsonify({'success': True, 'message': 'Member added successfully'})
        
    except Exception as e:
        logger.error(f"❌ Error adding member: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>/members/<user_id>", methods=["DELETE"])
@cross_origin()
def remove_member(conversation_id, user_id):
    """Remove a member from an internal conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM internal_conversation_members
            WHERE conversation_id = ? AND user_id = ?
        ''', (conversation_id, user_id))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_conversation_update', {
                'type': 'member_removed',
                'conversation_id': conversation_id,
                'user_id': user_id
            })
        
        return jsonify({'success': True, 'message': 'Member removed successfully'})
        
    except Exception as e:
        logger.error(f"❌ Error removing member: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>/messages", methods=["GET"])
@cross_origin()
def get_internal_messages(conversation_id):
    """Get messages for an internal conversation"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM internal_messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (conversation_id, limit, offset))
        
        messages = []
        for row in cursor.fetchall():
            metadata = json.loads(row['metadata']) if row['metadata'] else None
            messages.append({
                'id': row['id'],
                'conversation_id': row['conversation_id'],
                'sender_id': row['sender_id'],
                'content': row['content'],
                'message_type': row['message_type'],
                'metadata': metadata,
                'timestamp': row['timestamp']
            })
        
        conn.close()
        
        # Reverse to show oldest first
        messages.reverse()
        
        return jsonify({'messages': messages})
        
    except Exception as e:
        logger.error(f"❌ Error getting internal messages: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>/messages", methods=["POST"])
@cross_origin()
def send_internal_message(conversation_id):
    """Send a message in an internal conversation"""
    try:
        data = request.get_json()
        sender_id = data.get('sender_id', 'current-user')  # TODO: Get from auth
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        metadata = data.get('metadata')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Save message
        metadata_json = json.dumps(metadata) if metadata else None
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO internal_messages 
            (conversation_id, sender_id, content, message_type, metadata, timestamp, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (conversation_id, sender_id, content, message_type, metadata_json, timestamp, timestamp, timestamp))
        
        message_id = cursor.lastrowid
        
        # Update conversation updated_at
        cursor.execute('''
            UPDATE internal_conversations
            SET updated_at = ?
            WHERE id = ?
        ''', (timestamp, conversation_id))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_message_new', {
                'conversation_id': conversation_id,
                'message': {
                    'id': message_id,
                    'sender_id': sender_id,
                    'content': content,
                    'message_type': message_type,
                    'metadata': metadata,
                    'timestamp': timestamp
                }
            })
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'message': 'Message sent successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error sending internal message: {e}")
        return jsonify({'error': str(e)}), 500

@internal_bp.route("/internal-conversations/<int:conversation_id>/upload-media", methods=["POST"])
@cross_origin()
def upload_internal_media(conversation_id):
    """Upload media for an internal conversation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        sender_id = request.form.get('sender_id', 'current-user')  # TODO: Get from auth
        message_type = request.form.get('type', 'image')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file size
        MAX_FILE_SIZES = {
            'image': 10 * 1024 * 1024,  # 10MB
            'document': 50 * 1024 * 1024,  # 50MB
            'audio': 20 * 1024 * 1024,  # 20MB
            'video': 50 * 1024 * 1024  # 50MB
        }
        
        max_size = MAX_FILE_SIZES.get(message_type, 10 * 1024 * 1024)
        if file.content_length and file.content_length > max_size:
            return jsonify({
                'error': f'File too large. Maximum size: {max_size / (1024 * 1024)}MB'
            }), 400
        
        # Read file content
        file_content = file.read()
        file.seek(0)
        
        # Generate secure filename
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f"internal/{conversation_id}/{timestamp}_{filename}"
        
        # Upload to Supabase Storage (if configured)
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "media")
        
        media_url = None
        if supabase_url and supabase_key:
            try:
                import requests
                upload_url = f"{supabase_url}/storage/v1/object/{supabase_bucket}/{file_path}"
                headers = {
                    'apikey': supabase_key,
                    'Authorization': f'Bearer {supabase_key}',
                    'Content-Type': file.content_type or 'application/octet-stream'
                }
                
                upload_response = requests.put(
                    upload_url,
                    data=file_content,
                    headers=headers,
                    timeout=30
                )
                
                if upload_response.status_code in [200, 201]:
                    public_url = f"{supabase_url}/storage/v1/object/public/{supabase_bucket}/{file_path}"
                    media_url = public_url
                    logger.info(f"✅ Arquivo enviado para Supabase: {file_path}")
            except Exception as e:
                logger.error(f"❌ Erro ao fazer upload para Supabase: {e}")
        
        # Save message with media URL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        content = f"📎 {filename}"
        if media_url:
            content += f" ({media_url})"
        
        metadata = {
            'media_url': media_url,
            'filename': filename,
            'file_path': file_path,
            'content_type': file.content_type
        }
        
        metadata_json = json.dumps(metadata)
        timestamp_iso = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO internal_messages 
            (conversation_id, sender_id, content, message_type, metadata, timestamp, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (conversation_id, sender_id, content, message_type, metadata_json, timestamp_iso, timestamp_iso, timestamp_iso))
        
        message_id = cursor.lastrowid
        
        # Update conversation updated_at
        cursor.execute('''
            UPDATE internal_conversations
            SET updated_at = ?
            WHERE id = ?
        ''', (timestamp_iso, conversation_id))
        
        conn.commit()
        conn.close()
        
        # Emit WebSocket event
        if socketio:
            socketio.emit('internal_message_new', {
                'conversation_id': conversation_id,
                'message': {
                    'id': message_id,
                    'sender_id': sender_id,
                    'content': content,
                    'message_type': message_type,
                    'metadata': metadata,
                    'timestamp': timestamp_iso
                }
            })
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'url': media_url,
            'file_path': file_path,
            'message': 'Media uploaded successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error uploading internal media: {e}")
        return jsonify({'error': str(e)}), 500
