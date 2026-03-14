export interface PaymentAllocationCreate {
  invoice_id: number;
  allocated_amount: number;
}

export interface PaymentAllocation extends PaymentAllocationCreate {
  id: number;
}

export interface Payment {
  id: number;
  company_id: number;
  client_id: number;
  currency_id: number;
  payment_date: string;
  amount: number;
  payment_method: string;
  reference?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  allocations: PaymentAllocation[];
}

export interface PaymentCreate {
  company_id: number;
  client_id: number;
  currency_id: number;
  payment_date: string;
  amount: number;
  payment_method: string;
  reference?: string | null;
  notes?: string | null;
  allocations: PaymentAllocationCreate[];
}

