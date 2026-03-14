import { apiClient } from "./client";
import type { Client, ClientCreate, ClientUpdate } from "../types/client";

export const fetchClients = async (): Promise<Client[]> => {
  const { data } = await apiClient.get<Client[]>("/api/v1/clients");
  return data;
};

export const createClient = async (payload: ClientCreate): Promise<Client> => {
  const { data } = await apiClient.post<Client>("/api/v1/clients", payload);
  return data;
};

export const updateClient = async (id: number, payload: ClientUpdate): Promise<Client> => {
  const { data } = await apiClient.put<Client>(`/api/v1/clients/${id}`, payload);
  return data;
};

export const deleteClient = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/v1/clients/${id}`);
};

