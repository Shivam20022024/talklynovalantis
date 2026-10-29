'use client';

import React from 'react';
import { Navbar } from '@/components/landing/Navbar';
import { HeroSection } from '@/components/landing/HeroSection';
import { ValuePropSection } from '@/components/landing/ValuePropSection';
import { CapabilitiesSection } from '@/components/landing/CapabilitiesSection';
import { WorkflowSection } from '@/components/landing/WorkflowSection';
import { CTASection } from '@/components/landing/CTASection';
import { Footer } from '@/components/landing/Footer';

const LandingPage = () => {
  const handleStart = () => {
    // Demo implementation for onStart
    console.log("Starting demo or navigating to signup...");
  };

  return (
    <div className="min-h-screen text-slate-800 dark:text-slate-200 font-sans selection:bg-theme-500/30 selection:text-theme-900 overflow-x-hidden bg-white dark:bg-background transition-colors duration-300">
      <Navbar />
      <main>
        <HeroSection onStart={handleStart} />
        <ValuePropSection />
        <CapabilitiesSection />
        <WorkflowSection />
        <CTASection onStart={handleStart} />
      </main>
      <Footer />
    </div>
  );
};

export default LandingPage;
