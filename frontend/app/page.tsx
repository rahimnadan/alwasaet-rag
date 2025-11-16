'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, Loader2, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: string[]
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [groqApiKey, setGroqApiKey] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Get session ID from localStorage or create new one
    const storedSessionId = localStorage.getItem('sessionId')
    const storedApiKey = localStorage.getItem('groqApiKey')
    if (storedSessionId) {
      setSessionId(storedSessionId)
    }
    if (storedApiKey) {
      setGroqApiKey(storedApiKey)
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || !sessionId || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Connect to WebSocket
      const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`)
      wsRef.current = ws

      let assistantMessage = ''
      let citations: string[] = []

      ws.onopen = () => {
        ws.send(JSON.stringify({ query: input }))
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'chunk') {
          assistantMessage += data.content
          setMessages(prev => {
            const newMessages = [...prev]
            const lastMessage = newMessages[newMessages.length - 1]
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.content = assistantMessage
              return [...newMessages]
            } else {
              return [...newMessages, { role: 'assistant', content: assistantMessage }]
            }
          })
        } else if (data.type === 'done') {
          citations = data.citations || []
          setMessages(prev => {
            const newMessages = [...prev]
            const lastMessage = newMessages[newMessages.length - 1]
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.citations = citations
            }
            return [...newMessages]
          })
          setLoading(false)
          ws.close()
        } else if (data.type === 'error') {
          console.error('WebSocket error:', data.message)
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: `Error: ${data.message}` 
          }])
          setLoading(false)
          ws.close()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'Connection error. Please try again.' 
        }])
        setLoading(false)
      }

      ws.onclose = () => {
        wsRef.current = null
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'An error occurred. Please try again.' 
      }])
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-900">Alwasaet RAG</h1>
          <a 
            href="/admin" 
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Admin Dashboard
          </a>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-16">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Welcome to Alwasaet RAG
              </h2>
              <p className="text-gray-600 max-w-md">
                Ask questions about your documents and get instant answers with citations.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={cn(
                    'flex gap-4',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-white text-sm font-medium">AI</span>
                    </div>
                  )}
                  <div
                    className={cn(
                      'max-w-[85%] rounded-2xl px-4 py-3',
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    )}
                  >
                    <div className="whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                    {message.citations && message.citations.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-300">
                        <p className="text-xs text-gray-600 font-medium">Sources:</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {message.citations.map((citation, i) => (
                            <span
                              key={i}
                              className="text-xs bg-white px-2 py-1 rounded border border-gray-300"
                            >
                              {citation}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-white text-sm font-medium">You</span>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-4 justify-start">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-white text-sm font-medium">AI</span>
                  </div>
                  <div className="bg-gray-100 text-gray-900 rounded-2xl px-4 py-3">
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              placeholder="Ask a question about your documents..."
              className="w-full pl-4 pr-12 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 placeholder-gray-500"
              disabled={loading || !sessionId}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim() || !sessionId}
              className={cn(
                'absolute right-2 p-2 rounded-lg transition-colors',
                loading || !input.trim() || !sessionId
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              )}
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          {!sessionId && (
            <p className="text-sm text-red-600 mt-2">
              Please upload documents in the Admin Dashboard first
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
