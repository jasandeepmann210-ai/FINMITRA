import 'package:flutter/material.dart';
import '../config.dart';
import '../helpers/api_helper.dart';
import 'student_dashboard.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _schoolController  = TextEditingController();
  final _studentController = TextEditingController();
  final _admNoController   = TextEditingController();

  bool _loading = false;
  bool _obscure = true;
  String _error = "";

  Future<void> _login() async {
    final school  = _schoolController.text.trim();
    final student = _studentController.text.trim();
    final admNo   = _admNoController.text.trim();

    if (school.isEmpty || student.isEmpty || admNo.isEmpty) {
      setState(() => _error = "Please fill in all fields.");
      return;
    }

    setState(() { _loading = true; _error = ""; });

    try {
      // Authenticate via student_log.csv
      final allStudents = await fetchCSV(school, FILE_STUDENTS);
      final matched = filterByStudent(allStudents, student);

      if (matched.isEmpty) {
        setState(() { _error = "Student not found."; _loading = false; });
        return;
      }

      final validAdmNo = matched.any((row) =>
          row["admission_no"]?.toString().trim() == admNo);

      if (!validAdmNo) {
        setState(() { _error = "Incorrect admission number."; _loading = false; });
        return;
      }

      // Fetch fees_ledger.csv
      List<Map<String, dynamic>> feeLedger = [];
      try {
        final allFees = await fetchCSV(school, FILE_FEES);
        feeLedger = filterFeeByAdmNo(allFees, admNo);
      } catch (_) {}

      // Fetch marks using studying_class
      final studyingClass = matched.first["studying_class"]?.toString().trim() ?? "";
      List<Map<String, dynamic>> marksList = [];
      try {
        final allMarks = await fetchCSV(school, "$MARKS_FOLDER/$studyingClass.csv");
        marksList = filterMarksByAdmNo(allMarks, admNo);
      } catch (_) {}

      // Fetch school_info.csv for school name + address
      String schoolInfoName = school;
      String schoolAddress  = "";
      try {
        final infoRows = await fetchCSV(school, "school_info.csv");
        if (infoRows.isNotEmpty) {
          schoolInfoName = infoRows.first["school_name"]?.toString() ?? school;
          schoolAddress  = infoRows.first["address"]?.toString() ?? "";
        }
      } catch (_) {}

      // Logo URL — served directly from Render
      final logoUrl = "$BASE_URL/user-logo/$school";

      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => StudentDashboard(
            studentName: student,
            schoolName: schoolInfoName,
            schoolFolder: school,
            schoolAddress: schoolAddress,
            logoUrl: logoUrl,
            profileRows: matched,
            feeRows: feeLedger,
            marksRows: marksList,
          ),
        ),
      );
    } catch (e) {
      setState(() { _error = "Connection error: $e"; _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Card(
            elevation: 8,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 400),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Image.asset("assets/logo.png", height: 80,),
                    const SizedBox(height: 12),
                    Text("Fin Mitra",
                        style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold,
                            color: Colors.blue.shade800)),
                    const SizedBox(height: 4),
                    Text("Student Portal",
                        style: TextStyle(fontSize: 14, color: Colors.grey.shade600)),
                    const SizedBox(height: 32),
                    _buildField(_schoolController, "School Name", "e.g. test_school", Icons.business),
                    const SizedBox(height: 16),
                    _buildField(_studentController, "Student Name", "As listed in records", Icons.person),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _admNoController,
                      obscureText: _obscure,
                      decoration: InputDecoration(
                        labelText: "Admission Number",
                        hintText: "Your admission number",
                        prefixIcon: const Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off),
                          onPressed: () => setState(() => _obscure = !_obscure),
                        ),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                    const SizedBox(height: 12),
                    if (_error.isNotEmpty)
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline, color: Colors.red, size: 18),
                            const SizedBox(width: 8),
                            Expanded(child: Text(_error, style: const TextStyle(color: Colors.red))),
                          ],
                        ),
                      ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        onPressed: _loading ? null : _login,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue.shade700,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        child: _loading
                            ? const SizedBox(height: 20, width: 20,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Text("Login", style: TextStyle(fontSize: 16)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField(TextEditingController ctrl, String label, String hint, IconData icon) {
    return TextField(
      controller: ctrl,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(icon),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}
