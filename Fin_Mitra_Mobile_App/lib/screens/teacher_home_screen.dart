import 'package:flutter/material.dart';
import '../helpers/enquiry_api.dart';
import '../helpers/notification_api.dart';
import 'teacher_login_screen.dart';

class TeacherHomeScreen extends StatefulWidget {
  final String classCode;
  final String pin;
  final String teacherName;
  final bool isAdmin;

  const TeacherHomeScreen({
    super.key,
    required this.classCode,
    required this.pin,
    required this.teacherName,
    required this.isAdmin,
  });

  @override
  State<TeacherHomeScreen> createState() => _TeacherHomeScreenState();
}

class _TeacherHomeScreenState extends State<TeacherHomeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.isAdmin ? "Admin portal" : "Class ${widget.classCode}"),
            Text(
              widget.teacherName,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        backgroundColor: Colors.teal.shade700,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabs,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: "Enquiries"),
            Tab(text: "Announcements"),
          ],
        ),
        actions: [
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
      body: TabBarView(
        controller: _tabs,
        children: [
          _TeacherEnquiriesPanel(
            classCode: widget.classCode,
            pin: widget.pin,
            isAdmin: widget.isAdmin,
          ),
          _TeacherAnnouncementsPanel(
            classCode: widget.classCode,
            pin: widget.pin,
            isAdmin: widget.isAdmin,
          ),
        ],
      ),
    );
  }
}

class _TeacherEnquiriesPanel extends StatefulWidget {
  final String classCode;
  final String pin;
  final bool isAdmin;

  const _TeacherEnquiriesPanel({
    required this.classCode,
    required this.pin,
    required this.isAdmin,
  });

  @override
  State<_TeacherEnquiriesPanel> createState() => _TeacherEnquiriesPanelState();
}

class _TeacherEnquiriesPanelState extends State<_TeacherEnquiriesPanel> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  Future<void> _reload() async {
    setState(() => _loading = true);
    try {
      final data = await fetchTeacherEnquiries(
        classCode: widget.classCode,
        pin: widget.pin,
      );
      if (mounted) {
        setState(() {
          _items = List<Map<String, dynamic>>.from(data["enquiries"] ?? []);
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _reply(Map<String, dynamic> e) async {
    final controller = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text("Reply to ${e["student_name"]}"),
        content: TextField(controller: controller, minLines: 3, maxLines: 5),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Cancel")),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text("Send"),
          ),
        ],
      ),
    );
    if (ok == true && controller.text.trim().isNotEmpty) {
      await replyToEnquiry(
        enquiryId: e["id"]?.toString() ?? "",
        classCode: widget.classCode,
        pin: widget.pin,
        reply: controller.text.trim(),
      );
      await _reload();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    return RefreshIndicator(
      onRefresh: _reload,
      child: _items.isEmpty
          ? ListView(children: const [SizedBox(height: 48), Center(child: Text("No enquiries"))])
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _items.length,
              itemBuilder: (_, i) {
                final e = _items[i];
                final answered = (e["reply"]?.toString() ?? "").isNotEmpty;
                return Card(
                  child: ListTile(
                    title: Text("${e["student_name"]} · Class ${e["class_code"]}"),
                    subtitle: Text(e["message"]?.toString() ?? ""),
                    trailing: answered
                        ? const Icon(Icons.check, color: Colors.green)
                        : const Icon(Icons.reply),
                    onTap: answered ? null : () => _reply(e),
                  ),
                );
              },
            ),
    );
  }
}

class _TeacherAnnouncementsPanel extends StatefulWidget {
  final String classCode;
  final String pin;
  final bool isAdmin;

  const _TeacherAnnouncementsPanel({
    required this.classCode,
    required this.pin,
    required this.isAdmin,
  });

  @override
  State<_TeacherAnnouncementsPanel> createState() => _TeacherAnnouncementsPanelState();
}

class _TeacherAnnouncementsPanelState extends State<_TeacherAnnouncementsPanel> {
  final _titleCtrl = TextEditingController();
  final _msgCtrl = TextEditingController();
  final _classCtrl = TextEditingController();
  String _scope = "class";
  List<Map<String, dynamic>> _posted = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    if (widget.isAdmin) _scope = "all";
    _reload();
  }

  Future<void> _reload() async {
    setState(() => _loading = true);
    try {
      final list = await fetchTeacherNotifications(
        classCode: widget.classCode,
        pin: widget.pin,
      );
      if (mounted) {
        setState(() {
          _posted = list;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _post() async {
    try {
      await postNotification(
        classCode: widget.classCode,
        pin: widget.pin,
        title: _titleCtrl.text,
        message: _msgCtrl.text,
        scope: _scope,
        targetClassCode: _scope == "class" ? (_classCtrl.text.trim().isNotEmpty
            ? _classCtrl.text
            : widget.classCode) : null,
      );
      _titleCtrl.clear();
      _msgCtrl.clear();
      await _reload();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Announcement published")),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("$e")));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
            padding: const EdgeInsets.all(12),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      widget.isAdmin ? "Post school-wide or class notice" : "Post to your class parents",
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    if (widget.isAdmin) ...[
                      const SizedBox(height: 8),
                      SegmentedButton<String>(
                        segments: const [
                          ButtonSegment(value: "all", label: Text("All parents")),
                          ButtonSegment(value: "class", label: Text("One class")),
                        ],
                        selected: {_scope},
                        onSelectionChanged: (s) => setState(() => _scope = s.first),
                      ),
                    ],
                    if (widget.isAdmin && _scope == "class") ...[
                      const SizedBox(height: 8),
                      TextField(
                        controller: _classCtrl,
                        decoration: const InputDecoration(
                          labelText: "Target class code (e.g. 10B)",
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ],
                    const SizedBox(height: 8),
                    TextField(
                      controller: _titleCtrl,
                      decoration: const InputDecoration(
                        labelText: "Title",
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _msgCtrl,
                      minLines: 2,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: "Message",
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 8),
                    FilledButton(
                      onPressed: _post,
                      child: const Text("Publish announcement"),
                    ),
                  ],
                ),
              ),
            ),
        ),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _reload,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _posted.length,
                    itemBuilder: (_, i) {
                      final n = _posted[i];
                      return ListTile(
                        title: Text(n["title"]?.toString() ?? ""),
                        subtitle: Text(n["message"]?.toString() ?? ""),
                        trailing: Chip(
                          label: Text(n["scope"]?.toString() ?? ""),
                          visualDensity: VisualDensity.compact,
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
