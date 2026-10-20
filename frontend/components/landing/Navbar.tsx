'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Sun, Moon } from 'lucide-react';
import { useTheme } from 'next-themes';
import Image from 'next/image';

export const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Features', href: '#features' },
    { name: 'How it works', href: '#how-it-works' },
    { name: 'Pricing', href: '/pricing' },
  ];

  const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith('#')) {
      e.preventDefault();
      const targetId = href.substring(1);
      const elem = document.getElementById(targetId);
      if (elem) {
        elem.scrollIntoView({ behavior: 'smooth' });
        setMobileMenuOpen(false);
      }
    }
  };

  return (
    <>
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className={`fixed left-0 right-0 z-[100] transition-all duration-300 mx-auto max-w-5xl px-4 ${
          isScrolled ? 'top-4' : 'top-6'
        }`}
      >
        <div className={`flex items-center justify-between h-16 px-4 rounded-2xl transition-all duration-300 ${
          isScrolled
            ? 'bg-white/90 dark:bg-bg-dark-card/90 backdrop-blur-xl border border-gray-200 dark:border-white/10 shadow-lg shadow-gray-300/40 dark:shadow-theme-900/20'
            : 'bg-white/70 dark:bg-bg-dark-card/60 backdrop-blur-md border border-gray-200/60 dark:border-white/5 shadow-sm'
        }`}>
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center gap-3 cursor-pointer" onClick={() => window.location.href = '/'}>
          
              <Image
                src="/logo-white.png"
                alt="Logo"
                width={550}
                height={453}
                className="h-[42px] w-auto flex-shrink-0 object-contain hidden dark:block"
                priority
                unoptimized
              />
              <Image
                src="/logo-color.png"
                alt="Logo"
                width={550}
                height={453}
                className="h-[42px] w-auto flex-shrink-0 object-contain block dark:hidden"
                priority
                unoptimized
              />
            <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">
              Talkly<span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-grad-1 to-brand-grad-2 dark:from-brand-primary dark:to-brand-grad-3">AI</span>
            </span>
          </div>

          {/* Nav Links – Desktop */}
          <div className="hidden md:flex items-center justify-center flex-1 mx-8 gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleScrollTo(e, link.href)}
                className="text-sm font-semibold text-gray-500 dark:text-gray-400 hover:text-brand-muted dark:hover:text-brand-primary transition-colors"
              >
                {link.name}
              </a>
            ))}
          </div>

          {/* Actions – Desktop */}
          <div className="hidden md:flex flex-shrink-0 items-center gap-4">
            {mounted && (
              <button
                onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-brand-muted dark:hover:text-brand-primary hover:bg-gray-100 dark:hover:bg-white/5 rounded-full transition-colors"
                aria-label="Toggle theme"
              >
                {resolvedTheme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            )}
            <button onClick={() => window.location.href = "/login"} className="text-gray-600 dark:text-gray-300 hover:text-foreground text-sm font-semibold px-2 py-1.5 transition-colors">
              Login
            </button>
            <button onClick={() => window.location.href = "/register"} className="bg-gradient-to-r from-brand-primary to-brand-muted text-white dark:text-bg-dark-card px-5 py-2.5 rounded-xl text-sm font-bold shadow-md shadow-theme-500/20 transition-all hover:opacity-90 hover:scale-105 active:scale-95">
              Free Trial
            </button>
          </div>

          {/* Actions – Mobile */}
          <div className="md:hidden flex items-center gap-2">
            {mounted && (
              <button
                onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-brand-muted dark:hover:text-brand-primary hover:bg-gray-100 dark:hover:bg-white/5 rounded-full transition-colors"
              >
                {resolvedTheme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            )}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white p-2"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-x-4 top-28 z-[90] md:hidden rounded-2xl bg-white/95 dark:bg-bg-dark-card/95 backdrop-blur-xl shadow-2xl border border-gray-200 dark:border-white/10 overflow-hidden"
          >
            <div className="px-4 pt-4 pb-6 space-y-2">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={(e) => handleScrollTo(e, link.href)}
                  className="block px-4 py-3 rounded-xl text-base font-semibold text-gray-600 dark:text-gray-300 hover:text-brand-muted dark:hover:text-brand-primary hover:bg-gray-100 dark:hover:bg-white/5 transition-colors"
                >
                  {link.name}
                </a>
              ))}
              <div className="pt-4 px-4">
                <button onClick={() => window.location.href = "/login"} className="w-full bg-gradient-to-r from-brand-primary to-brand-muted text-white dark:text-bg-dark-card px-6 py-3.5 rounded-xl text-sm font-bold shadow-md shadow-theme-500/20 transition-all hover:opacity-90 flex justify-center items-center">
                  Login
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
