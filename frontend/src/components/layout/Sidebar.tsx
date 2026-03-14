import React from "react";
import { Drawer, List, ListItemButton, ListItemText, Toolbar } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

const drawerWidth = 220;

const menuItems = [
  { label: "Dashboard", path: "/" },
  { label: "Clients", path: "/clients" },
  { label: "Services", path: "/services" },
  { label: "Invoices", path: "/invoices" },
  { label: "Payments", path: "/payments" }
];

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
          borderRightColor: "divider"
        }
      }}
    >
      <Toolbar />
      <List>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={location.pathname === item.path}
            onClick={() => navigate(item.path)}
            sx={{
              mx: 1,
              my: 0.5,
              borderRadius: 1,
              "&.Mui-selected": {
                bgcolor: "action.selected",
                "&:hover": { bgcolor: "action.selected" }
              }
            }}
          >
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
};

