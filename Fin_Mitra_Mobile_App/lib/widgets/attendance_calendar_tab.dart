import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import '../helpers/date_parse.dart';

class AttendanceCalendarTab extends StatefulWidget {
  final List<Map<String, dynamic>> rows;

  const AttendanceCalendarTab({super.key, required this.rows});

  @override
  State<AttendanceCalendarTab> createState() => _AttendanceCalendarTabState();
}

class _AttendanceCalendarTabState extends State<AttendanceCalendarTab> {
  CalendarFormat _format = CalendarFormat.month;
  DateTime _focused = DateTime.now();
  DateTime? _selected;

  Map<DateTime, String> get _statusByDay {
    final map = <DateTime, String>{};
    for (final r in widget.rows) {
      final d = parseAttendanceDate(r["date"]?.toString() ?? "");
      if (d == null) continue;
      final key = DateTime(d.year, d.month, d.day);
      map[key] = (r["status"]?.toString() ?? "").toLowerCase();
    }
    return map;
  }

  Color _colorForStatus(String? status) {
    switch (status) {
      case "present":
        return Colors.green;
      case "absent":
        return Colors.red;
      case "holiday":
        return Colors.amber.shade700;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusMap = _statusByDay;
    final selected = _selected != null
        ? DateTime(_selected!.year, _selected!.month, _selected!.day)
        : null;
    final dayStatus = selected != null ? statusMap[selected] : null;

    return Column(
      children: [
        TableCalendar(
          firstDay: DateTime.utc(2025, 1, 1),
          lastDay: DateTime.utc(2027, 12, 31),
          focusedDay: _focused,
          calendarFormat: _format,
          selectedDayPredicate: (day) => isSameDay(_selected, day),
          onDaySelected: (selectedDay, focusedDay) {
            setState(() {
              _selected = selectedDay;
              _focused = focusedDay;
            });
          },
          onFormatChanged: (f) => setState(() => _format = f),
          onPageChanged: (focusedDay) => _focused = focusedDay,
          calendarStyle: const CalendarStyle(
            outsideDaysVisible: false,
            weekendTextStyle: TextStyle(color: Colors.redAccent),
          ),
          calendarBuilders: CalendarBuilders(
            defaultBuilder: (context, day, focused) {
              final key = DateTime(day.year, day.month, day.day);
              final st = statusMap[key];
              if (st == null) return null;
              return Container(
                margin: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: _colorForStatus(st).withOpacity(0.25),
                  shape: BoxShape.circle,
                  border: Border.all(color: _colorForStatus(st), width: 2),
                ),
                alignment: Alignment.center,
                child: Text('${day.day}', style: const TextStyle(fontSize: 13)),
              );
            },
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _legend(Colors.green, "Present"),
              _legend(Colors.red, "Absent"),
              _legend(Colors.amber.shade700, "Holiday"),
            ],
          ),
        ),
        if (selected != null)
          Card(
            margin: const EdgeInsets.all(12),
            child: ListTile(
              leading: Icon(Icons.event_available, color: _colorForStatus(dayStatus)),
              title: Text(formatDisplayDate(selected)),
              subtitle: Text(
                dayStatus != null && dayStatus!.isNotEmpty
                    ? "Status: ${dayStatus![0].toUpperCase()}${dayStatus!.substring(1)}"
                    : "No attendance record for this day",
              ),
            ),
          ),
      ],
    );
  }

  Widget _legend(Color c, String label) {
    return Row(
      children: [
        Container(width: 12, height: 12, decoration: BoxDecoration(color: c, shape: BoxShape.circle)),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
