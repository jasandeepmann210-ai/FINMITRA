import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config.dart';

Future<List<Map<String, dynamic>>> fetchCSV(String school, String filename) async {
  // Server already anchors requests inside Data_Dummy; don't prefix with "school/"
  final uri = Uri.parse("$BASE_URL/api/v1/read?path=$filename");
  final response = await http.get(uri, headers: {"X-API-Key": API_KEY});
  if (response.statusCode != 200) throw Exception("Failed to load $filename");
  final jsonBody = jsonDecode(response.body);
  return List<Map<String, dynamic>>.from(jsonBody["data"]);
}

/// Attendance rows for the logged-in parent's selected child.
List<Map<String, dynamic>> filterAttendanceForChild(
  List<Map<String, dynamic>> rows,
  String studentName,
  String admissionNo,
) {
  final n = studentName.trim();
  final a = admissionNo.trim();
  final filtered = rows.where((row) {
    final s = row["student"]?.toString().trim() ?? "";
    final ad = row["admission_no"]?.toString().trim() ?? "";
    return (n.isNotEmpty && s == n) || (a.isNotEmpty && ad == a);
  }).toList();
  filtered.sort((x, y) {
    final dx = x["date"]?.toString() ?? "";
    final dy = y["date"]?.toString() ?? "";
    return dy.compareTo(dx);
  });
  return filtered;
}

/// Non-empty event rows from events.csv
List<Map<String, dynamic>> filterValidEvents(List<Map<String, dynamic>> rows) {
  return rows.where((row) {
    final ev = row["event"]?.toString().trim() ?? "";
    final dt = row["date"]?.toString().trim() ?? "";
    return ev.isNotEmpty && dt.isNotEmpty;
  }).toList();
}

// student_log.csv — filter by mobile number (parent login)
List<Map<String, dynamic>> filterByMobileNumber(
    List<Map<String, dynamic>> rows, String mobileNumber) {
  final trimmedMobile = mobileNumber.trim();
  return rows.where((row) {
    final mobile = row["mobile"]?.toString().trim() ?? "";
    return mobile == trimmedMobile;
  }).toList();
}

// fee_ledger.csv — filter by mobile/admission as prefix before "/"
List<Map<String, dynamic>> filterFeeByMobileAndAdmNo(
    List<Map<String, dynamic>> rows, String mobileNumber, String admNo) {
  final prefix = "$mobileNumber/$admNo";
  return rows.where((row) {
    final accountName = row["account_name"]?.toString().trim() ?? "";
    return accountName == prefix;
  }).toList();
}

// Marks — filter by student_id (matches marks/*.csv, not admission_no)
List<Map<String, dynamic>> filterMarksByStudentId(
    List<Map<String, dynamic>> rows, String studentId) {
  final id = studentId.trim();
  if (id.isEmpty) return [];
  return rows.where((row) {
    final sid = row["student_id"]?.toString().trim() ?? "";
    return sid == id;
  }).toList();
}

/// Maps studying_class label to marks CSV filenames under Data_Dummy/marks/.
List<String> marksPathCandidates(String studyingClass) {
  const wordToFile = {
    'First': '1',
    'Second': '2',
    'Third': '3',
    'Fourth': '4',
    'Fifth': '5',
    'Sixth': '6',
    'Seventh': '7',
    'Eighth': '8',
    'Ninth': '9',
    'Tenth': '10',
    'Eleventh': '11',
    'Twelth': '12',
    'Twelfth': '12',
  };

  final paths = <String>[];
  final c = studyingClass.trim();

  if (wordToFile.containsKey(c)) {
    paths.add('marks/${wordToFile[c]}.csv');
  }
  if (RegExp(r'^\d+$').hasMatch(c)) {
    paths.add('marks/$c.csv');
  }

  // Fallback files present in demo Data_Dummy
  for (final f in ['10', '11', '7', '0']) {
    final p = 'marks/$f.csv';
    if (!paths.contains(p)) paths.add(p);
  }
  return paths;
}

/// Loads report-card rows for one child (original FinMitra_Original login flow).
Future<List<Map<String, dynamic>>> loadMarksForChild(
    Map<String, dynamic> child) async {
  final studentId = child["student_id"]?.toString().trim() ?? "";
  if (studentId.isEmpty) return [];

  final studyingClass = child["studying_class"]?.toString().trim() ?? "";
  for (final path in marksPathCandidates(studyingClass)) {
    try {
      final allMarks = await fetchCSV("", path);
      final matched = filterMarksByStudentId(allMarks, studentId);
      if (matched.isNotEmpty) return matched;
    } catch (_) {
      continue;
    }
  }
  return [];
}

/// Normalize class codes for API matching (e.g. "10 B" → "10B").
String normalizeClassCode(String code) {
  return code.trim().toUpperCase().replaceAll(' ', '');
}

/// Class code from school_log.csv / student_log.csv (class_code column).
Future<String> resolveClassCodeForStudent(
  Map<String, dynamic>? childRow,
  String studentId,
  String admissionNo,
) async {
  final fromChild = childRow?["class_code"]?.toString().trim() ?? "";
  if (fromChild.isNotEmpty) return normalizeClassCode(fromChild);

  final sid = studentId.trim();
  final adm = admissionNo.trim();
  for (final file in ["school_log.csv", "student_log.csv"]) {
    try {
      final rows = await fetchCSV("", file);
      for (final row in rows) {
        final cc = row["class_code"]?.toString().trim() ?? "";
        if (cc.isEmpty) continue;
        final rowSid = row["student_id"]?.toString().trim() ?? "";
        final rowAdm = row["admission_no"]?.toString().trim() ?? "";
        if (sid.isNotEmpty && rowSid == sid) return normalizeClassCode(cc);
        if (adm.isNotEmpty && (rowSid == adm || rowAdm == adm)) {
          return normalizeClassCode(cc);
        }
      }
    } catch (_) {}
  }
  return "";
}

/// Class teacher name for a class code (class_teachers.csv).
Future<String?> teacherNameForClass(String classCode) async {
  final cc = normalizeClassCode(classCode);
  if (cc.isEmpty) return null;
  try {
    final rows = await fetchCSV("", "class_teachers.csv");
    for (final row in rows) {
      final rowCc = normalizeClassCode(row["class_code"]?.toString() ?? "");
      if (rowCc == cc) return row["teacher_name"]?.toString();
    }
  } catch (_) {}
  return null;
}

/// Display label for class code (e.g. 10B → "10 B").
String displayClassCode(String normalizedCode) {
  final c = normalizedCode.trim().toUpperCase();
  if (c.isEmpty) return "";
  if (c == "ADMIN") return "All school";
  final m = RegExp(r'^(\d+)([A-Z]+)$').firstMatch(c.replaceAll(' ', ''));
  if (m != null) return "${m.group(1)} ${m.group(2)}";
  return c;
}
