export interface DashboardSummary {
  total_revenue: number;
  total_invoices: number;
  total_outstanding: number;
  total_paid: number;
}

export interface MonthlyRevenueItem {
  year: number;
  month: number;
  revenue: number;
}

export interface OutstandingInvoiceItem {
  id: number;
  invoice_number: string;
  client_name: string;
  issue_date: string;
  due_date: string;
  amount_due: number;
}

