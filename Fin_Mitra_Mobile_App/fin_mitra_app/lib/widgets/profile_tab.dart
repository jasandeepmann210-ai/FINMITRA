import 'package:flutter/material.dart';

class ProfileTab extends StatelessWidget {
  final List<Map<String, dynamic>> rows;

  const ProfileTab({super.key, required this.rows});

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.person_off, size: 48, color: Colors.grey.shade400),
            const SizedBox(height: 12),
            Text("No profile data found.", style: TextStyle(color: Colors.grey.shade600)),
          ],
        ),
      );
    }

    final r = rows.first;

    String val(String key) => r[key]?.toString().trim() ?? "-";

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [

          // ── Avatar + Name Card ──
          Card(
            elevation: 3,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 36,
                    backgroundColor: Colors.blue.shade100,
                    child: Text(
                      (val("student_name") != "-" ? val("student_name")[0] : "?").toUpperCase(),
                      style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold,
                          color: Colors.blue.shade800),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(val("student_name"),
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text("Class: ${val("studying_class")}",
                            style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
                        Text("Adm No: ${val("admission_no")}",
                            style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // ── Personal Info ──
          _section("Personal Information", [
            _row(Icons.cake,       "Date of Birth",     val("dob")),
            _row(Icons.wc,         "Gender",            val("gender")),
            _row(Icons.category,   "Caste Category",    val("caste_category")),
            _row(Icons.temple_hindu, "Religion",        val("religion")),
            _row(Icons.translate,  "Mother Tongue",     val("mother_tongue")),
          ]),
          const SizedBox(height: 12),

          // ── Family Info ──
          _section("Family Information", [
            _row(Icons.man,        "Father's Name",     val("father_name")),
            _row(Icons.woman,      "Mother's Name",     val("mother_name")),
            _row(Icons.phone,      "Mobile",            val("mobile")),
            _row(Icons.email,      "Email",             val("email")),
          ]),
          const SizedBox(height: 12),

          // ── Academic Info ──
          _section("Academic Information", [
            _row(Icons.school,     "Academic Year",     val("current_academic_year")),
            _row(Icons.calendar_today, "Admission Date", val("admission_date")),
            _row(Icons.class_,     "Current Class",     val("studying_class")),
            _row(Icons.history,    "Previous Class",    val("previous_class")),
            _row(Icons.percent,    "Last Exam %",       val("last_exam_percentage")),
            _row(Icons.sports,     "Extracurricular",   val("extracurricular_activities")),
          ]),
        ],
      ),
    );
  }

  Widget _section(String title, List<Widget> children) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold,
                    color: Colors.blue)),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _row(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.blue.shade400),
          const SizedBox(width: 10),
          Expanded(
            flex: 2,
            child: Text(label,
                style: const TextStyle(fontSize: 13, color: Colors.black54)),
          ),
          Expanded(
            flex: 3,
            child: Text(value,
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
          ),
        ],
      ),
    );
  }
}
