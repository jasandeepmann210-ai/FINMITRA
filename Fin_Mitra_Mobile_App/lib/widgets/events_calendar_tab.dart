import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import '../helpers/date_parse.dart';

class EventsCalendarTab extends StatefulWidget {
  final List<Map<String, dynamic>> rows;

  const EventsCalendarTab({super.key, required this.rows});

  @override
  State<EventsCalendarTab> createState() => _EventsCalendarTabState();
}

class _EventsCalendarTabState extends State<EventsCalendarTab> {
  CalendarFormat _format = CalendarFormat.month;
  DateTime _focused = DateTime.now();
  DateTime? _selected;

  Map<DateTime, List<String>> get _eventsByDay {
    final map = <DateTime, List<String>>{};
    for (final r in widget.rows) {
      final name = r["event"]?.toString().trim() ?? "";
      if (name.isEmpty) continue;
      final d = parseEventDate(r["date"]?.toString() ?? "");
      if (d == null) continue;
      final key = DateTime(d.year, d.month, d.day);
      map.putIfAbsent(key, () => []).add(name);
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    final eventsMap = _eventsByDay;
    final selected = _selected != null
        ? DateTime(_selected!.year, _selected!.month, _selected!.day)
        : null;
    final dayEvents = selected != null ? eventsMap[selected] ?? [] : <String>[];

    return Column(
      children: [
        TableCalendar(
          firstDay: DateTime.utc(2025, 1, 1),
          lastDay: DateTime.utc(2027, 12, 31),
          focusedDay: _focused,
          calendarFormat: _format,
          selectedDayPredicate: (day) => isSameDay(_selected, day),
          eventLoader: (day) {
            final key = DateTime(day.year, day.month, day.day);
            return eventsMap[key] ?? [];
          },
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
            markerDecoration: BoxDecoration(
              color: Colors.blue,
              shape: BoxShape.circle,
            ),
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Text(
                selected != null
                    ? "Events on ${formatDisplayDate(selected)}"
                    : "Tap a date to see holidays & events",
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              if (dayEvents.isEmpty)
                Text("No events on this date", style: TextStyle(color: Colors.grey.shade600))
              else
                ...dayEvents.map(
                  (e) => Card(
                    child: ListTile(
                      leading: Icon(Icons.celebration, color: Colors.blue.shade700),
                      title: Text(e),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}
