import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export interface Crumb {
  name: string;
  path?: string;
}

interface BreadcrumbsProps {
  items: Crumb[];
}

interface BreadcrumbsProps {
  items: Crumb[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  if (items.length === 0) return null;
  return (
    <nav aria-label="Breadcrumb" className="mb-6">
      <ol className="flex items-center flex-wrap gap-1.5 text-[12px] text-surface-600">
        {items.map((crumb, idx) => {
          const isLast = idx === items.length - 1;
          return (
            <li key={`${crumb.name}-${idx}`} className="flex items-center gap-1.5">
              {idx === 0 && <Home className="w-3 h-3 text-surface-500" aria-hidden="true" />}
              {crumb.path && !isLast ? (
                <Link
                  to={crumb.path}
                  className="hover:text-surface-900 transition-colors"
                >
                  {crumb.name}
                </Link>
              ) : (
                <span className={isLast ? 'text-surface-900 font-medium' : ''} aria-current={isLast ? 'page' : undefined}>
                  {crumb.name}
                </span>
              )}
              {!isLast && <ChevronRight className="w-3 h-3 text-surface-500" aria-hidden="true" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
