import { apiClient } from "./client";
import type {
  DashboardSummary,
  MonthlyRevenueItem,
  OutstandingInvoiceItem
} from "../types/dashboard";

export const fetchDashboardSummary = async (): Promise<DashboardSummary> => {
  const { data } = await apiClient.get<DashboardSummary>("/api/v1/dashboard/summary");
  return data;
};

export const fetchMonthlyRevenue = async (): Promise<MonthlyRevenueItem[]> => {
  const { data } = await apiClient.get<MonthlyRevenueItem[]>("/api/v1/dashboard/monthly-revenue");
  return data;
};

export const fetchOutstandingInvoices = async (): Promise<OutstandingInvoiceItem[]> => {
  const { data } = await apiClient.get<OutstandingInvoiceItem[]>(
    "/api/v1/dashboard/outstanding-invoices"
  );
  return data;
};

