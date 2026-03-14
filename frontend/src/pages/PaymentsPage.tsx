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
import AddIcon from "@mui/icons-material/Add";

import { fetchPayments, createPayment } from "../api/payments";
import { fetchInvoices } from "../api/invoices";
import { fetchClients } from "../api/clients";
import type { Payment, PaymentCreate, PaymentAllocationCreate } from "../types/payment";
import type { Invoice } from "../types/invoice";
import type { Client } from "../types/client";
import { Loader } from "../components/common/Loader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { formatCurrency } from "../utils/format";

const defaultCompanyId = 1;
const defaultCurrencyId = 1;

const PaymentsPage: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState<Omit<PaymentCreate, "allocations">>({
    company_id: defaultCompanyId,
    client_id: 0,
    currency_id: defaultCurrencyId,
    payment_date: new Date().toISOString().slice(0, 10),
    amount: 0,
    payment_method: "bank_transfer",
    reference: "",
    notes: ""
  });
  const [allocations, setAllocations] = useState<PaymentAllocationCreate[]>([]);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, inv, cls] = await Promise.all([
        fetchPayments(),
        fetchInvoices(),
        fetchClients()
      ]);
      setPayments(p);
      setInvoices(inv);
      setClients(cls);
    } catch (err) {
      setError("Failed to load payments");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    const clientId = clients[0]?.id || 0;
    setForm({
      company_id: defaultCompanyId,
      client_id: clientId,
      currency_id: defaultCurrencyId,
      payment_date: new Date().toISOString().slice(0, 10),
      amount: 0,
      payment_method: "bank_transfer",
      reference: "",
      notes: ""
    });
    setAllocations([]);
    setDialogOpen(true);
  };

  const addAllocation = () => {
    setAllocations([
      ...allocations,
      {
        invoice_id: 0,
        allocated_amount: 0
      }
    ]);
  };

  const updateAllocation = (index: number, patch: Partial<PaymentAllocationCreate>) => {
    const copy = [...allocations];
    copy[index] = { ...copy[index], ...patch };
    setAllocations(copy);
  };

  const removeAllocation = (index: number) => {
    const copy = [...allocations];
    copy.splice(index, 1);
    setAllocations(copy);
  };

  const handleSubmit = async () => {
    if (!form.client_id || allocations.length === 0) {
      setError("Client and at least one allocation are required");
      return;
    }
    const payload: PaymentCreate = {
      ...form,
      allocations
    };
    try {
      setSaving(true);
      await createPayment(payload);
      setDialogOpen(false);
      await load();
    } catch (err) {
      setError("Failed to record payment. Please verify amounts and try again.");
    } finally {
      setSaving(false);
    }
  };

  const clientInvoices = invoices.filter(
    (inv) => inv.client_id === form.client_id && inv.amount_due > 0
  );

  if (loading) return <Loader />;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h5">Payments</Typography>
        <Button startIcon={<AddIcon />} onClick={openCreate}>
          Record Payment
        </Button>
      </Box>
      {error && <ErrorAlert message={error} />}

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Client</TableCell>
            <TableCell>Amount</TableCell>
            <TableCell>Method</TableCell>
            <TableCell>Reference</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {payments.map((p) => {
            const client = clients.find((c) => c.id === p.client_id);
            return (
              <TableRow key={p.id}>
                <TableCell>{p.payment_date}</TableCell>
                <TableCell>{client?.name || p.client_id}</TableCell>
                <TableCell>{formatCurrency(p.amount)}</TableCell>
                <TableCell>{p.payment_method}</TableCell>
                <TableCell>{p.reference}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Record Payment</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
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
            <TextField
              label="Payment Date"
              type="date"
              value={form.payment_date}
              onChange={(e) => setForm({ ...form, payment_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Stack>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField
              label="Amount"
              type="number"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })}
            />
            <TextField
              label="Method"
              value={form.payment_method}
              onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
            />
          </Stack>
          <TextField
            label="Reference"
            value={form.reference || ""}
            onChange={(e) => setForm({ ...form, reference: e.target.value })}
          />
          <TextField
            label="Notes"
            value={form.notes || ""}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            multiline
            minRows={2}
          />

          <Typography variant="subtitle1">Allocations</Typography>
          {allocations.map((a, idx) => (
            <Stack key={idx} direction={{ xs: "column", sm: "row" }} spacing={1} sx={{ mb: 1 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="Invoice"
                value={a.invoice_id}
                onChange={(e) =>
                  updateAllocation(idx, { invoice_id: Number(e.target.value) })
                }
                sx={{ minWidth: 200 }}
              >
                <option value={0}>Select invoice</option>
                {clientInvoices.map((inv) => (
                  <option key={inv.id} value={inv.id}>
                    {inv.invoice_number} (Due {inv.due_date}) – Due {inv.amount_due.toFixed(2)}
                  </option>
                ))}
              </TextField>
              <TextField
                label="Allocated Amount"
                type="number"
                value={a.allocated_amount}
                onChange={(e) =>
                  updateAllocation(idx, { allocated_amount: Number(e.target.value) })
                }
                sx={{ width: 160 }}
              />
              <IconButton onClick={() => removeAllocation(idx)}>
                <span>Remove</span>
              </IconButton>
            </Stack>
          ))}
          <Button onClick={addAllocation}>Add Allocation</Button>
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

export default PaymentsPage;

