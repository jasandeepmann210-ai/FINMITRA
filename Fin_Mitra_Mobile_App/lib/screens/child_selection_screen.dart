import 'package:flutter/material.dart';
import '../config.dart';
import 'student_dashboard.dart';

class ChildSelectionScreen extends StatelessWidget {
  final List<Map<String, dynamic>> children;
  final String mobileNumber;
  final List<Map<String, dynamic>> allFees;
  final String schoolName;
  final String schoolAddress;
  final String logoUrl;

  const ChildSelectionScreen({
    super.key,
    required this.children,
    required this.mobileNumber,
    required this.allFees,
    required this.schoolName,
    required this.schoolAddress,
    required this.logoUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      appBar: AppBar(
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        title: const Text("Select Child"),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 24),
            Text(
              "Select a child to view details",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade800,
              ),
            ),
            const SizedBox(height: 24),
            ...children.asMap().entries.map((entry) {
              final idx = entry.key;
              final child = entry.value;
              final studentName = child["student_name"]?.toString() ?? "Unknown";
              final className = child["studying_class"]?.toString() ?? "N/A";
              final admNo = child["admission_no"]?.toString() ?? "";

              return GestureDetector(
                onTap: () => _selectChild(context, idx, child, admNo),
                child: Card(
                  elevation: 4,
                  margin: const EdgeInsets.only(bottom: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 32,
                          backgroundColor: Colors.blue.shade100,
                          child: Text(
                            studentName.isNotEmpty
                                ? studentName[0].toUpperCase()
                                : "?",
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.blue.shade800,
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                studentName,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                "Class: $className",
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                              Text(
                                "Adm No: $admNo",
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.arrow_forward_ios,
                          color: Colors.blue.shade700,
                          size: 18,
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  void _selectChild(BuildContext context, int idx,
      Map<String, dynamic> child, String admNo) {
    // Filter fees for this specific child
    final childFees = allFees
        .where((row) =>
            (row["account_name"]?.toString() ?? "")
                .startsWith("$mobileNumber/$admNo") ||
            (row["account_name"]?.toString() ?? "").contains(admNo))
        .toList();

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => StudentDashboard(
          studentName: child["student_name"]?.toString() ?? "",
          schoolName: schoolName,
          schoolFolder: mobileNumber,
          schoolAddress: schoolAddress,
          logoUrl: logoUrl,
          parentMobile: mobileNumber,
          admissionNo: admNo,
          profileRows: [child],
          feeRows: childFees,
          marksRows: [],
        ),
      ),
    );
  }
}
