import type { AxiosError } from "axios";

export const getErrorMessage = (error: unknown, fallback = "Something went wrong") => {
  const axiosError = error as AxiosError<any>;
  const detail =
    axiosError?.response?.data?.detail ??
    axiosError?.response?.data?.message ??
    axiosError?.message;
  if (typeof detail === "string" && detail.trim().length > 0) {
    return detail;
  }
  return fallback;
};

