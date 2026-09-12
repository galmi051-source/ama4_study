import 'dart:async';
import 'dart:js_interop';

import 'voice_player.dart';

// web/index.html で定義している window.ama4Audio
@JS('ama4Audio.play')
external JSPromise<JSBoolean> _jsPlay(JSString url, JSNumber rate);

@JS('ama4Audio.stop')
external void _jsStop();

@JS('ama4Audio.isUnlocked')
external JSBoolean _jsIsUnlocked();

@JS('ama4Audio.prefetch')
external JSPromise<JSAny?> _jsPrefetch(JSArray<JSString> urls, JSFunction cb);

String _url(String assetPath) => 'assets/assets/$assetPath';

class VoicePlayerImpl implements VoicePlayer {
  @override
  Future<void> play(String assetPath, double rate) async {
    // <base href> からの相対 URL。Flutter Web は pubspec の assets/ を
    // build/web/assets/assets/ に置くので assets が 2 回続く
    await _jsPlay(_url(assetPath).toJS, rate.toJS).toDart;
  }

  @override
  Future<void> stop() async => _jsStop();

  @override
  bool get unlocked => _jsIsUnlocked().toDart;

  @override
  Future<void> prefetch(List<String> assetPaths,
      void Function(int done, int total) onProgress) async {
    final urls = assetPaths.map((p) => _url(p).toJS).toList().toJS;
    final cb = ((JSNumber done, JSNumber total) =>
        onProgress(done.toDartInt, total.toDartInt)).toJS;
    await _jsPrefetch(urls, cb).toDart;
  }
}
