import React, { useEffect, useState } from "react";
import { Box, Card, CardContent, Divider, Grid, Stack, Typography, List, ListItem, ListItemText } from "@mui/material";

import { fetchDashboardSummary, fetchMonthlyRevenue, fetchOutstandingInvoices } from "../api/dashboard";
import type { DashboardSummary, MonthlyRevenueItem, OutstandingInvoiceItem } from "../types/dashboard";
import { Loader } from "../components/common/Loader";
import { ErrorAlert } from "../components/common/ErrorAlert";
import { formatCurrency } from "../utils/format";

const StatCard: React.FC<{ label: string; value: string }> = ({ label, value }) => {
  return (
    <Card>
      <CardContent sx={{ py: 2.25 }}>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h6" sx={{ mt: 0.5 }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
};

const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [monthly, setMonthly] = useState<MonthlyRevenueItem[]>([]);
  const [outstanding, setOutstanding] = useState<OutstandingInvoiceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [s, m, o] = await Promise.all([
          fetchDashboardSummary(),
          fetchMonthlyRevenue(),
          fetchOutstandingInvoices()
        ]);
        setSummary(s);
        setMonthly(m);
        setOutstanding(o);
      } catch (err) {
        setError("Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <Loader />;
  if (error) return <ErrorAlert message={error} />;
  if (!summary) return null;

  return (
    <Stack spacing={2.5}>
      <Box>
        <Typography variant="h5">Dashboard</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Key billing metrics for your company.
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Total Revenue" value={formatCurrency(summary.total_revenue)} />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Total Invoices" value={String(summary.total_invoices)} />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Outstanding" value={formatCurrency(summary.total_outstanding)} />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard label="Total Paid" value={formatCurrency(summary.total_paid)} />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography variant="h6">Monthly Revenue</Typography>
                <Typography variant="body2" color="text.secondary">
                  Last few months of collected revenue.
                </Typography>
              </Stack>
              <Divider sx={{ my: 2 }} />
              {monthly.length === 0 ? (
                <Typography variant="body2">No data yet.</Typography>
              ) : (
                <Box sx={{ display: "flex", gap: 1.25, alignItems: "flex-end", overflowX: "auto", pb: 0.5 }}>
                  {monthly.map((m) => (
                    <Box key={`${m.year}-${m.month}`} sx={{ textAlign: "center" }}>
                      <Box
                        sx={{
                          width: 24,
                          height: Math.max(10, m.revenue / 100), // simple proportional bar
                          bgcolor: "primary.main",
                          mb: 1,
                          borderRadius: 1
                        }}
                      />
                      <Typography variant="caption">
                        {m.month}/{m.year % 100}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Stack spacing={1}>
                <Typography variant="h6">Outstanding Invoices</Typography>
                <Typography variant="body2" color="text.secondary">
                  Invoices with a remaining balance.
                </Typography>
              </Stack>
              <Divider sx={{ my: 2 }} />
              {outstanding.length === 0 ? (
                <Typography variant="body2">No outstanding invoices.</Typography>
              ) : (
                <List dense>
                  {outstanding.map((inv) => (
                    <ListItem key={inv.id}>
                      <ListItemText
                        primary={`${inv.invoice_number} - ${inv.client_name}`}
                        secondary={`Due: ${inv.due_date} • Amount due: ${formatCurrency(inv.amount_due)}`}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  );
};

export default DashboardPage;

