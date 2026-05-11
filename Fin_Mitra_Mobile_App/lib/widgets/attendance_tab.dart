import 'package:flutter/material.dart';

class AttendanceTab extends StatelessWidget {
  final List<Map<String, dynamic>> rows;

  const AttendanceTab({super.key, required this.rows});

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) {
      return Center(
        child: Text(
          "No attendance records found for this student.",
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey.shade700),
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: rows.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, i) {
        final r = rows[i];
        final date = r["date"]?.toString() ?? "";
        final status = r["status"]?.toString() ?? "";
        final cls = r["class"]?.toString() ?? "";
        Color chipColor;
        switch (status.toLowerCase()) {
          case "present":
            chipColor = Colors.green.shade100;
            break;
          case "absent":
            chipColor = Colors.red.shade100;
            break;
          case "holiday":
            chipColor = Colors.amber.shade100;
            break;
          default:
            chipColor = Colors.grey.shade200;
        }
        return ListTile(
          title: Text(date, style: const TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text("Class: $cls"),
          trailing: Chip(
            label: Text(status),
            backgroundColor: chipColor,
          ),
        );
      },
    );
  }
}
