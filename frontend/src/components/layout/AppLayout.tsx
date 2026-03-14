import React from "react";
import { Box, Container, Toolbar } from "@mui/material";

import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <Box sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <Header />
        {/* Header is fixed, so we need a spacer to avoid content hiding under it */}
        <Toolbar />
        <Box component="main" sx={{ flex: 1, py: { xs: 2, md: 3 } }}>
          <Container maxWidth="xl" sx={{ px: { xs: 2, md: 3 } }}>
            {children}
          </Container>
        </Box>
      </Box>
    </Box>
  );
};

