import 'package:flutter/material.dart';
import '../widgets/profile_tab.dart';
import '../widgets/fee_tab.dart';
import 'login_screen.dart';
import 'report_card_tab.dart';

class StudentDashboard extends StatelessWidget {
  final String studentName;
  final String schoolName;
  final String schoolFolder;
  final String schoolAddress;
  final String logoUrl;
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
    required this.profileRows,
    required this.feeRows,
    required this.marksRows,
  });

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: const Color(0xFFF0F4F8),
        appBar: AppBar(
          backgroundColor: Colors.blue.shade700,
          foregroundColor: Colors.white,
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(studentName,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              Text(schoolName,
                  style: const TextStyle(fontSize: 12, color: Colors.white70)),
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
            )
          ],
          bottom: const TabBar(
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white60,
            indicatorColor: Colors.white,
            tabs: [
              Tab(icon: Icon(Icons.person),       text: "Profile"),
              Tab(icon: Icon(Icons.receipt_long), text: "Fee Ledger"),
              Tab(icon: Icon(Icons.grade),        text: "Report Card"),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            ProfileTab(rows: profileRows),
            FeeTab(rows: feeRows),
            ReportCardTab(
              marksRows: marksRows,
              schoolName: schoolName,
              schoolAddress: schoolAddress,
              logoUrl: logoUrl,
            ),
          ],
        ),
      ),
    );
  }
}
