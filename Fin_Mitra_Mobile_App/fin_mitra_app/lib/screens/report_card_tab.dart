import 'package:flutter/material.dart';

class ReportCardTab extends StatelessWidget {
  final List<Map<String, dynamic>> marksRows;
  final String schoolName;
  final String schoolAddress;
  final String logoUrl;

  const ReportCardTab({
    super.key,
    required this.marksRows,
    required this.schoolName,
    required this.schoolAddress,
    required this.logoUrl,
  });

  // Extract subjects dynamically from column names
  List<String> _getSubjects(Map<String, dynamic> row) {
    final subjects = <String>{};
    for (final key in row.keys) {
      if (key.endsWith("_Final") && !key.endsWith("_status")) {
        subjects.add(key.replaceAll("_Final", ""));
      }
    }
    return subjects.toList();
  }

  @override
  Widget build(BuildContext context) {
    if (marksRows.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.grade, size: 48, color: Colors.grey.shade400),
            const SizedBox(height: 12),
            Text("No marks found.", style: TextStyle(color: Colors.grey.shade600)),
          ],
        ),
      );
    }

    final row = marksRows.first;
    final subjects = _getSubjects(row);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [

              // ── Header: Logo + School Info ──
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Image.network(
                    logoUrl,
                    height: 60,
                    errorBuilder: (_, _, _) =>
                        Icon(Icons.school, size: 60, color: Colors.blue.shade700),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(schoolName,
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center),
              Text(schoolAddress,
                  style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  textAlign: TextAlign.center),
              const SizedBox(height: 8),
              const Text("REPORT CARD",
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold,
                      letterSpacing: 2)),
              const Divider(thickness: 2),

              // ── Student Info ──
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(child: _infoRow("Name", row["student_name"]?.toString() ?? "")),
                  Expanded(child: _infoRow("Roll No", row["roll"]?.toString() ?? "")),
                ],
              ),
              Row(
                children: [
                  Expanded(child: _infoRow("Section", row["section"]?.toString() ?? "")),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(),

              // ── Marks Table ──
              const SizedBox(height: 8),
              Table(
                border: TableBorder.all(color: Colors.grey.shade300),
                columnWidths: const {
                  0: FlexColumnWidth(2),
                  1: FlexColumnWidth(1.5),
                  2: FlexColumnWidth(1.5),
                  3: FlexColumnWidth(1.2),
                },
                children: [
                  // Header row
                  TableRow(
                    decoration: BoxDecoration(color: Colors.blue.shade100),
                    children: const [
                      _TableCell("Subject", isHeader: true),
                      _TableCell("HY", isHeader: true),
                      _TableCell("Final", isHeader: true),
                      _TableCell("Total", isHeader: true),
                    ],
                  ),
                  // Subject rows
                  ...subjects.map((subject) {
                    final hy      = row["${subject}_HY"]?.toString() ?? "-";
                    final hyStatus = row["${subject}_HY_status"]?.toString() ?? "";
                    final fin     = row["${subject}_Final"]?.toString() ?? "-";
                    final finStatus = row["${subject}_Final_status"]?.toString() ?? "";
                    final hyVal   = double.tryParse(hy) ?? 0;
                    final finVal  = double.tryParse(fin) ?? 0;
                    final total   = (hyVal + finVal).toStringAsFixed(1);

                    return TableRow(
                      children: [
                        _TableCell(subject),
                        _TableCell("$hy (${hyStatus[0]})"),
                        _TableCell("$fin (${finStatus[0]})"),
                        _TableCell(total),
                      ],
                    );
                  }),
                ],
              ),

              const SizedBox(height: 16),
              const Divider(),

              // ── Summary ──
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _summaryBox("Total Obtained", row["total_marks"]?.toString() ?? "-"),
                  _summaryBox("Maximum Marks", row["max_marks"]?.toString() ?? "-"),
                  _summaryBox("Percentage", "${row["percentage"]?.toString() ?? "-"}%"),
                ],
              ),

              const SizedBox(height: 24),
              const Divider(),

              // ── Signatures ──
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: const [
                  _SignatureBox("Class Teacher"),
                  _SignatureBox("Exam Incharge"),
                  _SignatureBox("Principal"),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(fontSize: 13, color: Colors.black87),
          children: [
            TextSpan(text: "$label: ", style: const TextStyle(fontWeight: FontWeight.bold)),
            TextSpan(text: value),
          ],
        ),
      ),
    );
  }

  Widget _summaryBox(String label, String value) {
    return Column(
      children: [
        Text(value,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        Text(label,
            style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
      ],
    );
  }
}

class _TableCell extends StatelessWidget {
  final String text;
  final bool isHeader;
  const _TableCell(this.text, {this.isHeader = false});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 13,
          fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}

class _SignatureBox extends StatelessWidget {
  final String label;
  const _SignatureBox(this.label);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(width: 80, height: 1, color: Colors.black),
        const SizedBox(height: 4),
        Text(label,
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
