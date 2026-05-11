import 'package:flutter/material.dart';
import '../screens/class_stream_screen.dart';

class LiveStreamsTab extends StatelessWidget {
  final List<Map<String, dynamic>> rows;

  const LiveStreamsTab({super.key, required this.rows});

  String _classLabel(Map<String, dynamic> row) {
    return row["Class"]?.toString().trim() ??
        row["class"]?.toString().trim() ??
        "?";
  }

  String _streamUrl(Map<String, dynamic> row) {
    return row["URL"]?.toString().trim() ?? row["url"]?.toString().trim() ?? "";
  }

  @override
  Widget build(BuildContext context) {
    final available = rows.where((r) => _streamUrl(r).isNotEmpty).toList();
    if (available.isEmpty) {
      return Center(
        child: Text(
          "No classroom streams configured.",
          style: TextStyle(color: Colors.grey.shade700),
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: available.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, i) {
        final row = available[i];
        final label = _classLabel(row);
        final url = _streamUrl(row);
        return ListTile(
          leading: CircleAvatar(
            backgroundColor: Colors.red.shade50,
            child: Icon(Icons.live_tv, color: Colors.red.shade700),
          ),
          title: Text("Class $label"),
          subtitle: Text(
            "Tap to open live stream",
            style: TextStyle(color: Colors.grey.shade600),
          ),
          trailing: const Icon(Icons.open_in_new),
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ClassStreamScreen(classLabel: label, streamUrl: url),
            ),
          ),
        );
      },
    );
  }
}
