import 'package:flutter/material.dart';
import '../helpers/enquiry_api.dart';
import 'teacher_login_screen.dart';

class TeacherEnquiriesScreen extends StatefulWidget {
  final String classCode;
  final String pin;
  final String teacherName;

  const TeacherEnquiriesScreen({
    super.key,
    required this.classCode,
    required this.pin,
    required this.teacherName,
  });

  @override
  State<TeacherEnquiriesScreen> createState() => _TeacherEnquiriesScreenState();
}

class _TeacherEnquiriesScreenState extends State<TeacherEnquiriesScreen> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  String _filter = "all";
  int _openCount = 0;
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
      final data = await fetchTeacherEnquiries(
        classCode: widget.classCode,
        pin: widget.pin,
        status: _filter,
      );
      if (mounted) {
        setState(() {
          _items = List<Map<String, dynamic>>.from(data["enquiries"] ?? []);
          _openCount = data["open_count"] as int? ?? 0;
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

  Future<void> _showReplySheet(Map<String, dynamic> enquiry) async {
    final controller = TextEditingController();
    final id = enquiry["id"]?.toString() ?? "";
    final parentMsg = enquiry["message"]?.toString() ?? "";

    final sent = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                "Reply to ${enquiry["student_name"] ?? "parent"}",
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                "Parent wrote: \"$parentMsg\"",
                style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: controller,
                minLines: 3,
                maxLines: 6,
                decoration: InputDecoration(
                  labelText: "Your reply",
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () async {
                  final text = controller.text.trim();
                  if (text.isEmpty) return;
                  try {
                    await replyToEnquiry(
                      enquiryId: id,
                      classCode: widget.classCode,
                      pin: widget.pin,
                      reply: text,
                    );
                    if (ctx.mounted) Navigator.pop(ctx, true);
                  } catch (e) {
                    if (ctx.mounted) {
                      ScaffoldMessenger.of(ctx).showSnackBar(
                        SnackBar(content: Text("$e")),
                      );
                    }
                  }
                },
                child: const Text("Send reply to parent"),
              ),
            ],
          ),
        );
      },
    );

    if (sent == true) await _reload();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Class ${widget.classCode}"),
            Text(
              widget.teacherName,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        backgroundColor: Colors.teal.shade700,
        foregroundColor: Colors.white,
        actions: [
          if (_openCount > 0)
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 8),
                child: Chip(
                  label: Text("$_openCount open"),
                  backgroundColor: Colors.orange.shade100,
                  labelStyle: TextStyle(fontSize: 11, color: Colors.orange.shade900),
                ),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (_) => const TeacherLoginScreen()),
              (_) => false,
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: [
                _FilterChip("all", "All", _filter, (v) {
                  setState(() => _filter = v);
                  _reload();
                }),
                _FilterChip("open", "Pending", _filter, (v) {
                  setState(() => _filter = v);
                  _reload();
                }),
                _FilterChip("answered", "Answered", _filter, (v) {
                  setState(() => _filter = v);
                  _reload();
                }),
              ],
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: _reload,
              child: _buildBody(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return ListView(
        children: [Padding(padding: const EdgeInsets.all(16), child: Text(_error!))],
      );
    }
    if (_items.isEmpty) {
      return ListView(
        children: const [
          SizedBox(height: 64),
          Center(child: Text("No enquiries for this class.")),
        ],
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: _items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        final e = _items[i];
        final answered = (e["reply"]?.toString() ?? "").isNotEmpty;
        return Card(
          child: ListTile(
            title: Text(e["student_name"]?.toString() ?? "Student"),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text(e["message"]?.toString() ?? ""),
                const SizedBox(height: 4),
                Text(
                  "Parent: ${e["parent_mobile"] ?? ""}",
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                ),
                if (answered) ...[
                  const SizedBox(height: 8),
                  Text(
                    "Your reply: ${e["reply"]}",
                    style: TextStyle(fontSize: 12, color: Colors.green.shade800),
                  ),
                ],
              ],
            ),
            isThreeLine: true,
            trailing: answered
                ? Icon(Icons.check_circle, color: Colors.green.shade600)
                : FilledButton(
                    onPressed: () => _showReplySheet(e),
                    child: const Text("Reply"),
                  ),
            onTap: answered ? null : () => _showReplySheet(e),
          ),
        );
      },
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String value;
  final String label;
  final String selected;
  final ValueChanged<String> onSelected;

  const _FilterChip(this.value, this.label, this.selected, this.onSelected);

  @override
  Widget build(BuildContext context) {
    final isSelected = selected == value;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => onSelected(value),
      ),
    );
  }
}
