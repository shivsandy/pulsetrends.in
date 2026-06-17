import type { IPOStock } from '../data/ipoData';

/**
 * Returns a display-friendly date string for an IPO.
 * For listed IPOs with a listing date, shows "Listed on YYYY-MM-DD".
 * For upcoming/open IPOs, shows the expected date.
 * Falls back to "TBA" if no date is available.
 */
export function getDateDisplay(stock: IPOStock): string {
  if (stock.status === 'listed' && stock.listingDate) {
    return `Listed on ${stock.listingDate.split(',')[0]}`;
  }
  if (stock.expectedDate) {
    return stock.expectedDate.split(',')[0];
  }
  return 'TBA';
}
