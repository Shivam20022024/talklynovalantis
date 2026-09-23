'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function OverviewRedirect() {
  const params = useParams();
  const router = useRouter();
  useEffect(() => {
    router.replace(`/admin/companies/${params.id}`);
  }, [params.id, router]);
  return null;
}
