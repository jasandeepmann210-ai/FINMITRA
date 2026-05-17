import 'package:flutter/material.dart';
import '../helpers/enquiry_api.dart';
import 'teacher_home_screen.dart';

/// Class teacher / POC login — each class (2A, 10A, …) has its own PIN.
class TeacherLoginScreen extends StatefulWidget {
  const TeacherLoginScreen({super.key});

  @override
  State<TeacherLoginScreen> createState() => _TeacherLoginScreenState();
}

class _TeacherLoginScreenState extends State<TeacherLoginScreen> {
  final _classController = TextEditingController();
  final _pinController = TextEditingController();
  bool _loading = false;
  String _error = "";
  bool _obscurePin = true;

  Future<void> _login() async {
    final classCode = _classController.text.trim().toUpperCase();
    final pin = _pinController.text.trim();
    if (classCode.isEmpty || pin.isEmpty) {
      setState(() => _error = "Enter class code and PIN.");
      return;
    }
    setState(() {
      _loading = true;
      _error = "";
    });
    try {
      final info = await teacherLogin(classCode: classCode, pin: pin);
      if (!mounted) return;
      final isAdmin = info["is_admin"] == true;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => TeacherHomeScreen(
            classCode: isAdmin ? "ADMIN" : classCode,
            pin: pin,
            teacherName: info["teacher_name"]?.toString() ?? "Teacher",
            isAdmin: isAdmin,
          ),
        ),
      );
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Class teacher login"),
        backgroundColor: Colors.teal.shade700,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Icon(Icons.school, size: 56, color: Colors.teal.shade700),
            const SizedBox(height: 12),
            const Text(
              "Reply to parent enquiries for your class",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              "Use your class code (e.g. 10A, 5B) and the PIN shared by the school.",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
            ),
            const SizedBox(height: 28),
            TextField(
              controller: _classController,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(
                labelText: "Class code",
                hintText: "e.g. 10A",
                prefixIcon: const Icon(Icons.class_),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _pinController,
              obscureText: _obscurePin,
              decoration: InputDecoration(
                labelText: "Teacher PIN",
                prefixIcon: const Icon(Icons.lock),
                suffixIcon: IconButton(
                  icon: Icon(_obscurePin ? Icons.visibility : Icons.visibility_off),
                  onPressed: () => setState(() => _obscurePin = !_obscurePin),
                ),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            if (_error.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(_error, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _loading ? null : _login,
              style: FilledButton.styleFrom(
                backgroundColor: Colors.teal.shade700,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: _loading
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : const Text("Open class inbox"),
            ),
            const SizedBox(height: 16),
            Text(
              "Demo teacher: 10B / class10b · 9A / class9a\nAdmin: ADMIN / admin123",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600, fontStyle: FontStyle.italic),
            ),
          ],
        ),
      ),
    );
  }
}
