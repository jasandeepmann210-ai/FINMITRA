import 'package:flutter/material.dart';
import '../helpers/bus_api.dart';
import 'driver_home_screen.dart';

class DriverLoginScreen extends StatefulWidget {
  const DriverLoginScreen({super.key});

  @override
  State<DriverLoginScreen> createState() => _DriverLoginScreenState();
}

class _DriverLoginScreenState extends State<DriverLoginScreen> {
  final _busController = TextEditingController();
  final _pinController = TextEditingController();
  bool _loading = false;
  String _error = "";
  bool _obscurePin = true;

  Future<void> _login() async {
    final busId = _busController.text.trim().toUpperCase();
    final pin = _pinController.text.trim();
    if (busId.isEmpty || pin.isEmpty) {
      setState(() => _error = "Enter bus ID and PIN.");
      return;
    }
    setState(() {
      _loading = true;
      _error = "";
    });
    try {
      final info = await driverLogin(busId: busId, pin: pin);
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => DriverHomeScreen(
            busId: busId,
            pin: pin,
            routeName: info["route_name"]?.toString() ?? "",
            driverName: info["driver_name"]?.toString() ?? "Driver",
            vehicleNo: info["vehicle_no"]?.toString() ?? "",
          ),
        ),
      );
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Bus driver login"),
        backgroundColor: Colors.orange.shade800,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Icon(Icons.directions_bus, size: 56, color: Colors.orange.shade800),
            const SizedBox(height: 12),
            const Text(
              "Start your route to share this phone's location with parents",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 28),
            TextField(
              controller: _busController,
              textCapitalization: TextCapitalization.characters,
              decoration: InputDecoration(
                labelText: "Bus ID",
                hintText: "e.g. BUS-A",
                prefixIcon: const Icon(Icons.directions_bus),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _pinController,
              obscureText: _obscurePin,
              decoration: InputDecoration(
                labelText: "Driver PIN",
                prefixIcon: const Icon(Icons.lock),
                suffixIcon: IconButton(
                  icon: Icon(_obscurePin ? Icons.visibility : Icons.visibility_off),
                  onPressed: () => setState(() => _obscurePin = !_obscurePin),
                ),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            if (_error.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(_error, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _loading ? null : _login,
              style: FilledButton.styleFrom(
                backgroundColor: Colors.orange.shade800,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: _loading
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : const Text("Continue"),
            ),
            const SizedBox(height: 16),
            Text(
              "Demo: BUS-A / busa123 · BUS-B / busb123",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600, fontStyle: FontStyle.italic),
            ),
          ],
        ),
      ),
    );
  }
}
