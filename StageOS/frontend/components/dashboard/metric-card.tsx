'use client';

import { TrendingDown, TrendingUp, Minus } from 'lucide-react';
import type { ElementType, ReactNode } from 'react';

export interface MetricCardProps {
  label: string;
  value: number | string;
  subtitle?: string;
  detail?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color?: 'default' | 'teal' | 'red' | 'green' | 'orange';
  icon?: ElementType | ReactNode;
}

const iconBgMap: Record<NonNullable<MetricCardProps['color']>, string> = {
  default: 'bg-gray-100 text-gray-600',
  teal:    'bg-teal-50 text-teal-600',
  red:     'bg-red-50 text-red-600',
  green:   'bg-green-50 text-green-600',
  orange:  'bg-orange-50 text-orange-600',
};

const valueColorMap: Record<NonNullable<MetricCardProps['color']>, string> = {
  default: 'text-gray-900',
  teal:    'text-teal-700',
  red:     'text-red-700',
  green:   'text-green-700',
  orange:  'text-orange-700',
};

function isElementType(icon: unknown): icon is ElementType {
  return typeof icon === 'function';
}

export function MetricCard({
  label,
  value,
  subtitle,
  detail,
  trend,
  trendValue,
  color = 'default',
  icon,
}: MetricCardProps) {
  const iconBg = iconBgMap[color];
  const valueColor = valueColorMap[color];

  const renderedIcon = icon
    ? isElementType(icon)
      ? (() => { const Icon = icon as ElementType; return <Icon className="h-5 w-5" />; })()
      : (icon as ReactNode)
    : null;

  return (
    <article className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm text-gray-500 font-medium truncate">{label}</p>
          <p className={`mt-2 text-3xl font-bold tracking-tight ${valueColor}`}>{value}</p>
        </div>
        {renderedIcon ? (
          <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${iconBg}`}>
            {renderedIcon}
          </div>
        ) : null}
      </div>

      {(trend || trendValue || subtitle || detail) ? (
        <div className="mt-3 flex items-center gap-2">
          {trend === 'up' ? (
            <span className="inline-flex items-center gap-0.5 text-xs font-semibold text-green-600">
              <TrendingUp className="h-3 w-3" />
              {trendValue}
            </span>
          ) : trend === 'down' ? (
            <span className="inline-flex items-center gap-0.5 text-xs font-semibold text-red-600">
              <TrendingDown className="h-3 w-3" />
              {trendValue}
            </span>
          ) : trend === 'neutral' ? (
            <span className="inline-flex items-center gap-0.5 text-xs font-semibold text-gray-400">
              <Minus className="h-3 w-3" />
              {trendValue}
            </span>
          ) : null}
          {(subtitle || detail) ? (
            <p className="text-xs text-gray-500 leading-4">{subtitle ?? detail}</p>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}
