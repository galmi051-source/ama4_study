import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';

import 'voice_player.dart';

class VoicePlayerImpl implements VoicePlayer {
  final AudioPlayer _player = AudioPlayer();
  Completer<void>? _playing;
  bool _configured = false;

  Future<void> _configure() async {
    if (_configured) return;
    _configured = true;
    try {
      // iOS: サイレントスイッチが ON でも鳴らす（playback カテゴリ）
      await AudioPlayer.global.setAudioContext(AudioContext(
        iOS: AudioContextIOS(
          category: AVAudioSessionCategory.playback,
          options: const {AVAudioSessionOptions.duckOthers},
        ),
        android: const AudioContextAndroid(
          contentType: AndroidContentType.speech,
          usageType: AndroidUsageType.media,
          audioFocus: AndroidAudioFocus.gainTransientMayDuck,
        ),
      ));
    } catch (e) {
      debugPrint('audio context error: $e');
    }
  }

  @override
  Future<void> play(String assetPath, double rate) async {
    await _configure();
    final done = Completer<void>();
    _playing = done;
    final sub = _player.onPlayerComplete.listen((_) {
      if (!done.isCompleted) done.complete();
    });
    try {
      await _player.stop();
      await _player.play(AssetSource(assetPath));
      if (rate != 1.0) await _player.setPlaybackRate(rate);
      await done.future;
    } finally {
      await sub.cancel();
      if (identical(_playing, done)) _playing = null;
    }
  }

  @override
  Future<void> stop() async {
    final p = _playing;
    if (p != null && !p.isCompleted) p.complete();
    await _player.stop();
  }

  @override
  bool get unlocked => true;

  @override
  Future<void> prefetch(List<String> assetPaths,
      void Function(int done, int total) onProgress) async {
    onProgress(assetPaths.length, assetPaths.length); // 同梱済みなので不要
  }
}
