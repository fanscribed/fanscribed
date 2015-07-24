import Decimal from 'decimal.js';

export function range (start, end, step = new Decimal(1)) {
  let result = [];
  let current = start;
  while (current.lt(end)) {
    result.push(current);
    current = current.plus(step);
  }
  return result;
}
