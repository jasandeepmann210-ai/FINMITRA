import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

/// In-app playback for HLS / stream URLs from classroom_streams.csv.
class ClassStreamScreen extends StatefulWidget {
  final String classLabel;
  final String streamUrl;

  const ClassStreamScreen({
    super.key,
    required this.classLabel,
    required this.streamUrl,
  });

  @override
  State<ClassStreamScreen> createState() => _ClassStreamScreenState();
}

class _ClassStreamScreenState extends State<ClassStreamScreen> {
  late final WebViewController _controller;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (_) {
            if (mounted) setState(() => _loading = false);
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.streamUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Class ${widget.classLabel}"),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_loading)
            const Center(child: CircularProgressIndicator()),
        ],
      ),
    );
  }
}
