export const formatCurrency = (value: number, currencyCode = "INR", locale = "en-IN"): string =>
  new Intl.NumberFormat(locale, {
    style: "currency",
    currency: currencyCode,
    maximumFractionDigits: 2
  }).format(value);

