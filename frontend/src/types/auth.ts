export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role?: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

