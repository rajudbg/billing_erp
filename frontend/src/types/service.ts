export interface Service {
  id: number;
  company_id: number;
  name: string;
  description?: string | null;
  unit_price: number;
  tax_rate_id?: number | null;
  category_id?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceCreate {
  company_id: number;
  name: string;
  description?: string | null;
  unit_price: number;
  tax_rate_id?: number | null;
  category_id?: number | null;
  is_active?: boolean;
}

export interface ServiceUpdate extends Partial<ServiceCreate> {}

