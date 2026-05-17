import 'package:flutter/material.dart';
import '../config.dart';
import '../helpers/api_helper.dart';
import '../widgets/profile_tab.dart';
import '../widgets/fee_tab.dart';
import '../widgets/attendance_calendar_tab.dart';
import '../widgets/events_calendar_tab.dart';
import '../widgets/notifications_tab.dart';
import '../widgets/live_streams_tab.dart';
import '../widgets/enquiry_tab.dart';
import '../widgets/bus_tracking_tab.dart';
import 'login_screen.dart';
import 'report_card_tab.dart';

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
  final String studentId;
  final String classCode;
  final String? assignedTeacher;
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
    required this.studentId,
    required this.classCode,
    this.assignedTeacher,
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
  List<Map<String, dynamic>> _streams = [];
  List<Map<String, dynamic>> _attendanceRows = [];
  List<Map<String, dynamic>> _eventRows = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 9, vsync: this);
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

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      appBar: AppBar(
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        leading: Navigator.canPop(context)
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                tooltip: "Choose another child",
                onPressed: () => Navigator.pop(context),
              )
            : null,
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
            Tab(icon: Icon(Icons.live_tv), text: "Streams"),
            Tab(icon: Icon(Icons.forum), text: "Enquiry"),
            Tab(icon: Icon(Icons.notifications), text: "Notices"),
            Tab(icon: Icon(Icons.directions_bus), text: "Bus"),
          ],
        ),
      ),
      body: TabBarView(
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
          AttendanceCalendarTab(rows: _attendanceRows),
          EventsCalendarTab(rows: _eventRows),
          LiveStreamsTab(rows: _streams),
          EnquiryTab(
            parentMobile: widget.parentMobile,
            studentName: widget.studentName,
            studentId: widget.studentId,
            admissionNo: widget.admissionNo,
            classCode: widget.classCode,
            assignedTeacher: widget.assignedTeacher,
          ),
          NotificationsTab(
            parentMobile: widget.parentMobile,
            classCode: widget.classCode,
          ),
          BusTrackingTab(
            studentId: widget.studentId,
            studentName: widget.studentName,
          ),
        ],
      ),
    );
  }
}
