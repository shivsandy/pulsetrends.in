import { TrendingDown, TrendingUp } from 'lucide-react';
import { ipoStocks } from '../data/ipoData';

/** Extract the first numeric value from a price range string (e.g. "₹41" from "₹41 - 63"). */
function extractPrice(priceRange: string): string | null {
  const m = priceRange.match(/[\d,]+(?:\.\d+)?/);
  return m ? m[0] : null;
}

export default function Ticker() {
  const items = ipoStocks.slice(0, 20).map((stock) => {
    const price = stock.priceRange ? extractPrice(stock.priceRange) : null;
    const score = `${stock.aiScores.overall}/100`;
    const up = stock.aiScores.overall >= 60;
    // Combine into a single compact badge:  TICKER [₹PRICE · SCORE/100] or TICKER [SCORE/100]
    const badge = price ? `₹${price} · ${score}` : score;
    return { ticker: stock.ticker, badge, up };
  });

  return (
    <div className="bg-surface-100 border-y border-surface-300/60 overflow-hidden h-9">
      <div className="relative flex items-center h-full">
        <div className="animate-ticker flex items-center gap-5 whitespace-nowrap">
          {[...items, ...items].map((item, i) => (
            <div key={`${item.ticker}-${i}`} className="flex items-center gap-2 text-[12px]">
              <span className="font-semibold text-surface-white shrink-0">{item.ticker}</span>
              <span className="inline-flex items-center gap-1 rounded-full bg-surface-200 px-2.5 py-0.5 text-[11px] text-surface-700 leading-none">
                {item.badge}
                {item.up
                  ? <TrendingUp className="w-2.5 h-2.5 text-success shrink-0" />
                  : <TrendingDown className="w-2.5 h-2.5 text-danger shrink-0" />
                }
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
