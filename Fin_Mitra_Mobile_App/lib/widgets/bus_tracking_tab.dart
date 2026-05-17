import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import '../helpers/bus_api.dart';

class BusTrackingTab extends StatefulWidget {
  final String studentId;
  final String studentName;

  const BusTrackingTab({
    super.key,
    required this.studentId,
    required this.studentName,
  });

  @override
  State<BusTrackingTab> createState() => _BusTrackingTabState();
}

class _BusTrackingTabState extends State<BusTrackingTab> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;
  Timer? _pollTimer;
  String? _lastAlertedEventId;

  @override
  void initState() {
    super.initState();
    _reload();
    _pollTimer = Timer.periodic(const Duration(seconds: 10), (_) => _reload(silent: true));
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _reload({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }
    try {
      final data = await fetchBusStatus(studentId: widget.studentId);
      if (!mounted) return;

      final last = data["last_event"] as Map<String, dynamic>?;
      if (last != null) {
        final eid = last["id"]?.toString() ?? "";
        if (eid.isNotEmpty && eid != _lastAlertedEventId) {
          _lastAlertedEventId = eid;
          final stop = last["stop_name"]?.toString() ?? "stop";
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text("${widget.studentName} got off the bus at $stop"),
              backgroundColor: Colors.green.shade800,
              duration: const Duration(seconds: 6),
            ),
          );
        }
      }

      setState(() {
        _data = data;
        _loading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _openInMaps(double lat, double lng) async {
    final uri = Uri.parse(
      "https://www.google.com/maps/search/?api=1&query=$lat,$lng",
    );
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _data == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null && _data == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 12),
              FilledButton(onPressed: _reload, child: const Text("Retry")),
            ],
          ),
        ),
      );
    }

    final assigned = _data?["assigned"] == true;
    if (!assigned) {
      return ListView(
        children: [
          const SizedBox(height: 48),
          Icon(Icons.directions_bus_outlined, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Text(
              _data?["message"]?.toString() ??
                  "No school bus is assigned to ${widget.studentName}.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade700),
            ),
          ),
        ],
      );
    }

    final assignment = _data!["assignment"] as Map<String, dynamic>? ?? {};
    final loc = _data!["location"] as Map<String, dynamic>? ?? {};
    final lastEvent = _data!["last_event"] as Map<String, dynamic>?;
    final statusLabel = _data!["status_label"]?.toString() ?? "";
    final tripActive = _data!["trip_active"] == true;

    final busLat = (loc["lat"] as num?)?.toDouble();
    final busLng = (loc["lng"] as num?)?.toDouble();
    final hasLocation = busLat != null && busLng != null;
    final busPoint = hasLocation ? LatLng(busLat, busLng) : null;

    return RefreshIndicator(
      onRefresh: () => _reload(),
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          if (lastEvent != null) _EventBanner(event: lastEvent, studentName: widget.studentName),
          if (!tripActive)
            Card(
              color: Colors.amber.shade50,
              child: const ListTile(
                leading: Icon(Icons.info_outline),
                title: Text("Driver has not started the route"),
                subtitle: Text("Location will appear when the driver taps Start route on their phone."),
              ),
            ),
          if (tripActive && !hasLocation)
            Card(
              color: Colors.blue.shade50,
              child: const ListTile(
                leading: Icon(Icons.gps_not_fixed),
                title: Text("Waiting for driver location"),
                subtitle: Text("The driver's phone will share GPS once available."),
              ),
            ),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.directions_bus, color: Colors.orange.shade800),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          assignment["route_name"]?.toString() ?? "School bus",
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      ),
                      Chip(
                        label: Text(statusLabel, style: const TextStyle(fontSize: 11)),
                        backgroundColor: Colors.orange.shade50,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text("Vehicle ${assignment["vehicle_no"] ?? "—"} · Driver ${assignment["driver_name"] ?? "—"}"),
                  Text("Your stop: ${assignment["drop_stop"] ?? assignment["pickup_stop"] ?? "—"}"),
                  if (loc["updated_at"] != null)
                    Text(
                      "Location from driver's phone · ${loc["updated_at"]}",
                      style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
                    ),
                ],
              ),
            ),
          ),
          if (busPoint != null) ...[
            const SizedBox(height: 8),
            SizedBox(
              height: 280,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: FlutterMap(
                  options: MapOptions(
                    initialCenter: busPoint,
                    initialZoom: 14,
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                      userAgentPackageName: "com.finmitra.app",
                    ),
                    MarkerLayer(
                      markers: [
                        Marker(
                          point: busPoint,
                          width: 48,
                          height: 48,
                          child: Icon(Icons.directions_bus, color: Colors.orange.shade800, size: 40),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () => _openInMaps(busLat!, busLng!),
              icon: const Icon(Icons.map),
              label: const Text("Open in Maps"),
            ),
          ],
          const SizedBox(height: 12),
          const Text("Got off the bus", style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          ..._buildRecentEvents(),
        ],
      ),
    );
  }

  List<Widget> _buildRecentEvents() {
    final events = List<Map<String, dynamic>>.from(_data?["recent_events"] ?? []);
    if (events.isEmpty) {
      return [
        Text("No drop-offs recorded yet.", style: TextStyle(color: Colors.grey.shade600)),
      ];
    }
    return events.map((e) {
      return Card(
        margin: const EdgeInsets.only(bottom: 6),
        child: ListTile(
          leading: Icon(Icons.check_circle, color: Colors.green.shade700),
          title: Text("${widget.studentName} got off"),
          subtitle: Text("${e["stop_name"] ?? ""} · ${e["at"]?.toString().substring(0, 16) ?? ""}"),
        ),
      );
    }).toList();
  }
}

class _EventBanner extends StatelessWidget {
  final Map<String, dynamic> event;
  final String studentName;

  const _EventBanner({required this.event, required this.studentName});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.green.shade50,
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(Icons.check_circle, color: Colors.green.shade700),
        title: Text("$studentName is off the bus"),
        subtitle: Text("At ${event["stop_name"] ?? "stop"} · ${event["at"]?.toString().substring(0, 16) ?? ""}"),
      ),
    );
  }
}
