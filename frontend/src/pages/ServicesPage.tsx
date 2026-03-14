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

import { fetchServices, createService, updateService, deleteService } from "../api/services";
import type { Service, ServiceCreate } from "../types/service";
import { Loader } from "../components/common/Loader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { formatCurrency } from "../utils/format";
import { getErrorMessage } from "../utils/error";

const defaultCompanyId = 1;

const ServicesPage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Service | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<ServiceCreate>({
    company_id: defaultCompanyId,
    name: "",
    unit_price: 0
  });

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchServices();
      setServices(data);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load services"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({
      company_id: defaultCompanyId,
      name: "",
      unit_price: 0
    });
    setDialogOpen(true);
  };

  const openEdit = (service: Service) => {
    setEditing(service);
    setForm({
      company_id: service.company_id,
      name: service.name,
      description: service.description || "",
      unit_price: service.unit_price,
      tax_rate_id: service.tax_rate_id || undefined,
      category_id: service.category_id || undefined,
      is_active: service.is_active
    });
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      if (editing) {
        await updateService(editing.id, form);
      } else {
        await createService(form);
      }
      setDialogOpen(false);
      await load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to save service. Please check the form and try again."));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (service: Service) => {
    if (!window.confirm(`Delete service ${service.name}?`)) return;
    try {
      await deleteService(service.id);
      await load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to delete service. It may be in use by invoices."));
    }
  };

  if (loading) return <Loader />;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h5">Services</Typography>
        <Button onClick={openCreate}>Add Service</Button>
      </Box>
      {error && <ErrorAlert message={error} />}

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Unit Price</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {services.map((s) => (
            <TableRow key={s.id}>
              <TableCell>{s.name}</TableCell>
              <TableCell>{s.description}</TableCell>
              <TableCell>{formatCurrency(s.unit_price)}</TableCell>
              <TableCell align="right">
                <IconButton size="small" onClick={() => openEdit(s)}>
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton size="small" onClick={() => handleDelete(s)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? "Edit Service" : "Add Service"}</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          <TextField
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
          <TextField
            label="Description"
            value={form.description || ""}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <TextField
            label="Unit Price"
            type="number"
            value={form.unit_price}
            onChange={(e) => setForm({ ...form, unit_price: Number(e.target.value) })}
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

export default ServicesPage;

