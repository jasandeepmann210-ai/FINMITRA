import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';

Future<List<Map<String, dynamic>>> fetchParentNotifications({
  required String parentMobile,
  String? classCode,
}) async {
  var uri = Uri.parse(
    "$BASE_URL/api/v1/notifications?parent_mobile=${Uri.encodeQueryComponent(parentMobile)}",
  );
  if (classCode != null && classCode.trim().isNotEmpty) {
    uri = uri.replace(queryParameters: {
      ...uri.queryParameters,
      "class_code": classCode.trim(),
    });
  }
  final response = await http.get(uri, headers: {"X-API-Key": API_KEY});
  if (response.statusCode != 200) throw Exception("Failed to load notifications");
  final body = jsonDecode(response.body) as Map<String, dynamic>;
  return List<Map<String, dynamic>>.from(body["notifications"] ?? []);
}

Future<void> postNotification({
  required String classCode,
  required String pin,
  required String title,
  required String message,
  required String scope,
  String? targetClassCode,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/notifications");
  final response = await http.post(
    uri,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      "X-Class-Code": classCode.trim().toUpperCase(),
      "X-Teacher-Pin": pin.trim(),
    },
    body: jsonEncode({
      "title": title.trim(),
      "message": message.trim(),
      "scope": scope,
      if (targetClassCode != null && targetClassCode.isNotEmpty)
        "class_code": targetClassCode.trim(),
    }),
  );
  if (response.statusCode != 200 && response.statusCode != 201) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Failed to post announcement");
  }
}

Future<List<Map<String, dynamic>>> fetchTeacherNotifications({
  required String classCode,
  required String pin,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/teacher/notifications");
  final response = await http.get(
    uri,
    headers: {
      "X-API-Key": API_KEY,
      "X-Class-Code": classCode.trim().toUpperCase(),
      "X-Teacher-Pin": pin.trim(),
    },
  );
  if (response.statusCode != 200) throw Exception("Failed to load announcements");
  final body = jsonDecode(response.body) as Map<String, dynamic>;
  return List<Map<String, dynamic>>.from(body["notifications"] ?? []);
}
