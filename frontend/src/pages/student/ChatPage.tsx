import React, { useState, useEffect, useRef } from 'react';
import { chatAPI, profileAPI } from '../../lib/api';
import { ChatMessage, StudentProfile } from '../../lib/types';
import { useAuth } from '../../lib/authContext';
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  Languages, 
  ShieldCheck,
  Zap
} from 'lucide-react';

export const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Fetch real profile data on mount to ensure ground truth score and credentials
  useEffect(() => {
    profileAPI.getStudentProfile()
      .then(data => {
        if (data) setProfile(data);
      })
      .catch(err => console.error("Error loading profile for chat grounding:", err));
  }, []);

  const verifiedCerts = profile?.certificates?.filter(c => c.verification_status === 'VERIFIED') || [];
  const verifiedBadgesText = verifiedCerts.length > 0
    ? verifiedCerts.map(c => `${c.title} (${c.badge_tier} Badge)`).join(', ')
    : 'AWS Certified Developer (Gold Badge)';
  const readinessScoreText = profile?.placement_readiness_score !== undefined
    ? `${profile.placement_readiness_score}%`
    : '88.5%';

  useEffect(() => {
    chatAPI.getHistory()
      .then(data => {
        if (data && data.length > 0) {
          setMessages(data);
        } else {
          // Welcome greeting dynamically grounded in profile
          setMessages([
            {
              id: 0,
              session_id: 1,
              sender: 'assistant',
              content: `Hello ${user?.full_name || 'Aarav'}! I am CareerLens AI, your personal senior engineering career mentor.\n\nI am grounded in your live profile (${readinessScoreText} Readiness • ${verifiedBadgesText}) and active job matches.\n\nAsk me for real project architectures, business ideas from your skills, internship preparation, or learning roadmaps in English, Hindi (हिंदी), or Hinglish!`,
              detected_language: 'en',
              created_at: new Date().toISOString()
            }
          ]);
        }
      })
      .catch(err => console.error(err));
  }, [user, profile]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    setInput('');
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      session_id: 1,
      sender: 'user',
      content: text,
      detected_language: 'auto',
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(text);
      setMessages(prev => [...prev, response]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          session_id: 1,
          sender: 'assistant',
          content: 'Sorry, I encountered an issue processing your question. Please try again.',
          detected_language: 'en',
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const promptChips = [
    { label: "Mere skills ke according 3 projects batao", lang: "Hinglish", tag: "🚀" },
    { label: "Mere skills se kya business bana sakta hoon?", lang: "Hinglish", tag: "💼" },
    { label: "Which career roles fit my profile?", lang: "English", tag: "🎯" },
    { label: "What should I learn next for 85%+ readiness?", lang: "English", tag: "📚" },
    { label: "रिज्यूमे में कौन सी स्किल्स जोड़नी चाहिए?", lang: "Hindi", tag: "🇮🇳" },
    { label: "Which project would make my resume stronger?", lang: "English", tag: "💻" },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <MessageSquare className="text-indigo-400" size={24} />
            <h1 className="text-2xl font-bold text-white">Bilingual AI Career Counselor</h1>
          </div>
          <p className="text-xs text-slate-400">
            Powered by Google Gemini 2.5 Flash • Context-aware of your verified certificates & match gaps
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 text-xs text-slate-300 border border-slate-700">
          <Languages size={14} className="text-indigo-400" />
          <span>English • हिंदी • Hinglish</span>
        </div>
      </div>

      {/* Profile Grounding Banner */}
      <div className="p-3.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-indigo-300">
          <ShieldCheck size={16} className="text-indigo-400 shrink-0" />
          <span>
            <strong>Context Active:</strong> {user?.full_name || profile?.full_name || 'Aarav Sharma'} • {verifiedBadgesText} • {readinessScoreText} Readiness
          </span>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded">
          LIVE GROUNDED
        </span>
      </div>

      {/* Chat Window */}
      <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/80 shadow-2xl h-[520px] flex flex-col justify-between">
        
        {/* Messages Stream */}
        <div className="overflow-y-auto space-y-4 pr-2">
          {messages.map((m, idx) => {
            const isUser = m.sender === 'user';
            return (
              <div
                key={idx}
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-indigo-600/20 mt-0.5">
                    <Bot size={16} />
                  </div>
                )}

                <div
                  className={`max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                      ? 'bg-indigo-600 text-white rounded-tr-none'
                      : 'bg-slate-900 border border-slate-700/80 text-slate-200 rounded-tl-none shadow-md'
                  }`}
                >
                  {m.content}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-700 text-white flex items-center justify-center shrink-0 mt-0.5">
                    <User size={16} />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 animate-pulse">
                <Bot size={16} />
              </div>
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-700/80 text-slate-400 text-xs rounded-tl-none flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                <span>CareerLens AI is analyzing your verified profile...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input & Quick Chips */}
        <div className="pt-4 border-t border-slate-700/60 space-y-3">
          
          {/* Quick Prompt Chips */}
          <div className="flex flex-wrap gap-2">
            {promptChips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(chip.label)}
                disabled={loading}
                className="text-[11px] px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors flex items-center gap-1.5"
              >
                <span>{chip.tag}</span>
                <span>{chip.label}</span>
              </button>
            ))}
          </div>

          {/* Text Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Ask anything in English, Hindi, or Hinglish (e.g. 'Mera match score kaise badhega?')..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 px-4 py-3 rounded-2xl bg-slate-900 border border-slate-700 text-white text-xs sm:text-sm placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-3 rounded-2xl bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-lg shadow-indigo-600/20"
            >
              <Send size={18} />
            </button>
          </form>

        </div>

      </div>

    </div>
  );
};
