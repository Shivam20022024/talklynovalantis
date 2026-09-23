'use client';

// NOTE: this is a UX convenience only. Real tenant isolation is enforced by the
// backend on every request - never rely on these redirects for security.

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';

const COMPANY_ADMIN_ONLY_PREFIXES = [
  '/dashboard', '/leads', '/campaigns', '/calls', '/prompt', '/agent',
  '/voice-intelligence', '/analytics', '/team',
];

export default function RouteGuard({ children }: { children: React.ReactNode }) {
  const { user, loading, isSuperAdmin } = useAuth();
  const pathname = usePathname() || '';
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    if (!user) {
      router.replace('/login');
      return;
    }

    const onAdminRoute = pathname.startsWith('/admin');

    if (onAdminRoute && !isSuperAdmin) {
      router.replace('/dashboard');
      return;
    }

    if (
      isSuperAdmin &&
      COMPANY_ADMIN_ONLY_PREFIXES.some((p) => pathname === p || pathname.startsWith(p + '/'))
    ) {
      router.replace('/admin');
    }
  }, [user, loading, isSuperAdmin, pathname, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="animate-pulse text-muted-foreground">Loading…</div>
      </div>
    );
  }

  if (!user) return null;
  if (pathname.startsWith('/admin') && !isSuperAdmin) return null;

  return <>{children}</>;
}
