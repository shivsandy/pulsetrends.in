interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'outline' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md';
}

export default function Badge({ children, variant = 'default', size = 'sm' }: BadgeProps) {
  const variants = {
    default: 'bg-brand-muted text-brand-light border-brand-border',
    outline: 'bg-transparent text-surface-800 border-surface-400',
    success: 'bg-success-muted text-success border-success-border',
    warning: 'bg-warning-muted text-warning border-warning-border',
    danger: 'bg-danger-muted text-danger border-danger-border',
    info: 'bg-info-muted text-info border-info-border',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  };

  return (
    <span className={`inline-flex items-center gap-1 rounded-md border font-medium tracking-wide uppercase ${variants[variant]} ${sizes[size]}`}>
      {children}
    </span>
  );
}
