'use client';

import React from 'react';
import { motion, Variants } from 'framer-motion';
import { PhoneIncoming, Sparkles, Layers, Target, LayoutDashboard } from 'lucide-react';
import { SectionBadge } from './SectionBadge';

const WaveformVisual = () => (
  <div className="flex items-end justify-center gap-[3px] h-16">
    {[...Array(12)].map((_, i) => (
      <motion.div
        key={i}
        className="w-1 rounded-full bg-gradient-to-t from-brand-muted to-brand-primary"
        animate={{ height: [6, 20 + Math.random() * 28, 10, 30 + Math.random() * 20, 6] }}
        transition={{ duration: 1.4 + Math.random() * 0.6, repeat: Infinity, delay: i * 0.08, ease: 'easeInOut' }}
      />
    ))}
  </div>
);

const QuoteVisual = () => (
  <div className="relative">
    <div className="absolute -top-2 -left-1 text-theme-300 dark:text-brand-primary/20 text-3xl font-serif">"</div>
    <motion.p
      initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
      transition={{ duration: 1, delay: 0.3 }}
      className="text-sm italic text-gray-500 leading-relaxed pl-4"
    >
      I&apos;m inquiring about your premium program details and would like to confirm my consultation schedule for this Friday...
    </motion.p>
  </div>
);

const TagsVisual = () => {
  const tags = ['High Intent', 'Verified Prospect', 'Urgent Timeline', 'Qualified Lead', 'Follow-up Set'];
  return (
    <div className="flex flex-wrap gap-1.5">
      {tags.map((tag, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, scale: 0.8, y: 10 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.15 * i, ease: 'easeOut' }}
          className="px-2.5 py-1 rounded-md text-[10px] font-semibold tracking-wide uppercase bg-theme-100 dark:bg-brand-primary/[0.08] border border-theme-200 dark:border-brand-primary/15 text-theme-600 dark:text-brand-primary/70"
        >
          {tag}
        </motion.span>
      ))}
    </div>
  );
};

const ScoreVisual = () => (
  <div className="flex items-center gap-4">
    <div className="relative w-16 h-16">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(59,130,246,0.08)" strokeWidth="4" />
        <motion.circle
          cx="32" cy="32" r="28" fill="none" stroke="url(#scoreGrad)" strokeWidth="4"
          strokeLinecap="round" strokeDasharray={175.9}
          initial={{ strokeDashoffset: 175.9 }}
          whileInView={{ strokeDashoffset: 175.9 * (1 - 0.92) }}
          viewport={{ once: true }}
          transition={{ duration: 1.5, delay: 0.3, ease: 'easeOut' }}
        />
        <defs>
          <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--brand-muted)" />
            <stop offset="100%" stopColor="var(--brand-primary)" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.span
          className="text-sm font-bold text-theme-600 dark:text-brand-primary"
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          transition={{ delay: 0.8 }}
        >92</motion.span>
      </div>
    </div>
    <div>
      <p className="text-xs font-bold text-theme-600 dark:text-brand-primary/80 uppercase tracking-widest">Hot Lead</p>
      <p className="text-[10px] text-gray-500 dark:text-gray-600 mt-0.5">Auto-prioritized</p>
    </div>
  </div>
);

const CRMVisual = () => (
  <div className="space-y-2.5">
    {['CRM Sync', 'Task Created', 'Team Notified'].map((label, i) => (
      <motion.div
        key={i}
        initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
        transition={{ duration: 0.4, delay: 0.3 + i * 0.2 }}
        className="flex items-center gap-2.5"
      >
        <motion.div
          initial={{ scale: 0 }} whileInView={{ scale: 1 }} viewport={{ once: true }}
          transition={{ duration: 0.3, delay: 0.5 + i * 0.2, type: 'spring' }}
          className="w-4 h-4 rounded-full bg-theme-100 dark:bg-brand-primary/10 border border-theme-200 dark:border-brand-primary/20 flex items-center justify-center"
        >
          <motion.svg
            initial={{ pathLength: 0, opacity: 0 }} whileInView={{ pathLength: 1, opacity: 1 }} viewport={{ once: true }}
            transition={{ duration: 0.3, delay: 0.7 + i * 0.2 }}
            className="w-2.5 h-2.5 text-theme-600 dark:text-brand-primary"
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </motion.svg>
        </motion.div>
        <span className="text-xs text-gray-500 font-medium">{label}</span>
      </motion.div>
    ))}
  </div>
);

