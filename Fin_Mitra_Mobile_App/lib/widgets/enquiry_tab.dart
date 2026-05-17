import 'package:flutter/material.dart';
import '../helpers/api_helper.dart';
import '../helpers/enquiry_api.dart';

class EnquiryTab extends StatefulWidget {
  final String parentMobile;
  final String studentName;
  final String studentId;
  final String admissionNo;
  final String classCode;
  final String? assignedTeacher;

  const EnquiryTab({
    super.key,
    required this.parentMobile,
    required this.studentName,
    required this.studentId,
    required this.admissionNo,
    required this.classCode,
    this.assignedTeacher,
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
      final list = await fetchEnquiries(
        parentMobile: widget.parentMobile,
        studentId: widget.studentId,
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

  Future<void> _submit() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;
    if (widget.classCode.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Class not assigned for this student.")),
      );
      return;
    }
    setState(() => _submitting = true);
    try {
      await postEnquiry(
        parentMobile: widget.parentMobile,
        studentName: widget.studentName,
        studentId: widget.studentId,
        admissionNo: widget.admissionNo,
        classCode: widget.classCode,
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
    final teacherLabel = widget.assignedTeacher?.isNotEmpty == true
        ? widget.assignedTeacher!
        : "Class ${widget.classCode} teacher";

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          margin: const EdgeInsets.fromLTRB(12, 12, 12, 0),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.teal.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.teal.shade100),
          ),
          child: Row(
            children: [
              Icon(Icons.class_, color: Colors.teal.shade700),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Class ${displayClassCode(widget.classCode)}",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.teal.shade900,
                      ),
                    ),
                    Text(
                      "Your message goes to $teacherLabel",
                      style: TextStyle(fontSize: 12, color: Colors.teal.shade800),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
          child: TextField(
            controller: _messageController,
            minLines: 2,
            maxLines: 4,
            decoration: InputDecoration(
              labelText: "Ask your class teacher",
              hintText: "Homework, attendance, fees, transport…",
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(12),
          child: FilledButton.icon(
            onPressed: _submitting ? null : _submit,
            icon: _submitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.send),
            label: Text(_submitting ? "Sending…" : "Send to class teacher"),
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _reload,
            child: _buildList(),
          ),
        ),
      ],
    );
  }

  Widget _buildList() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return ListView(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(_error!, style: const TextStyle(color: Colors.red)),
          ),
        ],
      );
    }
    if (_items.isEmpty) {
      return ListView(
        children: [
          const SizedBox(height: 48),
          Center(
            child: Column(
              children: [
                Icon(Icons.forum_outlined, size: 48, color: Colors.grey.shade400),
                const SizedBox(height: 8),
                Text(
                  "No messages yet",
                  style: TextStyle(color: Colors.grey.shade700, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  "Class teacher will reply here",
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: _items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (context, i) => _EnquiryCard(item: _items[i]),
    );
  }
}

class _EnquiryCard extends StatelessWidget {
  final Map<String, dynamic> item;
  const _EnquiryCard({required this.item});

  @override
  Widget build(BuildContext context) {
    final msg = item["message"]?.toString() ?? "";
    final reply = item["reply"]?.toString();
    final answered = reply != null && reply.isNotEmpty;
    final created = item["created_at"]?.toString() ?? "";
    final teacher = item["replied_by"]?.toString() ?? item["assigned_teacher"]?.toString() ?? "";

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                _StatusChip(answered: answered),
                const Spacer(),
                Text(
                  created.length > 16 ? created.substring(0, 16) : created,
                  style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text("You asked", style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
            const SizedBox(height: 4),
            Text(msg, style: const TextStyle(fontSize: 15)),
            const SizedBox(height: 12),
            if (answered) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      teacher.isNotEmpty ? "Reply from $teacher" : "Class teacher reply",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.green.shade800,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(reply, style: const TextStyle(fontSize: 14)),
                  ],
                ),
              ),
            ] else
              Row(
                children: [
                  Icon(Icons.hourglass_empty, size: 16, color: Colors.orange.shade700),
                  const SizedBox(width: 6),
                  Text(
                    "Waiting for class teacher reply…",
                    style: TextStyle(
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                      color: Colors.orange.shade800,
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final bool answered;
  const _StatusChip({required this.answered});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: answered ? Colors.green.shade100 : Colors.orange.shade100,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        answered ? "Answered" : "Pending",
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: answered ? Colors.green.shade900 : Colors.orange.shade900,
        ),
      ),
    );
  }
}
