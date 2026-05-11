import 'package:flutter/material.dart';
import '../helpers/enquiry_api.dart';

class EnquiryTab extends StatefulWidget {
  final String parentMobile;
  final String studentName;
  final String admissionNo;

  const EnquiryTab({
    super.key,
    required this.parentMobile,
    required this.studentName,
    required this.admissionNo,
  });

  @override
  State<EnquiryTab> createState() => _EnquiryTabState();
}

class _EnquiryTabState extends State<EnquiryTab> {
  final _messageController = TextEditingController();
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  String? _error;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _reload() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await fetchEnquiries(widget.parentMobile);
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

  Future<void> _submit() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;
    setState(() => _submitting = true);
    try {
      await postEnquiry(
        parentMobile: widget.parentMobile,
        studentName: widget.studentName,
        admissionNo: widget.admissionNo,
        message: text,
      );
      _messageController.clear();
      await _reload();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Could not send: $e")),
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
          child: TextField(
            controller: _messageController,
            minLines: 2,
            maxLines: 4,
            decoration: InputDecoration(
              labelText: "Your question / enquiry",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(12),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _submitting ? null : _submit,
              icon: _submitting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.send),
              label: Text(_submitting ? "Sending…" : "Send to school"),
            ),
          ),
        ),
        const Divider(),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _reload,
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? ListView(
                        children: [
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: Text(_error!, style: const TextStyle(color: Colors.red)),
                          ),
                        ],
                      )
                    : _items.isEmpty
                        ? ListView(
                            children: const [
                              SizedBox(height: 48),
                              Center(child: Text("No messages yet. School will reply here.")),
                            ],
                          )
                        : ListView.separated(
                            padding: const EdgeInsets.all(12),
                            itemCount: _items.length,
                            separatorBuilder: (_, __) => const SizedBox(height: 8),
                            itemBuilder: (context, i) {
                              final e = _items[i];
                              final msg = e["message"]?.toString() ?? "";
                              final reply = e["reply"]?.toString();
                              final created = e["created_at"]?.toString() ?? "";
                              return Card(
                                child: Padding(
                                  padding: const EdgeInsets.all(12),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(created,
                                          style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                                      const SizedBox(height: 6),
                                      Text(msg, style: const TextStyle(fontSize: 15)),
                                      if (reply != null && reply.isNotEmpty) ...[
                                        const SizedBox(height: 10),
                                        Container(
                                          width: double.infinity,
                                          padding: const EdgeInsets.all(10),
                                          decoration: BoxDecoration(
                                            color: Colors.green.shade50,
                                            borderRadius: BorderRadius.circular(8),
                                            border: Border.all(color: Colors.green.shade200),
                                          ),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text("School reply",
                                                  style: TextStyle(
                                                    fontWeight: FontWeight.bold,
                                                    color: Colors.green.shade800,
                                                    fontSize: 12,
                                                  )),
                                              const SizedBox(height: 4),
                                              Text(reply),
                                            ],
                                          ),
                                        ),
                                      ] else
                                        Padding(
                                          padding: const EdgeInsets.only(top: 8),
                                          child: Text(
                                            "Awaiting reply from school…",
                                            style: TextStyle(
                                              fontSize: 12,
                                              fontStyle: FontStyle.italic,
                                              color: Colors.grey.shade600,
                                            ),
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
          ),
        ),
      ],
    );
  }
}
