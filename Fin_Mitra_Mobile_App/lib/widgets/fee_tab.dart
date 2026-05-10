import 'package:flutter/material.dart';

class FeeTab extends StatelessWidget {
  final List<Map<String, dynamic>> rows;

  const FeeTab({super.key, required this.rows});

  // Parse breakup dict string like "{'Admission Fees': 3500.0, 'Tuition Fees': 500.0}"
  Map<String, String> _parseBreakup(Map<String, dynamic> row) {
    final breakupKeys = [
      "breakup_cash", "breakup_bank1", "breakup_bank2", "breakup_bank3",
      "breakup_bank4", "breakup_bank5", "breakup_bank6", "breakup_bank7",
      "breakup_bank8", "breakup_bank9", "breakup_bank10",
    ];

    final result = <String, String>{};
    for (final key in breakupKeys) {
      final val = row[key]?.toString().trim() ?? "{}";
      if (val == "{}" || val.isEmpty) continue;
      // Parse "{'Admission Fees': 3500.0, 'Tuition Fees': 500.0}"
      final cleaned = val.replaceAll("{", "").replaceAll("}", "").replaceAll("'", "");
      for (final pair in cleaned.split(",")) {
        final parts = pair.split(":");
        if (parts.length == 2) {
          final feeType = parts[0].trim();
          final amount  = parts[1].trim();
          if (feeType.isNotEmpty && amount != "0.0") {
            result[feeType] = "₹$amount";
          }
        }
      }
    }
    return result;
  }

  // Determine payment mode from which bank/cash column is non-zero
  String _paymentMode(Map<String, dynamic> row) {
    final cash = double.tryParse(row["cash_amount"]?.toString() ?? "0") ?? 0;
    if (cash > 0) return "Cash";
    for (int i = 1; i <= 10; i++) {
      final bank = double.tryParse(row["bank${i}_amount"]?.toString() ?? "0") ?? 0;
      if (bank > 0) return "Bank";
    }
    return "-";
  }

  // Total across all rows
  double _grandTotal() {
    return rows.fold(0.0, (sum, row) =>
        sum + (double.tryParse(row["total_amount"]?.toString() ?? "0") ?? 0));
  }

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.receipt_long, size: 48, color: Colors.grey.shade400),
            const SizedBox(height: 12),
            Text("No fee records found.", style: TextStyle(color: Colors.grey.shade600)),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [

          // ── Grand Total Card ──
          Card(
            elevation: 3,
            color: Colors.blue.shade700,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Total Fees Paid",
                          style: TextStyle(color: Colors.white70, fontSize: 13)),
                      SizedBox(height: 4),
                      Text("All Transactions",
                          style: TextStyle(color: Colors.white54, fontSize: 12)),
                    ],
                  ),
                  Text(
                    "₹${_grandTotal().toStringAsFixed(0)}",
                    style: const TextStyle(
                        color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // ── Individual Receipt Cards ──
          ...rows.map((row) {
            final date    = row["transaction_date"]?.toString() ?? "-";
            final total   = row["total_amount"]?.toString() ?? "0";
            final details = row["details"]?.toString() ?? "";
            final mode    = _paymentMode(row);
            final breakup = _parseBreakup(row);

            return Card(
              elevation: 2,
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [

                    // Date + Amount
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.calendar_today,
                                size: 14, color: Colors.grey.shade500),
                            const SizedBox(width: 6),
                            Text(date,
                                style: TextStyle(color: Colors.grey.shade600,
                                    fontSize: 13)),
                          ],
                        ),
                        Text("₹$total",
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold,
                                color: Colors.green)),
                      ],
                    ),
                    const SizedBox(height: 8),

                    // Payment mode badge
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                      decoration: BoxDecoration(
                        color: mode == "Cash"
                            ? Colors.orange.shade50
                            : Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: mode == "Cash"
                              ? Colors.orange.shade200
                              : Colors.blue.shade200,
                        ),
                      ),
                      child: Text(mode,
                          style: TextStyle(
                              fontSize: 11,
                              color: mode == "Cash"
                                  ? Colors.orange.shade700
                                  : Colors.blue.shade700,
                              fontWeight: FontWeight.w600)),
                    ),
                    const SizedBox(height: 10),

                    // Fee Breakup
                    if (breakup.isNotEmpty) ...[
                      const Text("Fee Breakup",
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold,
                              color: Colors.black54)),
                      const SizedBox(height: 6),
                      ...breakup.entries.map((e) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(e.key,
                                    style: const TextStyle(fontSize: 13)),
                                Text(e.value,
                                    style: const TextStyle(
                                        fontSize: 13, fontWeight: FontWeight.w500)),
                              ],
                            ),
                          )),
                    ],

                    // Details
                    if (details.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(details,
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade500,
                              fontStyle: FontStyle.italic)),
                    ],
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
