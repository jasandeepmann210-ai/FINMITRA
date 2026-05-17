import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';

Future<List<Map<String, dynamic>>> fetchEnquiries({
  required String parentMobile,
  String? studentId,
}) async {
  var uri = Uri.parse(
    "$BASE_URL/api/v1/enquiries?parent_mobile=${Uri.encodeQueryComponent(parentMobile.trim())}",
  );
  if (studentId != null && studentId.trim().isNotEmpty) {
    uri = uri.replace(
      queryParameters: {
        ...uri.queryParameters,
        "student_id": studentId.trim(),
      },
    );
  }
  final response = await http.get(uri, headers: {"X-API-Key": API_KEY});
  if (response.statusCode != 200) {
    throw Exception("Failed to load enquiries");
  }
  final body = jsonDecode(response.body) as Map<String, dynamic>;
  return List<Map<String, dynamic>>.from(body["enquiries"] ?? []);
}

Future<void> postEnquiry({
  required String parentMobile,
  required String studentName,
  required String studentId,
  required String admissionNo,
  required String classCode,
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
      "student_id": studentId.trim(),
      "admission_no": admissionNo.trim(),
      "class_code": classCode.trim().toUpperCase(),
      "message": message.trim(),
    }),
  );
  if (response.statusCode != 200 && response.statusCode != 201) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Failed to submit enquiry");
  }
}

Future<Map<String, dynamic>> teacherLogin({
  required String classCode,
  required String pin,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/teacher/login");
  final response = await http.post(
    uri,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: jsonEncode({
      "class_code": classCode.trim().toUpperCase(),
      "pin": pin.trim(),
    }),
  );
  if (response.statusCode != 200) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Login failed");
  }
  return jsonDecode(response.body) as Map<String, dynamic>;
}

Future<Map<String, dynamic>> fetchTeacherEnquiries({
  required String classCode,
  required String pin,
  String status = "all",
}) async {
  final cc = classCode.trim().toUpperCase();
  var uri = Uri.parse(
    "$BASE_URL/api/v1/teacher/enquiries?class_code=${Uri.encodeQueryComponent(cc)}",
  );
  if (status != "all") {
    uri = uri.replace(queryParameters: {...uri.queryParameters, "status": status});
  }
  final response = await http.get(
    uri,
    headers: {
      "X-API-Key": API_KEY,
      "X-Class-Code": cc,
      "X-Teacher-Pin": pin.trim(),
    },
  );
  if (response.statusCode != 200) {
    throw Exception("Failed to load class enquiries");
  }
  return jsonDecode(response.body) as Map<String, dynamic>;
}

Future<void> replyToEnquiry({
  required String enquiryId,
  required String classCode,
  required String pin,
  required String reply,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/enquiries/$enquiryId/reply");
  final response = await http.post(
    uri,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      "X-Class-Code": classCode.trim().toUpperCase(),
      "X-Teacher-Pin": pin.trim(),
    },
    body: jsonEncode({"reply": reply.trim()}),
  );
  if (response.statusCode != 200) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Failed to send reply");
  }
}
