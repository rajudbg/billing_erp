import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import { fetchClients, createClient, updateClient, deleteClient } from "../api/clients";
import type { Client, ClientCreate } from "../types/client";
import { Loader } from "../components/common/Loader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { getErrorMessage } from "../utils/error";

const defaultCompanyId = 1; // MVP: single company

const ClientsPage: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<ClientCreate>({
    company_id: defaultCompanyId,
    name: "",
    billing_email: ""
  });

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchClients();
      setClients(data);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load clients"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditingClient(null);
    setForm({
      company_id: defaultCompanyId,
      name: "",
      billing_email: ""
    });
    setDialogOpen(true);
  };

  const openEdit = (client: Client) => {
    setEditingClient(client);
    setForm({
      company_id: client.company_id,
      name: client.name,
      billing_email: client.billing_email || "",
      gst_number: client.gst_number || "",
      address_line1: client.address_line1 || "",
      address_line2: client.address_line2 || "",
      city: client.city || "",
      state: client.state || "",
      country: client.country || "",
      postal_code: client.postal_code || ""
    });
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      if (editingClient) {
        await updateClient(editingClient.id, form);
      } else {
        await createClient(form);
      }
      setDialogOpen(false);
      await load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to save client. Please check the form and try again."));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (client: Client) => {
    if (!window.confirm(`Delete client ${client.name}?`)) return;
    try {
      await deleteClient(client.id);
      await load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to delete client"));
    }
  };

  if (loading) return <Loader />;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h5">Clients</Typography>
        <Button onClick={openCreate}>Add Client</Button>
      </Box>
      {error && <ErrorAlert message={error} />}

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Billing Email</TableCell>
            <TableCell>GST</TableCell>
            <TableCell>Country</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {clients.map((c) => (
            <TableRow key={c.id}>
              <TableCell>{c.name}</TableCell>
              <TableCell>{c.billing_email}</TableCell>
              <TableCell>{c.gst_number}</TableCell>
              <TableCell>{c.country}</TableCell>
              <TableCell align="right">
                <IconButton size="small" onClick={() => openEdit(c)}>
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton size="small" onClick={() => handleDelete(c)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingClient ? "Edit Client" : "Add Client"}</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          <TextField
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <TextField
            label="Billing Email"
            value={form.billing_email || ""}
            onChange={(e) => setForm({ ...form, billing_email: e.target.value })}
          />
          <TextField
            label="GST Number"
            value={form.gst_number || ""}
            onChange={(e) => setForm({ ...form, gst_number: e.target.value })}
          />
          <TextField
            label="Address Line 1"
            value={form.address_line1 || ""}
            onChange={(e) => setForm({ ...form, address_line1: e.target.value })}
          />
          <TextField
            label="Address Line 2"
            value={form.address_line2 || ""}
            onChange={(e) => setForm({ ...form, address_line2: e.target.value })}
          />
          <TextField
            label="City"
            value={form.city || ""}
            onChange={(e) => setForm({ ...form, city: e.target.value })}
          />
          <TextField
            label="State"
            value={form.state || ""}
            onChange={(e) => setForm({ ...form, state: e.target.value })}
          />
          <TextField
            label="Country"
            value={form.country || ""}
            onChange={(e) => setForm({ ...form, country: e.target.value })}
          />
          <TextField
            label="Postal Code"
            value={form.postal_code || ""}
            onChange={(e) => setForm({ ...form, postal_code: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ClientsPage;

