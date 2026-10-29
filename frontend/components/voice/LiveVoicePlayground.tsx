'use client'

import React, { useState, useEffect } from 'react'
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  useConnectionState,
  BarVisualizer
} from '@livekit/components-react'
import '@livekit/components-styles'
import { ConnectionState } from 'livekit-client'
import { Mic, MicOff, PhoneOff, Sparkles, Loader2, Volume2, AlertCircle } from 'lucide-react'
import { fetchApi } from '@/lib/api'

interface LiveVoicePlaygroundProps {
  isOpen: boolean
  onClose: () => void
  promptText: string
  welcomeMessage: string
  industry: string
}

function ActiveVoiceRoom({ onClose }: { onClose: () => void }) {
  const connectionState = useConnectionState()
  const { state, audioTrack } = useVoiceAssistant()
  const [isMuted, setIsMuted] = useState(false)

  const toggleMute = () => {
    setIsMuted(!isMuted)
  }

  const getStatusLabel = () => {
    switch (state) {
      case 'speaking':
        return 'AI is Speaking...'
      case 'listening':
        return 'Listening to you...'
      case 'thinking':
        return 'Thinking...'
      default:
        return connectionState === ConnectionState.Connected ? 'Connected (LiveKit WebRTC)' : 'Connecting...'
    }
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 text-center">
      {/* Animated Glowing Orb / Visualizer */}
      <div className="relative flex items-center justify-center mb-6">
        <div
          className={`absolute w-36 h-36 rounded-full blur-xl transition-all duration-300 ${
            state === 'speaking'
              ? 'bg-emerald-500/40 animate-pulse scale-110'
              : state === 'listening'
              ? 'bg-primary/40 animate-pulse scale-105'
              : 'bg-muted/40'
          }`}
        />
        <div className="relative flex items-center justify-center w-28 h-28 rounded-full bg-card border-2 border-border shadow-xl">
          {audioTrack ? (
            <div className="w-20 h-14 flex items-center justify-center">
              <BarVisualizer
                state={state}
                barCount={7}
                trackRef={audioTrack}
                className="w-full h-full text-primary"
              />
            </div>
          ) : (
            <Volume2 className={`w-10 h-10 ${state === 'speaking' ? 'text-emerald-500 animate-bounce' : 'text-primary'}`} />
          )}
        </div>
      </div>

      {/* Connection / Activity State Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-muted border border-border text-xs font-semibold mb-2">
        <span
          className={`w-2 h-2 rounded-full ${
            connectionState === ConnectionState.Connected
              ? state === 'speaking'
                ? 'bg-emerald-500 animate-pulse'
                : 'bg-primary animate-pulse'
              : 'bg-amber-500'
          }`}
        />
        <span>{getStatusLabel()}</span>
      </div>

      <div className="text-[11px] text-muted-foreground mb-6 font-mono">
        Sub-300ms WebRTC Engine • Instant Barge-in Active
      </div>

      {/* Control Buttons */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={toggleMute}
          className={`flex items-center justify-center w-12 h-12 rounded-full border transition-all ${
            isMuted
              ? 'bg-destructive/10 border-destructive text-destructive'
              : 'bg-muted border-border text-foreground hover:bg-muted/80'
          }`}
          title={isMuted ? 'Unmute Microphone' : 'Mute Microphone'}
        >
          {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
        </button>

        <button
          type="button"
          onClick={onClose}
          className="flex items-center gap-2 px-5 py-3 rounded-full bg-destructive text-destructive-foreground font-bold text-xs shadow-lg hover:opacity-90 transition-all cursor-pointer"
        >
          <PhoneOff size={16} />
          End Voice Test
        </button>
      </div>

      {/* LiveKit Audio Renderer for speaker output */}
      <RoomAudioRenderer />
    </div>
  )
}

export default function LiveVoicePlayground({
  isOpen,
  onClose,
  promptText,
  welcomeMessage,
  industry
}: LiveVoicePlaygroundProps) {
  const [token, setToken] = useState<string | null>(null)
  const [livekitUrl, setLivekitUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      startSession()
    } else {
      setToken(null)
      setError(null)
    }
  }, [isOpen])

  const startSession = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchApi('/api/v1/livekit/token', {
        method: 'POST',
        body: JSON.stringify({
          prompt: promptText,
          welcome_message: welcomeMessage,
          industry: industry
        })
      })

      if (res?.token && res?.livekit_url) {
        setToken(res.token)
        setLivekitUrl(res.livekit_url)
      } else {
        throw new Error(res?.detail || 'Failed to initialize LiveKit room')
      }
    } catch (err: any) {
      setError(err.message || 'Could not connect to LiveKit. Please check your credentials in Settings.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl relative">
        <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Sparkles size={16} />
            </span>
            <div>
              <h3 className="text-sm font-bold text-foreground">In-Browser Voice Playground</h3>
              <p className="text-[11px] text-muted-foreground font-mono">LiveKit WebRTC Agent</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground text-xs font-semibold px-2 py-1 rounded"
          >
            ✕
          </button>
        </div>

        {loading && (
          <div className="py-12 flex flex-col items-center justify-center text-center">
            <Loader2 className="w-8 h-8 text-primary animate-spin mb-3" />
            <p className="text-xs font-semibold text-foreground">Spawning LiveKit Real-time Voice Room...</p>
            <p className="text-[11px] text-muted-foreground mt-1">Preparing WebRTC audio and Silero VAD</p>
          </div>
        )}

        {error && (
          <div className="py-6 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-full bg-destructive/10 text-destructive flex items-center justify-center mb-3">
              <AlertCircle size={24} />
            </div>
            <h4 className="text-xs font-bold text-foreground mb-1">LiveKit Setup Required</h4>
            <p className="text-xs text-muted-foreground max-w-xs mb-4">{error}</p>
            <div className="flex gap-2">
              <a
                href="/settings"
                className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-xs font-bold shadow hover:opacity-90"
              >
                Configure LiveKit in Settings
              </a>
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-lg border border-border text-xs font-semibold text-muted-foreground hover:bg-muted"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {!loading && !error && token && livekitUrl && (
          <LiveKitRoom
            token={token}
            serverUrl={livekitUrl}
            connect={true}
            audio={true}
            video={false}
            onDisconnected={onClose}
            onError={(e) => setError(e.message)}
          >
            <ActiveVoiceRoom onClose={onClose} />
          </LiveKitRoom>
        )}
      </div>
    </div>
  )
}
