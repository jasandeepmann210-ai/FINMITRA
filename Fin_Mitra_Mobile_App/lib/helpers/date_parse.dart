/// Parse dates from Data_Dummy CSV formats.
DateTime? parseAttendanceDate(String raw) {
  final s = raw.trim();
  if (s.isEmpty) return null;
  try {
    if (s.contains('-') && s.length >= 10) {
      final parts = s.split('T').first.split('-');
      if (parts.length == 3 && parts[0].length == 4) {
        return DateTime(
          int.parse(parts[0]),
          int.parse(parts[1]),
          int.parse(parts[2]),
        );
      }
    }
  } catch (_) {}
  return null;
}

DateTime? parseEventDate(String raw) {
  final s = raw.trim();
  if (s.isEmpty) return null;
  try {
    final parts = s.split('-');
    if (parts.length == 3) {
      final d = int.parse(parts[0]);
      final m = int.parse(parts[1]);
      final y = int.parse(parts[2]);
      return DateTime(y, m, d);
    }
  } catch (_) {}
  return null;
}

String formatDisplayDate(DateTime d) {
  return '${d.day.toString().padLeft(2, '0')}-${d.month.toString().padLeft(2, '0')}-${d.year}';
}
