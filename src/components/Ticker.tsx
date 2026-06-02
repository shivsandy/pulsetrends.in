import { TrendingDown, TrendingUp } from 'lucide-react';
import { ipoStocks } from '../data/ipoData';

export default function Ticker() {
  const items = ipoStocks.slice(0, 20).flatMap((stock) => [
    {
      label: stock.ticker,
      value: stock.priceRange ? `Rs ${stock.priceRange.match(/\d[\d,]*/)?.[0] ?? stock.priceRange}` : '-',
      up: true,
    },
    {
      label: stock.ticker,
      value: `${stock.aiScores.overall}/100`,
      up: stock.aiScores.overall >= 60,
    },
  ]);

  return (
    <div className="bg-surface-100 border-y border-surface-300/60 overflow-hidden h-9">
      <div className="relative flex items-center h-full">
        <div className="animate-ticker flex items-center gap-6 whitespace-nowrap">
          {[...items, ...items].map((item, i) => (
            <div key={`${item.label}-${item.value}-${i}`} className="flex items-center gap-1.5 text-[12px]">
              <span className="font-semibold text-surface-white">{item.label}</span>
              <span className="text-surface-700">{item.value}</span>
              {item.up
                ? <TrendingUp className="w-3 h-3 text-success" />
                : <TrendingDown className="w-3 h-3 text-danger" />
              }
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
