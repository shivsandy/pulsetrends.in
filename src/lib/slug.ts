import { slugify as _slugify } from '../seo/config';

export function slugify(input: string): string {
  return _slugify(input);
}

export function makeIdSlug(prefix: string, id: string | number): string {
  return `${_slugify(prefix)}-${id}`;
}
