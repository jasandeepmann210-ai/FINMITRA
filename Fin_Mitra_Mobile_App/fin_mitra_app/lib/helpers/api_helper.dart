import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config.dart';

Future<List<Map<String, dynamic>>> fetchCSV(String school, String filename) async {
  final uri = Uri.parse("$BASE_URL/api/v1/read?path=$filename");
  final response = await http.get(uri, headers: {"X-API-Key": API_KEY});
  if (response.statusCode != 200) throw Exception("Failed to load $filename");
  final jsonBody = jsonDecode(response.body);
  return List<Map<String, dynamic>>.from(jsonBody["data"]);
}

// student_log.csv — exact match on account_name
List<Map<String, dynamic>> filterByStudent(
    List<Map<String, dynamic>> rows, String studentName) {
  return rows.where((row) {
    final name = row["account_name"]?.toString().trim().toLowerCase() ?? "";
    return name == studentName.toLowerCase();
  }).toList();
}

// fee_ledger.csv — match admission number as "/" separated part
List<Map<String, dynamic>> filterFeeByAdmNo(
    List<Map<String, dynamic>> rows, String admNo) {
  return rows.where((row) {
    final parts = (row["account_name"]?.toString() ?? "")
        .split("/")
        .map((p) => p.trim());
    return parts.any((part) => part == admNo.trim());
  }).toList();
}

// Marks — filter by student_id == admNo
List<Map<String, dynamic>> filterMarksByAdmNo(
    List<Map<String, dynamic>> rows, String admNo) {
  return rows.where((row) {
    final studentId = row["student_id"]?.toString().trim() ?? "";
    return studentId == admNo.trim();
  }).toList();
}
