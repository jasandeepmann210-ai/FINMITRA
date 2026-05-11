import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';

Future<List<Map<String, dynamic>>> fetchEnquiries(String parentMobile) async {
  final q = Uri.encodeQueryComponent(parentMobile.trim());
  final uri = Uri.parse("$BASE_URL/api/v1/enquiries?parent_mobile=$q");
  final response = await http.get(uri, headers: {"X-API-Key": API_KEY});
  if (response.statusCode != 200) {
    throw Exception("Failed to load enquiries");
  }
  final body = jsonDecode(response.body) as Map<String, dynamic>;
  final list = body["enquiries"];
  return List<Map<String, dynamic>>.from(list ?? []);
}

Future<void> postEnquiry({
  required String parentMobile,
  required String studentName,
  required String admissionNo,
  required String message,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/enquiries");
  final response = await http.post(
    uri,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: jsonEncode({
      "parent_mobile": parentMobile.trim(),
      "student_name": studentName.trim(),
      "admission_no": admissionNo.trim(),
      "message": message.trim(),
    }),
  );
  if (response.statusCode != 200 && response.statusCode != 201) {
    throw Exception("Failed to submit enquiry");
  }
}
