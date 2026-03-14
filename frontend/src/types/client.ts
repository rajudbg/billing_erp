export interface ClientContact {
  id?: number;
  name: string;
  email: string;
  phone?: string | null;
  position?: string | null;
  is_primary?: boolean;
}

export interface Client {
  id: number;
  company_id: number;
  name: string;
  gst_number?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  billing_email?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  contacts: ClientContact[];
}

export interface ClientCreate {
  company_id: number;
  name: string;
  gst_number?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  billing_email?: string | null;
  is_active?: boolean;
}

export interface ClientUpdate extends Partial<ClientCreate> {}

