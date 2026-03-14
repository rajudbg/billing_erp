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
  IconButton,
  Stack
} from "@mui/material";
import EmailIcon from "@mui/icons-material/Email";
import FileDownloadIcon from "@mui/icons-material/FileDownload";

import { fetchInvoices, createInvoice, sendInvoiceEmail } from "../api/invoices";
import { fetchClients } from "../api/clients";
import { fetchServices } from "../api/services";
import type { Invoice, InvoiceCreate, InvoiceItemCreate } from "../types/invoice";
import type { Client } from "../types/client";
import type { Service } from "../types/service";
import { Loader } from "../components/common/Loader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { formatCurrency } from "../utils/format";
import { apiClient } from "../api/client";
import { getErrorMessage } from "../utils/error";

const defaultCompanyId = 1;
const defaultCurrencyId = 1;

const InvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState<InvoiceCreate>({
    company_id: defaultCompanyId,
    client_id: 0,
    currency_id: defaultCurrencyId,
    issue_date: new Date().toISOString().slice(0, 10),
    due_date: new Date().toISOString().slice(0, 10),
    items: []
  });

  const [items, setItems] = useState<InvoiceItemCreate[]>([]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [inv, cls, svs] = await Promise.all([
        fetchInvoices(),
        fetchClients(),
        fetchServices()
      ]);
      setInvoices(inv);
      setClients(cls);
      setServices(svs);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load invoices"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setForm({
      company_id: defaultCompanyId,
      client_id: clients[0]?.id || 0,
      currency_id: defaultCurrencyId,
      issue_date: new Date().toISOString().slice(0, 10),
      due_date: new Date().toISOString().slice(0, 10),
      items: []
    });
    setItems([]);
    setDialogOpen(true);
  };

  const addItem = () => {
    setItems([
      ...items,
      {
        description: "",
        quantity: 1,
        unit_price: 0,
        tax_rate_percent: 0
      }
    ]);
  };

  const updateItem = (index: number, patch: Partial<InvoiceItemCreate>) => {
    const copy = [...items];
    copy[index] = { ...copy[index], ...patch };
    setItems(copy);
  };

  const removeItem = (index: number) => {
    const copy = [...items];
    copy.splice(index, 1);
    setItems(copy);
  };

  const handleSubmit = async () => {
    if (!form.client_id || items.length === 0) {
      setError("Client and at least one line item are required");
      return;
    }
    setSaving(true);
    try {
      const payload: InvoiceCreate = {
        ...form,
        items
      };
      await createInvoice(payload);
      setDialogOpen(false);
      await load();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create invoice. Please check form values and try again."));
    } finally {
      setSaving(false);
    }
  };

  const handleSendEmail = async (invoice: Invoice) => {
    try {
      await sendInvoiceEmail(invoice.id);
      alert("Invoice email queued.");
    } catch (err) {
      setError(getErrorMessage(err, "Failed to send invoice email"));
    }
  };

  const handleDownloadPdf = (invoice: Invoice) => {
    if (!invoice.pdf_path) {
      alert("PDF not available");
      return;
    }
    const filename = invoice.pdf_path.split("/").pop();
    if (!filename) {
      alert("Invalid PDF path");
      return;
    }
    const baseURL = apiClient.defaults.baseURL?.replace(/\/$/, "") ?? "";
    const url = `${baseURL}/generated_invoices/${encodeURIComponent(filename)}`;
    window.open(url, "_blank");
  };

  if (loading) return <Loader />;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h5">Invoices</Typography>
        <Button onClick={openCreate}>Create Invoice</Button>
      </Box>
      {error && <ErrorAlert message={error} />}

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Number</TableCell>
            <TableCell>Client</TableCell>
            <TableCell>Issue Date</TableCell>
            <TableCell>Due Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Total</TableCell>
            <TableCell>Amount Due</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {invoices.map((inv) => {
            const client = clients.find((c) => c.id === inv.client_id);
            return (
              <TableRow key={inv.id}>
                <TableCell>{inv.invoice_number}</TableCell>
                <TableCell>{client?.name || inv.client_id}</TableCell>
                <TableCell>{inv.issue_date}</TableCell>
                <TableCell>{inv.due_date}</TableCell>
                <TableCell>{inv.status}</TableCell>
                <TableCell>{formatCurrency(inv.total_amount)}</TableCell>
                <TableCell>{formatCurrency(inv.amount_due)}</TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <IconButton size="small" onClick={() => handleDownloadPdf(inv)}>
                      <FileDownloadIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleSendEmail(inv)}>
                      <EmailIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Invoice</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          <TextField
            select
            SelectProps={{ native: true }}
            label="Client"
            value={form.client_id}
            onChange={(e) => setForm({ ...form, client_id: Number(e.target.value) })}
          >
            <option value={0}>Select client</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </TextField>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField
              label="Issue Date"
              type="date"
              value={form.issue_date}
              onChange={(e) => setForm({ ...form, issue_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Due Date"
              type="date"
              value={form.due_date}
              onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Stack>
          <TextField
            label="Notes"
            value={form.notes || ""}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            multiline
            minRows={2}
          />

          <Typography variant="subtitle1">Line Items</Typography>
          {items.map((it, idx) => (
            <Stack key={idx} direction={{ xs: "column", sm: "row" }} spacing={1} sx={{ mb: 1 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="Service"
                value={it.service_id || ""}
                onChange={(e) =>
                  updateItem(idx, {
                    service_id: e.target.value ? Number(e.target.value) : undefined
                  })
                }
                sx={{ minWidth: 160 }}
              >
                <option value="">Custom</option>
                {services.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </TextField>
              <TextField
                label="Description"
                value={it.description}
                onChange={(e) => updateItem(idx, { description: e.target.value })}
                sx={{ flex: 1 }}
              />
              <TextField
                label="Qty"
                type="number"
                value={it.quantity}
                onChange={(e) => updateItem(idx, { quantity: Number(e.target.value) })}
                sx={{ width: 90 }}
              />
              <TextField
                label="Unit Price"
                type="number"
                value={it.unit_price}
                onChange={(e) => updateItem(idx, { unit_price: Number(e.target.value) })}
                sx={{ width: 120 }}
              />
              <TextField
                label="GST %"
                type="number"
                value={it.tax_rate_percent}
                onChange={(e) =>
                  updateItem(idx, { tax_rate_percent: Number(e.target.value) })
                }
                sx={{ width: 100 }}
              />
              <Button onClick={() => removeItem(idx)}>Remove</Button>
            </Stack>
          ))}
          <Button onClick={addItem}>Add Item</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={saving}>
            {saving ? "Creating..." : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InvoicesPage;

