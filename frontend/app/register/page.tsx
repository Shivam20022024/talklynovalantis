'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Bot, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@/components/providers/AuthProvider';
import { fetchApi } from '@/lib/api';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('general_sales');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pendingNotice, setPendingNotice] = useState(false);

  const router = useRouter();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await fetchApi('/api/v1/auth/register', {
        method: 'POST',
        requireAuth: false,
        body: JSON.stringify({
          name,
          company_name: companyName,
          industry,
          email,
          password,
        }),
      });

      if (data.status === 'success' && data.access_token && data.user) {
        login(data.access_token, data.user);
        router.push('/dashboard');
      } else if (data.status === 'pending_review') {
        setPendingNotice(true);
      } else {
        throw new Error(data.message || 'Registration failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create workspace');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 shadow-sm">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary mb-3">
            <Bot size={24} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Create Workspace</h1>
          <p className="text-xs text-muted-foreground mt-1">Get started with 10 free AI voice calling minutes</p>
          
          <div className="mt-3.5 inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <Sparkles size={12} /> Instant Trial Sandbox — No Card Required
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-destructive/10 p-3 text-xs text-destructive">
            {error}
          </div>
        )}

        {pendingNotice ? (
          <div className="text-center py-6 space-y-3">
            <div className="flex justify-center text-emerald-500"><CheckCircle2 size={36} /></div>
            <h3 className="font-bold text-base">Request Submitted</h3>
            <p className="text-xs text-muted-foreground">Your account request has been received. Our team will activate your workspace shortly.</p>
            <Link href="/login" className="inline-block mt-4 text-xs font-semibold text-primary hover:underline">
              Return to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="text-xs font-semibold text-muted-foreground">Your Full Name</label>
              <input
                required
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-muted-foreground">Company / Organization Name</label>
              <input
                required
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Acme Inc."
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-muted-foreground">Primary Industry / Use Case</label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
              >
                <option value="general_sales">B2B Sales & Services</option>
                <option value="healthcare">Healthcare & Medical Clinics</option>
                <option value="edtech">EdTech & Education</option>
                <option value="bfsi">BFSI & Loans</option>
                <option value="real_estate">Real Estate</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-muted-foreground">Business Email</label>
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@company.com"
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-muted-foreground">Password</label>
              <input
                required
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-2 w-full flex items-center justify-center gap-2 rounded-lg bg-primary py-2.5 text-sm font-semibold text-primary-foreground shadow-md hover:opacity-90 disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : 'Start Free Trial'}
            </button>
          </form>
        )}

        <div className="mt-6 text-center text-xs text-muted-foreground">
          Already have an account?{' '}
          <Link href="/login" className="font-semibold text-primary hover:underline">
            Sign in
          </Link>
          <span className="mx-2">•</span>
          <Link href="/pricing" className="text-muted-foreground hover:underline">
            View Pricing
          </Link>
        </div>
      </div>
    </div>
  );
}
