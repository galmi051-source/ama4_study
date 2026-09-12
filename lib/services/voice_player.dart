import 'voice_player_io.dart' if (dart.library.js_interop) 'voice_player_web.dart';

/// VOICEVOX 音声ファイルの再生。
/// ネイティブ（Android/iOS）は audioplayers、Web は index.html の
/// `<audio>` 要素 1 個を使い回す JS（window.ama4Audio）で再生する。
abstract class VoicePlayer {
  factory VoicePlayer() = VoicePlayerImpl;

  /// assets/ からの相対パス（例 'voice/H-001_q.m4a'）を再生し、
  /// 最後まで鳴るか stop() されるまで待つ。再生できなければ例外。
  Future<void> play(String assetPath, double rate);

  Future<void> stop();

  /// iOS Safari などで「ユーザー操作による音声の有効化」がまだなら false。
  bool get unlocked;

  /// オフライン用に音声ファイルをまとめて取得してキャッシュする（Web のみ）。
  Future<void> prefetch(
      List<String> assetPaths, void Function(int done, int total) onProgress);
}
