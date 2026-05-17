import 'package:flutter/material.dart';
import '../helpers/api_helper.dart';
import '../helpers/notification_api.dart';

class NotificationsTab extends StatefulWidget {
  final String parentMobile;
  final String classCode;

  const NotificationsTab({
    super.key,
    required this.parentMobile,
    required this.classCode,
  });

  @override
  State<NotificationsTab> createState() => _NotificationsTabState();
}

class _NotificationsTabState extends State<NotificationsTab> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  Future<void> _reload() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await fetchParentNotifications(
        parentMobile: widget.parentMobile,
        classCode: widget.classCode,
      );
      if (mounted) {
        setState(() {
          _items = list;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(child: Text(_error!, style: const TextStyle(color: Colors.red)));
    }

    return RefreshIndicator(
      onRefresh: _reload,
      child: _items.isEmpty
          ? ListView(
              children: const [
                SizedBox(height: 64),
                Center(child: Text("No announcements yet.")),
              ],
            )
          : ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: _items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, i) {
                final n = _items[i];
                final scope = n["scope"]?.toString() ?? "";
                final isAll = scope == "all";
                final cc = n["class_code"]?.toString() ?? "";
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              isAll ? Icons.campaign : Icons.class_,
                              color: isAll ? Colors.indigo : Colors.teal,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                n["title"]?.toString() ?? "",
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                            ),
                            Chip(
                              label: Text(
                                isAll ? "All parents" : displayClassCode(cc),
                                style: const TextStyle(fontSize: 10),
                              ),
                              visualDensity: VisualDensity.compact,
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(n["message"]?.toString() ?? ""),
                        const SizedBox(height: 8),
                        Text(
                          "From ${n["posted_by"] ?? "School"} · ${n["created_at"]?.toString().substring(0, 16) ?? ""}",
                          style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
