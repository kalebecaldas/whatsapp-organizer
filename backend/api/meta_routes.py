from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

meta_bp = Blueprint("meta", __name__)

# Meta WhatsApp API Configuration
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
META_API_VERSION = os.getenv("META_API_VERSION", "v18.0")
META_API_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

def send_meta_message(phone_number: str, message_text: str) -> dict:
    """
    Send a text message via Meta WhatsApp API
    
    Args:
        phone_number: Recipient phone number (with country code, no +)
        message_text: Message content
    
    Returns:
        dict with success status and response data
    """
    if not META_ACCESS_TOKEN or not META_PHONE_NUMBER_ID:
        logger.warning("⚠️ Meta API credentials not configured")
        return {'success': False, 'error': 'Meta API not configured'}
    
    try:
        url = f"{META_API_BASE_URL}/{META_PHONE_NUMBER_ID}/messages"
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        payload = {
            'messaging_product': 'whatsapp',
            'to': phone_number,
            'type': 'text',
            'text': {
                'body': message_text
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ Mensagem enviada via Meta API para {phone_number}")
            return {'success': True, 'data': response.json()}
        else:
            logger.error(f"❌ Erro ao enviar via Meta API: {response.status_code} - {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem via Meta API: {e}")
        return {'success': False, 'error': str(e)}

def _handle_outgoing_media(phone_number: str, media_url: str, media_type: str, caption: str = None) -> dict:
    """
    Send media (image, video, audio, document) via Meta WhatsApp API
    
    Args:
        phone_number: Recipient phone number
        media_url: URL of the media file (must be publicly accessible)
        media_type: Type of media (image, video, audio, document)
        caption: Optional caption for the media
    
    Returns:
        dict with success status and response data
    """
    if not META_ACCESS_TOKEN or not META_PHONE_NUMBER_ID:
        logger.warning("⚠️ Meta API credentials not configured")
        return {'success': False, 'error': 'Meta API not configured'}
    
    try:
        url = f"{META_API_BASE_URL}/{META_PHONE_NUMBER_ID}/messages"
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Map media types to Meta API types
        type_mapping = {
            'image': 'image',
            'video': 'video',
            'audio': 'audio',
            'document': 'document'
        }
        
        meta_type = type_mapping.get(media_type, 'document')
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': phone_number,
            'type': meta_type,
            meta_type: {
                'link': media_url
            }
        }
        
        # Add caption if provided (only for image and video)
        if caption and meta_type in ['image', 'video']:
            payload[meta_type]['caption'] = caption
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ Mídia enviada via Meta API para {phone_number}")
            return {'success': True, 'data': response.json()}
        else:
            logger.error(f"❌ Erro ao enviar mídia via Meta API: {response.status_code} - {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mídia via Meta API: {e}")
        return {'success': False, 'error': str(e)}

@meta_bp.route('/send-message', methods=['POST'])
@cross_origin()
def send_message_endpoint():
    """Endpoint to send a message via Meta WhatsApp API"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({'error': 'Phone and message are required'}), 400
        
        result = send_meta_message(phone, message)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ Error in send message endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@meta_bp.route('/send-media', methods=['POST'])
@cross_origin()
def send_media_endpoint():
    """Endpoint to send media via Meta WhatsApp API"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        media_url = data.get('url') or data.get('media_url')
        media_type = data.get('type', 'image')
        caption = data.get('caption')
        
        if not phone or not media_url:
            return jsonify({'error': 'Phone and media URL are required'}), 400
        
        result = _handle_outgoing_media(phone, media_url, media_type, caption)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ Error in send media endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@meta_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check for Meta API configuration"""
    return jsonify({
        'status': 'ok',
        'meta_configured': bool(META_ACCESS_TOKEN and META_PHONE_NUMBER_ID),
        'api_version': META_API_VERSION
    }), 200
