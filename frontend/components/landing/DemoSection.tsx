import React, { useState, useEffect } from 'react';
import { MessageSquare, BarChart3, ShieldCheck, Zap, Smile, Meh, Frown } from 'lucide-react';
import Button from '../ui/button';

const DemoSection: React.FC = () => {
  const [activeMessage, setActiveMessage] = useState(0);

  // Simple auto-scrolling transcript effect
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveMessage((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const transcript = [
    { speaker: "Customer", text: "I'm having trouble with the billing setup, can you help?", sentiment: "neutral" },
    { speaker: "Agent", text: "Of course! Let me pull up your account details. One moment please.", sentiment: "positive" },
    { speaker: "Customer", text: "Thank you, I appreciate the quick response. It's been frustrating.", sentiment: "neutral" },
    { speaker: "Agent", text: "I understand. I've located the issue and fixed the configuration error.", sentiment: "positive" },
  ];

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <Smile size={14} className="text-emerald-500" />;
      case 'neutral': return <Meh size={14} className="text-slate-400" />;
      case 'negative': return <Frown size={14} className="text-rose-500" />;
      default: return null;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-emerald-50 text-emerald-700 border-emerald-100';
      case 'neutral': return 'bg-slate-50 text-slate-600 border-slate-200';
      case 'negative': return 'bg-rose-50 text-rose-700 border-rose-100';
      default: return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  return (
    <section id="demo" className="py-12 bg-slate-50/50">
      <div className="max-w-[1100px] mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-8 items-center">
          {/* Left Content */}
          <div className="order-2 lg:order-1">
            <h2 className="text-3xl font-display font-semibold text-slate-900 mb-5 leading-tight">
              Turn every conversation into <br />
              <span className="text-primary-600">actionable intelligence.</span>
            </h2>
            <p className="text-base text-slate-500 mb-6 leading-relaxed">
              Stop guessing what happens on your calls. Our AI analyzes 100% of your voice data in real-time to provide insights that drive revenue and customer loyalty.
            </p>

            <ul className="space-y-3 mb-8">
              {[
                { icon: <Zap className="text-primary-600" size={18} />, text: "Instant transcription with 99.9% accuracy" },
                { icon: <BarChart3 className="text-primary-600" size={18} />, text: "Automated sentiment and intent detection" },
                { icon: <ShieldCheck className="text-primary-600" size={18} />, text: "Built-in compliance and security monitoring" },
              ].map((feature, i) => (
                <li key={i} className="flex items-center gap-3 text-slate-600 text-[15px]">
                  <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-primary-50 flex items-center justify-center">
                    {feature.icon}
                  </div>
                  <span>{feature.text}</span>
                </li>
              ))}
            </ul>

            <Button variant="outline" size="md" className="gap-2 group text-sm border-slate-200">
              Explore All Features
              <MessageSquare size={16} className="text-slate-400 group-hover:text-primary-600 transition-colors" />
            </Button>
          </div>

          {/* Right Demo Card */}
          <div className="order-1 lg:order-2">
            <div className="relative">
              {/* Glassmorphism Background Decor */}
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-purple-100/40 rounded-full blur-3xl -z-10" />
              <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-primary-100/40 rounded-full blur-3xl -z-10" />

              <div className="bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden backdrop-blur-sm bg-white/90">
                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Live Analysis</span>
                  </div>
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />
                    <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />
                    <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />
                  </div>
                </div>

                {/* Waveform */}
                <div className="px-6 py-8 bg-slate-900 flex items-center justify-center gap-1 overflow-hidden h-24">
                  {[...Array(32)].map((_, i) => (
                    <div
                      key={i}
                      className="w-1.5 bg-gradient-to-t from-primary-500 to-purple-400 rounded-full transition-all duration-300 ease-in-out"
                      style={{
                        height: `${20 + Math.random() * 60}%`,
                        opacity: 0.6 + (Math.random() * 0.4),
                        animation: `wave 1.5s ease-in-out infinite ${i * 0.05}s`
                      }}
                    />
                  ))}
                  <style>{`
                    @keyframes wave {
                      0%, 100% { transform: scaleY(1); }
                      50% { transform: scaleY(1.5); }
                    }
                  `}</style>
                </div>

                {/* Transcript UI */}
                <div className="p-6 space-y-4 max-h-[300px] overflow-hidden">
                  {transcript.map((msg, i) => (
                    <div 
                      key={i}
                      className={`flex flex-col gap-1.5 transition-all duration-500 ${
                        i === activeMessage ? 'opacity-100 translate-x-0' : 'opacity-40 -translate-x-1'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`text-[10px] font-bold uppercase tracking-widest ${
                          msg.speaker === 'Agent' ? 'text-primary-600' : 'text-slate-400'
                        }`}>
                          {msg.speaker}
                        </span>
                        <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded border text-[9px] font-bold uppercase ${getSentimentColor(msg.sentiment)}`}>
                          {getSentimentIcon(msg.sentiment)}
                          {msg.sentiment}
                        </div>
                      </div>
                      <div className={`px-4 py-2.5 rounded-xl text-sm leading-relaxed ${
                        msg.speaker === 'Agent' 
                          ? 'bg-primary-50 text-slate-800 rounded-tl-none border border-primary-100' 
                          : 'bg-slate-100 text-slate-700 rounded-tr-none border border-slate-200'
                      }`}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Footer Insight */}
                <div className="px-6 py-4 bg-primary-600 text-white flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Zap size={16} className="text-primary-200" />
                    <span className="text-xs font-medium">Insight: Successful Resolution</span>
                  </div>
                  <span className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full">Score: 94/100</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DemoSection;
