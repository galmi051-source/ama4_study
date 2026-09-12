import 'package:flutter/material.dart';

import 'app_state.dart';
import 'screens/home_screen.dart';
import 'theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final state = AppState();
  await state.load();
  runApp(Ama4App(state: state));
}

class Ama4App extends StatefulWidget {
  final AppState state;
  const Ama4App({super.key, required this.state});

  @override
  State<Ama4App> createState() => _Ama4AppState();
}

class _Ama4AppState extends State<Ama4App> {
  final _messenger = GlobalKey<ScaffoldMessengerState>();

  @override
  void initState() {
    super.initState();
    widget.state.tts.lastError.addListener(_showError);
  }

  @override
  void dispose() {
    widget.state.tts.lastError.removeListener(_showError);
    super.dispose();
  }

  /// 再生に失敗したら、どの画面でも黙って止まらず理由を出す
  void _showError() {
    final msg = widget.state.tts.lastError.value;
    if (msg == null) return;
    _messenger.currentState
      ?..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(
        content: Text(msg),
        duration: const Duration(seconds: 6),
      ));
  }

  @override
  Widget build(BuildContext context) {
    return AppScope(
      state: widget.state,
      child: MaterialApp(
        title: '4アマ ながら学習',
        debugShowCheckedModeBanner: false,
        scaffoldMessengerKey: _messenger,
        theme: buildTheme(),
        home: const HomeScreen(),
      ),
    );
  }
}
