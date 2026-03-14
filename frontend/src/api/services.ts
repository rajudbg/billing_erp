import { apiClient } from "./client";
import type { Service, ServiceCreate, ServiceUpdate } from "../types/service";

export const fetchServices = async (): Promise<Service[]> => {
  const { data } = await apiClient.get<Service[]>("/api/v1/services");
  return data;
};

export const createService = async (payload: ServiceCreate): Promise<Service> => {
  const { data } = await apiClient.post<Service>("/api/v1/services", payload);
  return data;
};

export const updateService = async (id: number, payload: ServiceUpdate): Promise<Service> => {
  const { data } = await apiClient.put<Service>(`/api/v1/services/${id}`, payload);
  return data;
};

export const deleteService = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/v1/services/${id}`);
};

