/**
 * Money on this platform is rupees: strategies trade NSE and BSE through
 * Upstox. The UI previously formatted every figure as USD.
 *
 * en-IN also groups by lakh (1,00,000 rather than 100,000), which is what a
 * user reconciling against a broker statement expects to see.
 */
const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const inrCompact = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  notation: "compact",
  maximumFractionDigits: 1,
});

const units = new Intl.NumberFormat("en-IN", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const formatCurrency = (value: number | null | undefined): string =>
  inr.format(Number(value ?? 0));

/** For headline figures where the exact paise are noise. */
export const formatCurrencyCompact = (value: number | null | undefined): string =>
  inrCompact.format(Number(value ?? 0));

export const formatUnits = (value: number | null | undefined): string =>
  units.format(Number(value ?? 0));

/** Signed, so a gain reads as +₹1,200.00 rather than ₹1,200.00. */
export const formatSigned = (value: number | null | undefined): string => {
  const n = Number(value ?? 0);
  return `${n > 0 ? "+" : ""}${inr.format(n)}`;
};

/** Market direction. Returns a class name, never a colour directly. */
export const directionClass = (value: number | null | undefined): string => {
  const n = Number(value ?? 0);
  if (n > 0) return "long";
  if (n < 0) return "short";
  return "flat";
};
