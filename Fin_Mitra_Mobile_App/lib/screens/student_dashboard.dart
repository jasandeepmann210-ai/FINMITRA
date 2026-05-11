import 'package:flutter/material.dart';
import '../config.dart';
import '../helpers/api_helper.dart';
import '../widgets/profile_tab.dart';
import '../widgets/fee_tab.dart';
import '../widgets/attendance_tab.dart';
import '../widgets/events_tab.dart';
import '../widgets/enquiry_tab.dart';
import 'login_screen.dart';
import 'report_card_tab.dart';
import 'class_stream_screen.dart';

class StudentDashboard extends StatefulWidget {
  final String studentName;
  final String schoolName;
  final String schoolFolder;
  final String schoolAddress;
  final String logoUrl;
  /// Parent login mobile — used for communication / enquiries API.
  final String parentMobile;
  /// Selected child's admission number — used for attendance filter.
  final String admissionNo;
  final List<Map<String, dynamic>> profileRows;
  final List<Map<String, dynamic>> feeRows;
  final List<Map<String, dynamic>> marksRows;

  const StudentDashboard({
    super.key,
    required this.studentName,
    required this.schoolName,
    required this.schoolFolder,
    required this.schoolAddress,
    required this.logoUrl,
    required this.parentMobile,
    required this.admissionNo,
    required this.profileRows,
    required this.feeRows,
    required this.marksRows,
  });

  @override
  State<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends State<StudentDashboard>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _sidebarOpen = true;
  bool _streamsExpanded = true;
  List<Map<String, dynamic>> _streams = [];
  List<Map<String, dynamic>> _attendanceRows = [];
  List<Map<String, dynamic>> _eventRows = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
    _loadSideData();
  }

  Future<void> _loadSideData() async {
    try {
      final s = await fetchCSV("", FILE_CLASSROOM_STREAMS);
      if (mounted) setState(() => _streams = s);
    } catch (_) {
      if (mounted) setState(() => _streams = []);
    }
    try {
      final a = await fetchCSV("", FILE_STUDENT_ATTENDANCE);
      if (mounted) {
        setState(() {
          _attendanceRows = filterAttendanceForChild(
            a,
            widget.studentName,
            widget.admissionNo,
          );
        });
      }
    } catch (_) {
      if (mounted) setState(() => _attendanceRows = []);
    }
    try {
      final e = await fetchCSV("", FILE_EVENTS);
      if (mounted) setState(() => _eventRows = filterValidEvents(e));
    } catch (_) {
      if (mounted) setState(() => _eventRows = []);
    }
  }

  String _streamClassLabel(Map<String, dynamic> row) {
    return row["Class"]?.toString().trim() ??
        row["class"]?.toString().trim() ??
        "?";
  }

  String _streamUrl(Map<String, dynamic> row) {
    return row["URL"]?.toString().trim() ??
        row["url"]?.toString().trim() ??
        "";
  }

  void _openStream(Map<String, dynamic> row) {
    final url = _streamUrl(row);
    if (url.isEmpty) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ClassStreamScreen(
          classLabel: _streamClassLabel(row),
          streamUrl: url,
        ),
      ),
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Widget _buildSidePanel() {
    return Container(
      width: 280,
      color: Colors.white,
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.only(top: 8, left: 8, right: 8),
          children: [
            Text(
              "Quick links",
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 8),
            ListTile(
              dense: true,
              leading: const Icon(Icons.event_available, size: 22),
              title: const Text("Attendance"),
              onTap: () {
                setState(() => _sidebarOpen = false);
                _tabController.animateTo(3);
              },
            ),
            ListTile(
              dense: true,
              leading: const Icon(Icons.calendar_month, size: 22),
              title: const Text("Holidays & events"),
              onTap: () {
                setState(() => _sidebarOpen = false);
                _tabController.animateTo(4);
              },
            ),
            ListTile(
              dense: true,
              leading: const Icon(Icons.forum, size: 22),
              title: const Text("Communication"),
              onTap: () {
                setState(() => _sidebarOpen = false);
                _tabController.animateTo(5);
              },
            ),
            const Divider(),
            ExpansionTile(
              initiallyExpanded: _streamsExpanded,
              onExpansionChanged: (v) => setState(() => _streamsExpanded = v),
              title: const Text(
                "Live classroom streams",
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
              ),
              leading: const Icon(Icons.live_tv, color: Colors.redAccent),
              children: _streams.isEmpty
                  ? [
                      Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(
                          "No stream URLs configured.",
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                      ),
                    ]
                  : _streams.map((row) {
                      final label = _streamClassLabel(row);
                      final url = _streamUrl(row);
                      if (url.isEmpty) return const SizedBox.shrink();
                      return ListTile(
                        dense: true,
                        title: Text("Class $label"),
                        trailing: const Icon(Icons.play_circle_outline),
                        onTap: () => _openStream(row),
                      );
                    }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      appBar: AppBar(
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: Icon(_sidebarOpen ? Icons.menu_open : Icons.menu),
          tooltip: _sidebarOpen ? "Hide side panel" : "Show side panel",
          onPressed: () => setState(() => _sidebarOpen = !_sidebarOpen),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.studentName,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Text(
              widget.schoolName,
              style: const TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: "Logout",
            onPressed: () => Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const LoginScreen()),
            ),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(icon: Icon(Icons.person), text: "Profile"),
            Tab(icon: Icon(Icons.receipt_long), text: "Fee"),
            Tab(icon: Icon(Icons.grade), text: "Report"),
            Tab(icon: Icon(Icons.event_available), text: "Attendance"),
            Tab(icon: Icon(Icons.calendar_month), text: "Events"),
            Tab(icon: Icon(Icons.forum), text: "Enquiry"),
          ],
        ),
      ),
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 220),
            curve: Curves.easeInOut,
            width: _sidebarOpen ? 280 : 0,
            child: _sidebarOpen
                ? Material(
                    elevation: 2,
                    child: _buildSidePanel(),
                  )
                : const SizedBox.shrink(),
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                ProfileTab(rows: widget.profileRows),
                FeeTab(rows: widget.feeRows),
                ReportCardTab(
                  marksRows: widget.marksRows,
                  schoolName: widget.schoolName,
                  schoolAddress: widget.schoolAddress,
                  logoUrl: widget.logoUrl,
                ),
                AttendanceTab(rows: _attendanceRows),
                EventsTab(rows: _eventRows),
                EnquiryTab(
                  parentMobile: widget.parentMobile,
                  studentName: widget.studentName,
                  admissionNo: widget.admissionNo,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
