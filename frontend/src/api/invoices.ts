import { apiClient } from "./client";
import type { Invoice, InvoiceCreate } from "../types/invoice";

export const fetchInvoices = async (): Promise<Invoice[]> => {
  const { data } = await apiClient.get<Invoice[]>("/api/v1/invoices");
  return data;
};

export const createInvoice = async (payload: InvoiceCreate): Promise<Invoice> => {
  const { data } = await apiClient.post<Invoice>("/api/v1/invoices", payload);
  return data;
};

export const sendInvoiceEmail = async (id: number): Promise<void> => {
  await apiClient.post(`/api/v1/invoices/${id}/send-email`);
};

