import { apiClient } from "./client";
import type { LoginResponse, User } from "../types/auth";

interface LoginJsonRequest {
  email: string;
  password: string;
}

interface TokenOnlyResponse {
  access_token: string;
  token_type: string;
}

export const loginRequest = async (email: string, password: string): Promise<LoginResponse> => {
  const payload: LoginJsonRequest = { email, password };
  const { data } = await apiClient.post<TokenOnlyResponse>("/api/v1/auth/login-json", payload);

  // Fetch current user info after login
  const meResp = await apiClient.get<User>("/api/v1/auth/me", {
    headers: {
      Authorization: `Bearer ${data.access_token}`
    }
  });

  return {
    access_token: data.access_token,
    token_type: data.token_type,
    user: meResp.data
  };
};

