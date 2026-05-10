import 'package:flutter/material.dart';

class DataTab extends StatelessWidget {
  final List<Map<String, dynamic>> rows;
  final String emptyMessage;

  const DataTab({super.key, required this.rows, required this.emptyMessage});

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.inbox, size: 48, color: Colors.grey.shade400),
            const SizedBox(height: 12),
            Text(emptyMessage, style: TextStyle(color: Colors.grey.shade600)),
          ],
        ),
      );
    }

    final columns = rows.first.keys.toList();

    return Padding(
      padding: const EdgeInsets.all(12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: SingleChildScrollView(
          child: DataTable(
            headingRowColor: WidgetStateProperty.all(Colors.blue.shade100),
            border: TableBorder.all(color: Colors.blue.shade100, width: 0.5),
            columnSpacing: 20,
            columns: columns
                .map((col) => DataColumn(
                      label: Text(col,
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 13)),
                    ))
                .toList(),
            rows: rows
                .map((row) => DataRow(
                      cells: columns
                          .map((col) => DataCell(
                                Text(row[col]?.toString() ?? "",
                                    style: const TextStyle(fontSize: 13)),
                              ))
                          .toList(),
                    ))
                .toList(),
          ),
        ),
      ),
    );
  }
}
