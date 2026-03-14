export interface InvoiceItemCreate {
  service_id?: number | null;
  description: string;
  quantity: number;
  unit_price: number;
  tax_rate_percent: number;
}

export interface InvoiceItem extends InvoiceItemCreate {
  id: number;
  line_subtotal: number;
  line_tax_amount: number;
  line_total: number;
  sort_order: number;
}

export interface Invoice {
  id: number;
  company_id: number;
  client_id: number;
  currency_id: number;
  issue_date: string;
  due_date: string;
  notes?: string | null;
  invoice_number: string;
  status: string;
  subtotal_amount: number;
  tax_amount: number;
  total_amount: number;
  amount_paid: number;
  amount_due: number;
  pdf_path?: string | null;
  created_at: string;
  updated_at: string;
  items: InvoiceItem[];
}

export interface InvoiceCreate {
  company_id: number;
  client_id: number;
  currency_id: number;
  issue_date: string;
  due_date: string;
  notes?: string | null;
  items: InvoiceItemCreate[];
}