export const WorkflowSection = () => {
  const steps = [
    { icon: PhoneIncoming, num: '01', title: 'Customer Speaks', desc: 'Every call, voice note, and conversation is captured in real time with zero manual effort.', visual: <QuoteVisual /> },
    { icon: Sparkles, num: '02', title: 'AI Processing', desc: 'TalklyAI analyzes tone, intent, sentiment, and context across every interaction instantly.', visual: <WaveformVisual /> },
    { icon: Layers, num: '03', title: 'Intelligence Extraction', desc: 'Unstructured conversations are transformed into structured, queryable data points.', visual: <TagsVisual /> },
    { icon: Target, num: '04', title: 'Lead Qualification', desc: 'High-value leads are automatically scored and prioritized based on real conversation signals.', visual: <ScoreVisual /> },
    { icon: LayoutDashboard, num: '05', title: 'Team Action', desc: 'Insights flow directly into your CRM, triggering tasks and notifications for your sales team.', visual: <CRMVisual /> },
  ];

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15 } },
  };

  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 40, scale: 0.97 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] } },
  };

  return (
    <section id="how-it-works" className="relative py-24 sm:py-32 md:py-40 px-4 md:px-8 bg-white dark:bg-bg-dark-elevated overflow-hidden">
      <div className="absolute top-1/4 left-0 w-[400px] h-[400px] rounded-full bg-theme-100/40 dark:bg-brand-primary/[0.015] blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-0 w-[500px] h-[500px] rounded-full bg-theme-50/60 dark:bg-brand-muted/[0.02] blur-[120px] pointer-events-none" />

      <div className="max-w-5xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}
          variants={containerVariants}
          className="text-center max-w-2xl mx-auto mb-16 md:mb-24"
        >
          <motion.div variants={cardVariants}><SectionBadge label="How It Works" className="mb-6" /></motion.div>
          <motion.h2 variants={cardVariants} className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight text-gray-900 dark:text-white leading-tight mb-5">
            From Conversations to{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-grad-1 to-brand-grad-2 dark:from-brand-primary dark:to-brand-grad-3">
              Actionable Intelligence
            </span>
          </motion.h2>
          <motion.p variants={cardVariants} className="text-sm sm:text-base text-gray-500 dark:text-gray-400 leading-relaxed">
            Five steps. Fully automated. From raw customer conversations to closed deals.
          </motion.p>
        </motion.div>

        {/* Steps */}
        <motion.div
          variants={containerVariants} initial="hidden" whileInView="visible"
          viewport={{ once: true, margin: '-40px' }}
          className="space-y-5 sm:space-y-6"
        >
          {steps.map((step, i) => (
            <motion.div
              key={i} variants={cardVariants}
              className="group relative rounded-2xl border border-gray-200 dark:border-white/[0.06] bg-gray-50 dark:bg-white/[0.02] hover:bg-white dark:hover:bg-white/[0.04] hover:border-theme-200 dark:hover:border-brand-primary/15 shadow-sm dark:shadow-none hover:shadow-md dark:hover:shadow-none transition-all duration-500 overflow-hidden"
            >
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                <div className="absolute -top-20 -right-20 w-60 h-60 rounded-full bg-theme-100/30 dark:bg-brand-primary/[0.04] blur-[80px]" />
              </div>

              <div className="relative flex flex-col md:flex-row md:items-center gap-5 md:gap-8 p-6 sm:p-8">
                {/* Step number */}
                <div className="flex-shrink-0 flex items-center gap-4 md:gap-0 md:flex-col md:w-16">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-theme-50 dark:bg-gradient-to-br dark:from-brand-primary dark:to-brand-muted border border-theme-100 dark:border-brand-primary/10 flex items-center justify-center group-hover:bg-theme-100 dark:group-hover:from-brand-primary/15 dark:group-hover:to-brand-muted/10 dark:group-hover:border-brand-primary/20 transition-all duration-500">
                    <span className="text-sm font-bold text-theme-400 dark:text-white group-hover:text-theme-600 dark:group-hover:text-brand-primary transition-colors duration-500">
                      {step.num}
                    </span>
                  </div>
                  <step.icon size={16} className="md:hidden text-theme-400 dark:text-brand-primary/40" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2.5 mb-2">
                    <step.icon size={16} strokeWidth={1.8} className="hidden md:block text-theme-400 dark:text-brand-primary/40 group-hover:text-theme-600 dark:group-hover:text-brand-primary/70 transition-colors duration-500" />
                    <h4 className="text-base sm:text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-brand-grad-1 to-brand-grad-2 dark:from-brand-primary dark:to-brand-grad-1">
                      {step.title}
                    </h4>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-100 font-medium leading-relaxed group-hover:text-gray-600 dark:group-hover:text-gray-400 transition-colors duration-500 max-w-lg">
                    {step.desc}
                  </p>
                </div>

                {/* Visual */}
                <div className="flex-shrink-0 md:w-52 lg:w-60 mt-2 md:mt-0 pl-0 md:pl-4 md:border-l md:border-gray-100 dark:md:border-white/[0.04]">
                  {step.visual}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

