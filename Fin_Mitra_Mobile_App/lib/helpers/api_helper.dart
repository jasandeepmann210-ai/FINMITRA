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

// Marks — filter by student_id == admNo
List<Map<String, dynamic>> filterMarksByAdmNo(
    List<Map<String, dynamic>> rows, String admNo) {
  return rows.where((row) {
    final studentId = row["student_id"]?.toString().trim() ?? "";
    return studentId == admNo.trim();
  }).toList();
}
