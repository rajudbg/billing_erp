import { apiClient } from "./client";
import type { Payment, PaymentCreate } from "../types/payment";

export const fetchPayments = async (): Promise<Payment[]> => {
  const { data } = await apiClient.get<Payment[]>("/api/v1/payments");
  return data;
};

export const createPayment = async (payload: PaymentCreate): Promise<Payment> => {
  const { data } = await apiClient.post<Payment>("/api/v1/payments", payload);
  return data;
};

