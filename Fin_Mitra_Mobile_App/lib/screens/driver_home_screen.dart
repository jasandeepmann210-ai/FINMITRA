import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../helpers/bus_api.dart';
import 'driver_login_screen.dart';

class DriverHomeScreen extends StatefulWidget {
  final String busId;
  final String pin;
  final String routeName;
  final String driverName;
  final String vehicleNo;

  const DriverHomeScreen({
    super.key,
    required this.busId,
    required this.pin,
    required this.routeName,
    required this.driverName,
    required this.vehicleNo,
  });

  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  bool _loading = true;
  bool _tripActive = false;
  bool _sharingLocation = false;
  List<Map<String, dynamic>> _roster = [];
  String? _error;
  Timer? _locationTimer;
  StreamSubscription<Position>? _positionSub;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  @override
  void dispose() {
    _stopLocationSharing();
    super.dispose();
  }

  Future<void> _reload() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await fetchDriverTrip(busId: widget.busId, pin: widget.pin);
      if (!mounted) return;
      final active = data["trip_active"] == true;
      setState(() {
        _tripActive = active;
        _roster = List<Map<String, dynamic>>.from(data["roster"] ?? []);
        _loading = false;
      });
      if (active && !_sharingLocation) {
        await _startLocationSharing();
      }
      if (!active) {
        _stopLocationSharing();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<bool> _ensureLocationPermission() async {
    var perm = await Geolocator.checkPermission();
    if (perm == LocationPermission.denied) {
      perm = await Geolocator.requestPermission();
    }
    if (perm == LocationPermission.deniedForever || perm == LocationPermission.denied) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Location permission is required to share the bus position."),
          ),
        );
      }
      return false;
    }
    if (!await Geolocator.isLocationServiceEnabled()) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Turn on location (GPS) on your phone.")),
        );
      }
      return false;
    }
    return true;
  }

  Future<void> _uploadCurrentPosition() async {
    try {
      final pos = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
      );
      await driverPostLocation(
        busId: widget.busId,
        pin: widget.pin,
        lat: pos.latitude,
        lng: pos.longitude,
      );
    } catch (_) {}
  }

  Future<void> _startLocationSharing() async {
    if (_sharingLocation) return;
    if (!await _ensureLocationPermission()) return;

    setState(() => _sharingLocation = true);
    await _uploadCurrentPosition();

    _locationTimer?.cancel();
    _locationTimer = Timer.periodic(const Duration(seconds: 10), (_) => _uploadCurrentPosition());

    _positionSub?.cancel();
    _positionSub = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 25,
      ),
    ).listen((pos) {
      driverPostLocation(
        busId: widget.busId,
        pin: widget.pin,
        lat: pos.latitude,
        lng: pos.longitude,
      );
    });
  }

  void _stopLocationSharing() {
    _locationTimer?.cancel();
    _locationTimer = null;
    _positionSub?.cancel();
    _positionSub = null;
    _sharingLocation = false;
  }

  Future<void> _startTrip() async {
    if (!await _ensureLocationPermission()) return;
    try {
      await driverStartTrip(busId: widget.busId, pin: widget.pin);
      await _reload();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Route started — parents can see your location")),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("$e")));
      }
    }
  }

  Future<void> _endTrip() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("End route?"),
        content: const Text("Parents will no longer see live bus location."),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text("Cancel")),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text("End route")),
        ],
      ),
    );
    if (ok != true) return;

    try {
      _stopLocationSharing();
      await driverEndTrip(busId: widget.busId, pin: widget.pin);
      await _reload();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("$e")));
      }
    }
  }

  Future<void> _markAlight(Map<String, dynamic> student) async {
    final sid = student["student_id"]?.toString() ?? "";
    final name = student["student_name"]?.toString() ?? "Student";
    final stop = student["drop_stop"]?.toString();

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text("$name got off?"),
        content: Text("Parents will be notified${stop != null && stop.isNotEmpty ? " ($stop)" : ""}."),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text("Cancel")),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text("Confirm"),
          ),
        ],
      ),
    );
    if (ok != true) return;

    try {
      await driverMarkAlight(
        busId: widget.busId,
        pin: widget.pin,
        studentId: sid,
        stopName: stop,
      );
      await _reload();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("$name marked off — parent notified")),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("$e")));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.routeName.isNotEmpty ? widget.routeName : widget.busId),
        backgroundColor: Colors.orange.shade800,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              _stopLocationSharing();
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const DriverLoginScreen()),
              );
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _reload,
              child: ListView(
                padding: const EdgeInsets.all(12),
                children: [
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(_error!, style: const TextStyle(color: Colors.red)),
                    ),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(widget.driverName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          Text("${widget.busId} · ${widget.vehicleNo}"),
                          const SizedBox(height: 8),
                          if (_tripActive) ...[
                            Row(
                              children: [
                                Icon(Icons.gps_fixed, color: Colors.green.shade700, size: 20),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    _sharingLocation
                                        ? "Sharing this phone's location with parents"
                                        : "Route active",
                                    style: TextStyle(color: Colors.green.shade800),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            OutlinedButton(
                              onPressed: _endTrip,
                              child: const Text("End route"),
                            ),
                          ] else ...[
                            const Text(
                              "When you start the route, this phone becomes the bus GPS for parents.",
                            ),
                            const SizedBox(height: 12),
                            FilledButton.icon(
                              onPressed: _startTrip,
                              icon: const Icon(Icons.play_arrow),
                              label: const Text("Start route"),
                              style: FilledButton.styleFrom(
                                backgroundColor: Colors.orange.shade800,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text("Students on your bus", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 6),
                  if (!_tripActive)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(
                        "Start the route to mark when children get off.",
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ),
                  ..._roster.map((s) {
                    final alighted = s["alighted"] == true;
                    return Card(
                      margin: const EdgeInsets.only(bottom: 6),
                      color: alighted ? Colors.green.shade50 : null,
                      child: ListTile(
                        leading: Icon(
                          alighted ? Icons.check_circle : Icons.person,
                          color: alighted ? Colors.green : Colors.orange.shade800,
                        ),
                        title: Text(s["student_name"]?.toString() ?? ""),
                        subtitle: Text("Drop: ${s["drop_stop"] ?? "—"}"),
                        trailing: alighted
                            ? const Text("Off bus", style: TextStyle(color: Colors.green, fontWeight: FontWeight.w600))
                            : (_tripActive
                                ? FilledButton(
                                    onPressed: () => _markAlight(s),
                                    style: FilledButton.styleFrom(
                                      backgroundColor: Colors.orange.shade800,
                                      padding: const EdgeInsets.symmetric(horizontal: 12),
                                    ),
                                    child: const Text("Got off"),
                                  )
                                : null),
                      ),
                    );
                  }),
                ],
              ),
            ),
    );
  }
}
