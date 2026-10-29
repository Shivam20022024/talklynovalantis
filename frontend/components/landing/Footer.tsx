'use client';

import Image from 'next/image';
import Link from 'next/link';
import React from 'react';

const LEGAL_LINKS = [
  { name: 'Pricing', href: '/pricing' },
  { name: 'Terms', href: '/terms' },
  { name: 'Privacy', href: '/privacy' },
  { name: 'Refund Policy', href: '/refund-policy' },
  { name: 'Contact', href: '/contact' },
];

const SocialIcon = ({ children, href }: { children: React.ReactNode; href: string }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="w-10 h-10 rounded-full border border-gray-200 dark:border-white/[0.08] flex items-center justify-center text-gray-400 dark:text-gray-500 hover:text-theme-600 dark:hover:text-brand-primary hover:border-theme-200 dark:hover:border-brand-primary/25 hover:bg-theme-50 dark:hover:bg-white/[0.03] transition-all duration-300"
  >
    {children}
  </a>
);

export const Footer = () => {
  return (
    <footer className="relative bg-gray-50 dark:bg-bg-dark-elevated overflow-hidden pt-16 sm:pt-20 pb-8">
      {/* Top divider */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-white/[0.06] to-transparent" />
      
      <div className="max-w-4xl mx-auto px-4 md:px-8 flex flex-col items-center text-center relative z-10">
        {/* Brand */}
        <div className="flex items-center gap-3 mb-6">
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
          <span className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            Talkly<span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-grad-1 to-brand-grad-2 dark:from-brand-primary dark:to-brand-grad-3">AI</span>
          </span>
        </div>

        <p className="text-sm sm:text-base text-gray-500 font-medium leading-relaxed max-w-lg mb-8">
          We transform unstructured customer conversations into actionable sales intelligence, helping you close deals faster and smarter.
        </p>

        {/* Socials */}
        <div className="flex items-center gap-4 mb-8 md:mb-0">
          {/* Email icon removed */}
          <SocialIcon href="https://x.com/infoNovalantis">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          </SocialIcon>
          <SocialIcon href="https://novalantis.com/products/talklyai/">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
            </svg>
          </SocialIcon>
        </div>

        {/* Bottom bar */}
        <div className="w-full relative pt-8 border-t border-gray-200/60 dark:border-white/[0.06]">
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 w-[300px] h-[120px] rounded-full bg-theme-100/30 dark:bg-brand-primary/[0.06] blur-[60px] pointer-events-none" />
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-gray-400 dark:text-gray-500 font-medium">
              This product is made by Novalantis. All Rights Reserved.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-5 text-xs text-gray-400 dark:text-gray-500 font-medium">
              {LEGAL_LINKS.map((link) => (
                <Link key={link.href} href={link.href} className="hover:text-theme-600 dark:hover:text-brand-primary transition-colors">
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
