import { TrendingUp, type LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string;
  change: string;
  Icon: LucideIcon;
  tone: 'blue' | 'violet' | 'green' | 'orange';
}

export function MetricCard({ label, value, change, Icon, tone }: MetricCardProps) {
  return (
    <article className="rounded-xl border border-border/80 bg-card p-6 shadow-sm hover:shadow-md transition-all hover:border-primary/30">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-foreground">
          {label}
        </h3>
        <span className={`metric-icon ${tone} h-10 w-10 shrink-0`}><Icon size={18} /></span>
      </div>
      <div className="mt-6 flex items-end justify-between">
        <p className="text-4xl font-black tracking-tight text-foreground">{value}</p>
        <span className="flex items-center gap-1 text-sm font-bold text-emerald-600 dark:text-emerald-400">
          <TrendingUp size={16} className="stroke-[2.5]" />{change}
        </span>
      </div>
      <p className="mt-2 text-xs font-semibold text-muted-foreground">vs previous period</p>
    </article>
  );
}
