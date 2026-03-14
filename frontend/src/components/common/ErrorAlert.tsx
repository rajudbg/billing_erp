import React from "react";
import { Alert } from "@mui/material";

export const ErrorAlert: React.FC<{ message: string }> = ({ message }) => (
  <Alert severity="error" sx={{ mb: 2 }}>
    {message}
  </Alert>
);

