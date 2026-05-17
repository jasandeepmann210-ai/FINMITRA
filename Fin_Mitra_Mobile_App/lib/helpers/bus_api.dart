import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';

Map<String, String> _driverHeaders(String busId, String pin) => {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      "X-Bus-Id": busId.trim().toUpperCase(),
      "X-Driver-Pin": pin.trim(),
    };

// --- Parent ---

Future<Map<String, dynamic>> fetchBusStatus({required String studentId}) async {
  final uri = Uri.parse(
    "$BASE_URL/api/v1/bus/status?student_id=${Uri.encodeQueryComponent(studentId)}",
  );
  final response = await http.get(uri, headers: {"X-API-Key": API_KEY});
  if (response.statusCode != 200) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Failed to load bus status");
  }
  return jsonDecode(response.body) as Map<String, dynamic>;
}

// --- Driver ---

Future<Map<String, dynamic>> driverLogin({
  required String busId,
  required String pin,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/driver/login");
  final response = await http.post(
    uri,
    headers: {"Content-Type": "application/json", "X-API-Key": API_KEY},
    body: jsonEncode({"bus_id": busId.trim().toUpperCase(), "pin": pin.trim()}),
  );
  if (response.statusCode != 200) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Login failed");
  }
  return jsonDecode(response.body) as Map<String, dynamic>;
}

Future<Map<String, dynamic>> fetchDriverTrip({
  required String busId,
  required String pin,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/driver/trip");
  final response = await http.get(uri, headers: _driverHeaders(busId, pin));
  if (response.statusCode != 200) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Failed to load trip");
  }
  return jsonDecode(response.body) as Map<String, dynamic>;
}

Future<void> driverStartTrip({required String busId, required String pin}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/driver/trip/start");
  final response = await http.post(uri, headers: _driverHeaders(busId, pin));
  if (response.statusCode != 200 && response.statusCode != 201) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Could not start route");
  }
}

Future<void> driverEndTrip({required String busId, required String pin}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/driver/trip/end");
  final response = await http.post(uri, headers: _driverHeaders(busId, pin));
  if (response.statusCode != 200) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Could not end route");
  }
}

Future<void> driverPostLocation({
  required String busId,
  required String pin,
  required double lat,
  required double lng,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/driver/location");
  final response = await http.post(
    uri,
    headers: _driverHeaders(busId, pin),
    body: jsonEncode({"lat": lat, "lng": lng}),
  );
  if (response.statusCode != 200 && response.statusCode != 201) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Could not send location");
  }
}

Future<void> driverMarkAlight({
  required String busId,
  required String pin,
  required String studentId,
  String? stopName,
}) async {
  final uri = Uri.parse("$BASE_URL/api/v1/driver/alight");
  final response = await http.post(
    uri,
    headers: _driverHeaders(busId, pin),
    body: jsonEncode({
      "student_id": studentId,
      if (stopName != null && stopName.isNotEmpty) "stop_name": stopName,
    }),
  );
  if (response.statusCode != 200 && response.statusCode != 201) {
    final err = jsonDecode(response.body);
    throw Exception(err["error"]?.toString() ?? "Could not mark student");
  }
}
