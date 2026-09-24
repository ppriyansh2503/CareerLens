import React from 'react';
import { ShieldCheck, Award, AlertTriangle, Clock } from 'lucide-react';

interface TrustBadgeProps {
  tier: 'GOLD' | 'SILVER' | 'BRONZE' | 'NONE' | string;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
}

export const TrustBadge: React.FC<TrustBadgeProps> = ({ tier, size = 'md', showDetails = false }) => {
  const normalized = tier ? tier.toUpperCase() : 'NONE';

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5'
  };

  const iconSizes = {
    sm: 12,
    md: 14,
    lg: 16
  };

  if (normalized === 'GOLD') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 shadow-sm shadow-amber-500/10 ${sizeClasses[size]}`}>
        <Award size={iconSizes[size]} className="text-amber-400 animate-pulse" />
        <span>GOLD BADGE</span>
        {showDetails && <span className="text-amber-400/80 font-normal">| QR & Crypto Verified</span>}
      </span>
    );
  }

  if (normalized === 'SILVER') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-slate-300/10 text-slate-200 border border-slate-400/30 ${sizeClasses[size]}`}>
        <ShieldCheck size={iconSizes[size]} className="text-slate-300" />
        <span>SILVER BADGE</span>
        {showDetails && <span className="text-slate-400 font-normal">| OCR Verified</span>}
      </span>
    );
  }

  if (normalized === 'FLAGGED') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/40 animate-pulse ${sizeClasses[size]}`}>
        <AlertTriangle size={iconSizes[size]} className="text-rose-400" />
        <span>FLAGGED</span>
        {showDetails && <span className="text-rose-400/80 font-normal">| Tamper Anomaly</span>}
      </span>
    );
  }

  if (normalized === 'BRONZE' || normalized === 'PENDING') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-orange-500/10 text-orange-300 border border-orange-500/20 ${sizeClasses[size]}`}>
        <Clock size={iconSizes[size]} className="text-orange-400" />
        <span>BRONZE</span>
        {showDetails && <span className="text-orange-400/80 font-normal">| Self-Reported</span>}
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-slate-800 text-slate-400 border border-slate-700 ${sizeClasses[size]}`}>
      <span>UNVERIFIED</span>
    </span>
  );
};
