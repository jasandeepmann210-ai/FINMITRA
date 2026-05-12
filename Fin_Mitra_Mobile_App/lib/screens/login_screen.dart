import 'package:flutter/material.dart';
import '../branding_assets.dart';
import '../config.dart';
import '../helpers/api_helper.dart';
import 'student_dashboard.dart';
import 'child_selection_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _mobileController = TextEditingController();

  bool _loading = false;
  String _error = "";

  Future<void> _login() async {
    final mobile = _mobileController.text.trim();

    if (mobile.isEmpty) {
      setState(() => _error = "Please enter mobile number.");
      return;
    }

    if (mobile.length < 10) {
      setState(() => _error = "Mobile number must be at least 10 digits.");
      return;
    }

    setState(() { _loading = true; _error = ""; });

    try {
      // Fetch student_log.csv
      final allStudents = await fetchCSV("", FILE_STUDENTS);
      
      // Filter by mobile number
      final childrenList = filterByMobileNumber(allStudents, mobile);

      if (childrenList.isEmpty) {
        setState(() { _error = "No children found for this mobile number."; _loading = false; });
        return;
      }

      // Fetch fees_ledger.csv
      List<Map<String, dynamic>> feeLedger = [];
      try {
        final allFees = await fetchCSV("", FILE_FEES);
        feeLedger = allFees;
      } catch (_) {}

      // Fetch school_info.csv
      String schoolInfoName = "School";
      String schoolAddress = "";
      try {
        final infoRows = await fetchCSV("", "school_info.csv");
        if (infoRows.isNotEmpty) {
          schoolInfoName = infoRows.first["school_name"]?.toString() ?? "School";
          schoolAddress = infoRows.first["address"]?.toString() ?? "";
        }
      } catch (_) {}

      final logoUrl = "$BASE_URL/user-logo/demo";

      if (!mounted) return;

      // If only one child, go directly to dashboard
      if (childrenList.length == 1) {
        final child = childrenList.first;
        final admNo = child["admission_no"]?.toString() ?? "";
        
        // Filter fees for this child
        final childFees = feeLedger
            .where((row) =>
                (row["account_name"]?.toString() ?? "")
                    .startsWith("$mobile/$admNo") ||
                (row["account_name"]?.toString() ?? "").contains(admNo))
            .toList();

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => StudentDashboard(
              studentName: child["student_name"]?.toString() ?? "",
              schoolName: schoolInfoName,
              schoolFolder: mobile,
              schoolAddress: schoolAddress,
              logoUrl: logoUrl,
              parentMobile: mobile,
              admissionNo: admNo,
              profileRows: childrenList,
              feeRows: childFees,
              marksRows: [],
            ),
          ),
        );
      } else {
        // Multiple children: show selection screen
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ChildSelectionScreen(
              children: childrenList,
              mobileNumber: mobile,
              allFees: feeLedger,
              schoolName: schoolInfoName,
              schoolAddress: schoolAddress,
              logoUrl: logoUrl,
            ),
          ),
        );
      }
    } catch (e) {
      setState(() { _error = "Error: $e"; _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            Image.asset(
              kOpeningScreenAsset,
              width: double.infinity,
              fit: BoxFit.fitWidth,
              errorBuilder: (_, __, ___) => Container(
                color: const Color(0xFFF0F4F8),
                alignment: Alignment.center,
                height: 250,
                child: Icon(Icons.image_not_supported_outlined,
                    size: 48, color: Colors.grey.shade400),
              ),
            ),
            SafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 18),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: Card(
                    elevation: 10,
                    color: Colors.white.withOpacity(0.96),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          TextField(
                            controller: _mobileController,
                            keyboardType: TextInputType.phone,
                            decoration: InputDecoration(
                              labelText: "Mobile Number",
                              hintText: "Enter your mobile number",
                              prefixIcon: const Icon(Icons.phone),
                              filled: true,
                              fillColor: Colors.grey.shade50,
                              contentPadding: const EdgeInsets.symmetric(
                                horizontal: 14,
                                vertical: 12,
                              ),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                          ),
                          if (_error.isNotEmpty) ...[
                            const SizedBox(height: 10),
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
                                  Expanded(
                                    child: Text(
                                      _error,
                                      style: const TextStyle(color: Colors.red),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          const SizedBox(height: 14),
                          SizedBox(
                            width: double.infinity,
                            height: 48,
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(10),
                                gradient: const LinearGradient(
                                  colors: [Color(0xFF34C8A0), Color(0xFF2F75E1)],
                                ),
                              ),
                              child: ElevatedButton(
                                onPressed: _loading ? null : _login,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.transparent,
                                  shadowColor: Colors.transparent,
                                  foregroundColor: Colors.white,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                ),
                                child: _loading
                                    ? const SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(
                                          color: Colors.white,
                                          strokeWidth: 2,
                                        ),
                                      )
                                    : const Text("Login", style: TextStyle(fontSize: 17)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
