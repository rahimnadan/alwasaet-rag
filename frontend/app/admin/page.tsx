'use client'

import { useState, useEffect, useRef } from 'react'
import { Upload, FileText, Check, Loader2, MessageSquare, Key, Trash2, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DocumentInfo {
  filename: string
  processed: boolean
}

export default function AdminDashboard() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [groqApiKey, setGroqApiKey] = useState('')
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Get or create session
    const storedSessionId = localStorage.getItem('sessionId')
    const storedApiKey = localStorage.getItem('groqApiKey')
    
    if (storedSessionId) {
      setSessionId(storedSessionId)
      loadSessionInfo(storedSessionId)
    }
    
    if (storedApiKey) {
      setGroqApiKey(storedApiKey)
    }
  }, [])

  const loadSessionInfo = async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/session/${sessionId}`)
      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents)
      }
    } catch (error) {
      console.error('Error loading session info:', error)
    }
  }

  const initSession = async () => {
    if (!groqApiKey) {
      alert('Please enter your Groq API key')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/init-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ groq_api_key: groqApiKey })
      })

      if (response.ok) {
        const data = await response.json()
        setSessionId(data.session_id)
        localStorage.setItem('sessionId', data.session_id)
        localStorage.setItem('groqApiKey', groqApiKey)
      } else {
        alert('Failed to initialize session')
      }
    } catch (error) {
      console.error('Error initializing session:', error)
      alert('Failed to initialize session')
    }
  }

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0 || !sessionId || !groqApiKey) return

    setUploading(true)
    setUploadProgress('Uploading files...')

    try {
      const formData = new FormData()
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i])
      }

      const response = await fetch(
        `http://localhost:8000/api/upload?session_id=${sessionId}&groq_api_key=${groqApiKey}`,
        {
          method: 'POST',
          body: formData
        }
      )

      if (response.ok) {
        const data = await response.json()
        setUploadProgress(`Successfully processed ${data.processed_count} document(s)`)
        await loadSessionInfo(sessionId)
        setTimeout(() => setUploadProgress(''), 3000)
      } else {
        const error = await response.json()
        alert(`Upload failed: ${error.detail}`)
        setUploadProgress('')
      }
    } catch (error) {
      console.error('Error uploading files:', error)
      alert('Upload failed')
      setUploadProgress('')
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleClearSession = () => {
    if (confirm('Are you sure you want to clear the session? This will remove all uploaded documents.')) {
      localStorage.removeItem('sessionId')
      localStorage.removeItem('groqApiKey')
      setSessionId(null)
      setDocuments([])
      setGroqApiKey('')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Admin Dashboard
              </h1>
              <p className="text-gray-600 mt-1">Manage your documents and RAG system</p>
            </div>
            <a
              href="/"
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
            >
              <MessageSquare className="w-5 h-5" />
              Go to Chat
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* API Key Section */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-600 rounded-xl flex items-center justify-center">
                  <Key className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">API Configuration</h2>
                  <p className="text-sm text-gray-600">Enter your Groq API key to get started</p>
                </div>
              </div>
              
              <div className="flex gap-3">
                <div className="flex-1">
                  <input
                    type="password"
                    value={groqApiKey}
                    onChange={(e) => setGroqApiKey(e.target.value)}
                    placeholder="Enter your Groq API key..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={!!sessionId}
                  />
                </div>
                {!sessionId ? (
                  <button
                    onClick={initSession}
                    disabled={!groqApiKey}
                    className={cn(
                      'px-8 py-3 rounded-xl font-semibold transition-all',
                      groqApiKey
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    )}
                  >
                    Initialize
                  </button>
                ) : (
                  <button
                    onClick={handleClearSession}
                    className="px-8 py-3 bg-red-100 text-red-600 rounded-xl font-semibold hover:bg-red-200 transition-all"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                )}
              </div>
              
              {sessionId && (
                <div className="mt-4 px-4 py-3 bg-green-50 border border-green-200 rounded-xl">
                  <p className="text-sm text-green-800">
                    ✓ Session active: <span className="font-mono font-semibold">{sessionId}</span>
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Upload Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center">
                  <Upload className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Document Upload</h2>
                  <p className="text-sm text-gray-600">Upload PDF documents to index</p>
                </div>
              </div>

              <div
                className={cn(
                  'border-2 border-dashed rounded-2xl p-12 text-center transition-all',
                  !sessionId || uploading
                    ? 'border-gray-200 bg-gray-50'
                    : 'border-blue-300 bg-blue-50 hover:bg-blue-100 cursor-pointer'
                )}
                onClick={() => {
                  if (sessionId && !uploading) {
                    fileInputRef.current?.click()
                  }
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                  disabled={!sessionId || uploading}
                />
                
                {uploading ? (
                  <div className="flex flex-col items-center gap-3">
                    <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                    <p className="text-gray-700 font-medium">{uploadProgress}</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                      <Upload className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-gray-900 mb-1">
                        {sessionId ? 'Drop files here or click to browse' : 'Initialize session first'}
                      </p>
                      <p className="text-sm text-gray-600">
                        Supports PDF files
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {uploadProgress && !uploading && (
                <div className="mt-4 px-4 py-3 bg-green-50 border border-green-200 rounded-xl">
                  <p className="text-sm text-green-800">✓ {uploadProgress}</p>
                </div>
              )}
            </div>
          </div>

          {/* Documents List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Documents</h2>
                  <p className="text-sm text-gray-600">{documents.length} uploaded</p>
                </div>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {documents.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p className="text-sm">No documents uploaded yet</p>
                  </div>
                ) : (
                  documents.map((doc, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-200 hover:border-blue-300 transition-all"
                    >
                      <div className={cn(
                        'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                        doc.processed
                          ? 'bg-green-100 text-green-600'
                          : 'bg-yellow-100 text-yellow-600'
                      )}>
                        {doc.processed ? (
                          <Check className="w-5 h-5" />
                        ) : (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {doc.filename}
                        </p>
                        <p className="text-xs text-gray-600">
                          {doc.processed ? 'Ready' : 'Processing...'}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium mb-1">Total Documents</p>
                  <p className="text-4xl font-bold">{documents.length}</p>
                </div>
                <FileText className="w-12 h-12 text-blue-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium mb-1">Processed</p>
                  <p className="text-4xl font-bold">
                    {documents.filter(d => d.processed).length}
                  </p>
                </div>
                <Check className="w-12 h-12 text-green-200" />
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm font-medium mb-1">Status</p>
                  <p className="text-2xl font-bold">
                    {sessionId ? 'Active' : 'Inactive'}
                  </p>
                </div>
                <MessageSquare className="w-12 h-12 text-purple-200" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
