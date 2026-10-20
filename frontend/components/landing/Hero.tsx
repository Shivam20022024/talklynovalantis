import React from 'react';
import { ArrowRight, Play, CheckCircle2 } from 'lucide-react';
import Button from '../ui/button';
interface HeroProps {
  onNavigate?: (view: any) => void;
}

const Hero: React.FC<HeroProps> = ({ onNavigate }) => {
  return (
    <section className="relative overflow-hidden py-14">
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[20%] w-[500px] h-[500px] bg-primary-100/30 rounded-full blur-[100px]" />
        <div className="absolute top-[10%] right-[10%] w-[400px] h-[400px] bg-purple-100/20 rounded-full blur-[80px]" />
      </div>

      <div className="max-w-[1100px] mx-auto px-6 text-center">

        <h1 
          className="text-5xl md:text-6xl font-display font-bold text-slate-900 tracking-tight mb-6 animate-slide-up leading-[1.1]"
          style={{ animationDelay: '0.1s' }}
        >
          Understand every voice <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">
            in your business.
          </span>
        </h1>

        <p 
          className="text-lg md:text-xl text-slate-500 max-w-2xl mx-auto mb-8 animate-slide-up leading-relaxed font-normal"
          style={{ animationDelay: '0.2s' }}
        >
          Transform customer conversations into actionable growth. <br className="hidden md:block" />
          The all-in-one AI platform for speech analytics and performance.
        </p>

        <div 
          className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-slide-up"
          style={{ animationDelay: '0.3s' }}
        >
          <Button 
            size="lg" 
            className="w-full sm:w-auto gap-2 group bg-primary-600 hover:bg-primary-700 shadow-md shadow-primary-500/20"
            onClick={() => onNavigate && onNavigate('ANALYTICS')}
          >
            Try for free
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </Button>

          <Button 
            variant="outline" 
            size="lg" 
            className="w-full sm:w-auto gap-2 border-slate-200"
            onClick={() => {
              const demoSec = document.getElementById('demo');
              demoSec?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            <Play size={18} className="fill-slate-600 text-slate-600" />
            Watch Demo
          </Button>
        </div>

        {/* Compact Social Proof / Trust Badges */}
        <div 
          className="mt-8 pt-6 border-t border-slate-100 flex flex-wrap justify-center gap-x-12 gap-y-4 text-[13px] text-slate-400 animate-fade-in"
          style={{ animationDelay: '0.5s' }}
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-primary-500/70" />
            <span>99.9% Transcription Accuracy</span>
          </div>

          <div className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-primary-500/70" />
            <span>Real-time Insights</span>
          </div>

          <div className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-primary-500/70" />
            <span>Enterprise Grade Security</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
