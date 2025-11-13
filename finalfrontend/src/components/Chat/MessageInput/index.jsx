import { useState, useRef, useEffect } from 'react';
import { Send, Smile, Paperclip, Mic, Users, X, RotateCcw, Upload, File, Image, FileText, Music, Video } from 'lucide-react';
import { useChat } from '../../../context/ChatContext';
import { uploadMedia } from '../../../utils/api';
import './MessageInput.css';

const MessageInput = () => {
  const { selectedConversation, sendMessage } = useChat();
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && selectedConversation) {
      sendMessage(message.trim());
      setMessage('');
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e) => {
    setMessage(e.target.value);
    setIsTyping(e.target.value.length > 0);
  };

  // File type validation
  const ALLOWED_TYPES = {
    image: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
    document: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
               'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
    audio: ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/aac'],
    video: ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo']
  };

  const MAX_FILE_SIZES = {
    image: 10 * 1024 * 1024, // 10MB
    document: 50 * 1024 * 1024, // 50MB
    audio: 20 * 1024 * 1024, // 20MB
    video: 50 * 1024 * 1024 // 50MB
  };

  const getFileType = (file) => {
    if (ALLOWED_TYPES.image.includes(file.type)) return 'image';
    if (ALLOWED_TYPES.document.includes(file.type)) return 'document';
    if (ALLOWED_TYPES.audio.includes(file.type)) return 'audio';
    if (ALLOWED_TYPES.video.includes(file.type)) return 'video';
    return 'unknown';
  };

  const validateFile = (file) => {
    const fileType = getFileType(file);
    if (fileType === 'unknown') {
      return { valid: false, error: 'Tipo de arquivo não suportado' };
    }

    const maxSize = MAX_FILE_SIZES[fileType];
    if (file.size > maxSize) {
      const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(0);
      return { valid: false, error: `Arquivo muito grande. Tamanho máximo: ${maxSizeMB}MB` };
    }

    return { valid: true, type: fileType };
  };

  const handleFileSelect = (files) => {
    const fileArray = Array.from(files);
    const validFiles = [];

    fileArray.forEach(file => {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push({
          file,
          type: validation.type,
          preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
        });
      } else {
        alert(`${file.name}: ${validation.error}`);
      }
    });

    if (validFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...validFiles]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files);
    }
    // Reset input to allow selecting the same file again
    e.target.value = '';
  };

  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => {
      const newFiles = [...prev];
      if (newFiles[index].preview) {
        URL.revokeObjectURL(newFiles[index].preview);
      }
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const handleUpload = async (fileData, index) => {
    if (!selectedConversation) return;

    try {
      setUploadProgress(prev => ({ ...prev, [index]: 0 }));

      const response = await uploadMedia(
        selectedConversation.phone,
        fileData.file,
        fileData.type,
        (progress) => {
          setUploadProgress(prev => ({ ...prev, [index]: progress }));
        }
      );

      if (response.success) {
        // Remove file from selected files
        removeFile(index);
        // Optionally send a message indicating media was sent
        if (response.message) {
          sendMessage(response.message);
        }
      } else {
        alert(`Erro ao enviar ${fileData.file.name}: ${response.error || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro no upload:', error);
      alert(`Erro ao enviar ${fileData.file.name}`);
    } finally {
      setUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[index];
        return newProgress;
      });
    }
  };

  const handleSendFiles = () => {
    selectedFiles.forEach((fileData, index) => {
      handleUpload(fileData, index);
    });
  };

  // Drag and drop handlers
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'image': return <Image size={16} />;
      case 'document': return <FileText size={16} />;
      case 'audio': return <Music size={16} />;
      case 'video': return <Video size={16} />;
      default: return <File size={16} />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleConversationAction = async (action) => {
    if (!selectedConversation) return;

    try {
      const response = await fetch('/api/conversation-actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversationId: selectedConversation.id,
          action: action,
          targetUserId: action === 'transfer' ? 'target-user-id' : null
        })
      });

      if (response.ok) {
        console.log(`Ação ${action} executada com sucesso`);
        setShowActionMenu(false);
      } else {
        console.error(`Erro ao executar ação ${action}`);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Cleanup preview URLs on unmount
  useEffect(() => {
    return () => {
      selectedFiles.forEach(fileData => {
        if (fileData.preview) {
          URL.revokeObjectURL(fileData.preview);
        }
      });
    };
  }, []);

  if (!selectedConversation) {
    return null;
  }

  // Verificar se a conversa foi atribuída a um usuário
  // const isAssignedConversation = selectedConversation.atribuido_para;

  return (
    <div 
      className={`message-input-container ${isDragging ? 'dragging' : ''}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* File Preview Section */}
      {selectedFiles.length > 0 && (
        <div className="file-preview-section">
          {selectedFiles.map((fileData, index) => (
            <div key={index} className="file-preview-item">
              {fileData.preview ? (
                <img src={fileData.preview} alt="Preview" className="file-preview-image" />
              ) : (
                <div className="file-preview-icon">
                  {getFileIcon(fileData.type)}
                </div>
              )}
              <div className="file-preview-info">
                <span className="file-preview-name">{fileData.file.name}</span>
                <span className="file-preview-size">{formatFileSize(fileData.file.size)}</span>
                {uploadProgress[index] !== undefined && (
                  <div className="upload-progress">
                    <div 
                      className="upload-progress-bar" 
                      style={{ width: `${uploadProgress[index]}%` }}
                    />
                    <span className="upload-progress-text">{uploadProgress[index]}%</span>
                  </div>
                )}
              </div>
              <button
                type="button"
                className="file-preview-remove"
                onClick={() => removeFile(index)}
                disabled={uploadProgress[index] !== undefined}
              >
                <X size={16} />
              </button>
            </div>
          ))}
          {selectedFiles.length > 0 && Object.keys(uploadProgress).length === 0 && (
            <button
              type="button"
              className="send-files-button"
              onClick={handleSendFiles}
            >
              <Upload size={16} />
              Enviar {selectedFiles.length} arquivo{selectedFiles.length > 1 ? 's' : ''}
            </button>
          )}
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx,audio/*,video/*"
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
      />

      <form onSubmit={handleSubmit} className="message-input-form">
        <div className="input-wrapper">
          <button type="button" className="icon-button">
            <Smile size={20} />
          </button>
          <button 
            type="button" 
            className="icon-button"
            onClick={handleAttachmentClick}
            title="Anexar arquivo"
          >
            <Paperclip size={20} />
          </button>
          <div className="text-input-container">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Digite uma mensagem ou arraste arquivos aqui"
              className="message-textarea"
              rows={1}
              maxLength={4096}
            />
          </div>
          {isTyping ? (
            <button type="submit" className="send-button">
              <Send size={20} />
            </button>
          ) : (
            <button type="button" className="icon-button">
              <Mic size={20} />
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default MessageInput; 