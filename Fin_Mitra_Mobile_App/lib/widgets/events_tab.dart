import 'package:flutter/material.dart';

class EventsTab extends StatelessWidget {
  final List<Map<String, dynamic>> rows;

  const EventsTab({super.key, required this.rows});

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) {
      return Center(
        child: Text(
          "No holidays or events listed yet.",
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
        final name = r["event"]?.toString() ?? "";
        final date = r["date"]?.toString() ?? "";
        return ListTile(
          leading: CircleAvatar(
            backgroundColor: Colors.blue.shade100,
            child: Icon(Icons.event, color: Colors.blue.shade800),
          ),
          title: Text(name, style: const TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text(date),
        );
      },
    );
  }
}
