import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show AssetManifest, rootBundle;
import 'package:flutter_tts/flutter_tts.dart';

import '../models/question.dart';
import 'voice_player.dart';

typedef StepCallback = void Function(int step);

/// 読み上げる内容。assets/voice/<key>.m4a（または .wav/.mp3）があれば VOICEVOX の音声を再生し、
/// 無ければ text を端末の音声合成で読む。key は tools/make_voice.py の台本と同じ規則。
class Voice {
  final String key;
  final String text;
  const Voice(this.key, this.text);
}

/// VOICEVOX で作った音声ファイルを優先し、無いものは端末の音声合成
/// （Android: Google TTS / iOS: AVSpeech / Web: Web Speech API）で読み上げる。
/// speakAll に Voice・文字列・Duration（無音の間）を並べて渡すと順番に再生する。
class TtsService {
  final FlutterTts _tts = FlutterTts();
  final VoicePlayer _player = VoicePlayer();
  final Map<String, String> _voiceFiles = {}; // key → 'voice/xxx.m4a'（assets/ からの相対）
  bool _ready = false;
  int _token = 0;
  double _rate = 0.5;

  /// 直近の再生エラー（画面に表示する用）。null なら問題なし。
  final ValueNotifier<String?> lastError = ValueNotifier(null);

  /// 同梱されている VOICEVOX 音声の数（0 なら全部端末の音声合成で読む）
  int get voiceCount => _voiceFiles.length;

  /// assets/ からの相対パスの一覧（オフライン用の一括取得に使う）
  List<String> get voicePaths => _voiceFiles.values.toList();

  /// iOS Safari は画面を1回タップするまで音を出せない。まだなら false。
  bool get audioUnlocked => _player.unlocked;

  /// 音声ファイルをまとめてキャッシュする（Web のみ意味がある）
  Future<void> prefetchAll(void Function(int done, int total) onProgress) =>
      _player.prefetch(voicePaths, onProgress);

  /// assets/voice/ の音声ファイルを一覧にしておく。起動時に1回呼ぶ。
  Future<void> loadVoices() async {
    try {
      final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
      for (final path in manifest.listAssets()) {
        if (!path.startsWith('assets/voice/')) continue;
        final name = path.substring('assets/voice/'.length);
        final dot = name.lastIndexOf('.');
        if (dot <= 0) continue;
        final ext = name.substring(dot + 1).toLowerCase();
        if (ext != 'm4a' && ext != 'wav' && ext != 'mp3') continue;
        _voiceFiles[name.substring(0, dot)] = path.substring('assets/'.length);
      }
    } catch (e) {
      debugPrint('voice list error: $e');
    }
  }

  /// 設定の読み上げ速度（0.5 が標準）を音声ファイルの再生速度に換算
  double get _playbackRate => (_rate / 0.5).clamp(0.5, 2.0).toDouble();

  Future<void> _ensure() async {
    if (_ready) return;
    _ready = true;
    try {
      await _tts.setLanguage('ja-JP');
      await _tts.setPitch(1.0);
      await _tts.setSpeechRate(_rate);
      await _tts.awaitSpeakCompletion(true);
      if (!kIsWeb && defaultTargetPlatform == TargetPlatform.iOS) {
        await _tts.setSharedInstance(true);
        await _tts.setIosAudioCategory(
          IosTextToSpeechAudioCategory.playback,
          [
            IosTextToSpeechAudioCategoryOptions.allowBluetoothA2DP,
            IosTextToSpeechAudioCategoryOptions.duckOthers,
          ],
          IosTextToSpeechAudioMode.defaultMode,
        );
      }
    } catch (e) {
      debugPrint('TTS init error: $e');
    }
  }

  Future<void> setRate(double r) async {
    _rate = r;
    if (_ready) await _tts.setSpeechRate(r);
  }

  /// 途中で stop() や別の speakAll が呼ばれたら false を返して終了する。
  Future<bool> speakAll(List<Object> parts, {StepCallback? onStep}) async {
    await _ensure();
    final token = ++_token;
    lastError.value = null;
    await _player.stop();
    await _tts.stop();
    for (var i = 0; i < parts.length; i++) {
      if (token != _token) return false;
      onStep?.call(i);
      final p = parts[i];
      if (p is Duration) {
        final end = DateTime.now().add(p);
        while (DateTime.now().isBefore(end)) {
          if (token != _token) return false;
          await Future.delayed(const Duration(milliseconds: 100));
        }
      } else if (p is Voice) {
        final file = _voiceFiles[p.key];
        var ok = false;
        if (file != null) ok = await _playFile(file);
        if (token != _token) return false;
        if (!ok) {
          if (!await _speakText(p.text, token)) return false;
        } else {
          await Future.delayed(const Duration(milliseconds: 150));
        }
      } else {
        if (!await _speakText(p.toString(), token)) return false;
      }
    }
    return token == _token;
  }

  Future<bool> _speakText(String raw, int token) async {
    final text = normalize(raw);
    if (text.trim().isEmpty) return token == _token;
    try {
      await _tts.speak(text);
    } catch (e) {
      debugPrint('tts error: $e');
      lastError.value = '端末の読み上げに失敗しました（$e）';
      return token == _token;
    }
    if (token != _token) return false;
    await Future.delayed(const Duration(milliseconds: 250));
    return token == _token;
  }

  /// 再生が最後まで終わるか stop() されるまで待つ。再生できなかったら false。
  Future<bool> _playFile(String assetPath) async {
    try {
      await _player.play(assetPath, _playbackRate);
      return true;
    } catch (e) {
      debugPrint('voice play error ($assetPath): $e');
      lastError.value = _describe(e, assetPath);
      return false;
    }
  }

  static String _describe(Object e, String assetPath) {
    final s = e.toString();
    if (s.contains('NotAllowedError')) {
      return '音声がまだ有効になっていません。画面をタップしてから ▶ を押してください。';
    }
    if (s.contains('NotSupportedError') || s.contains('decode')) {
      return 'この端末で再生できない音声形式です（$assetPath）。端末の読み上げで代用します。';
    }
    if (s.contains('network') || s.contains('404') || s.contains('load')) {
      return '音声ファイルを取得できませんでした（$assetPath）。電波が無い場合は、設定の「音声をまとめてダウンロード」を試してください。';
    }
    return '音声を再生できませんでした：$s';
  }

  Future<bool> speak(String text) => speakAll([text]);
  Future<bool> speakVoice(Voice v) => speakAll([v]);

  Future<void> stop() async {
    _token++;
    await _player.stop();
    await _tts.stop();
  }

  // ---- 読み上げ文の組み立て ----

  static String _end(String s) {
    final t = s.trim();
    if (t.isEmpty) return t;
    return RegExp(r'[。？！?!]$').hasMatch(t) ? t : '$t。';
  }

  static String questionText(Question q) {
    final b = StringBuffer(_end(q.readQuestion ?? q.question));
    for (var i = 0; i < q.choices.length; i++) {
      b.write('${i + 1}番、${_end(q.choices[i])}');
    }
    return b.toString();
  }

  static String answerText(Question q) =>
      '正解は、${q.answer}番。${_end(q.correctChoice)}';

  static String explanationText(Question q) {
    final e = q.readExplanation ?? q.explanation;
    return e.trim().isEmpty ? '' : '解説。${_end(e)}';
  }

  // ---- VOICEVOX 音声のキー（tools/make_voice.py と同じ規則） ----

  static String _safe(String s) => s.replaceAll(RegExp(r'[^A-Za-z0-9_-]'), '_');

  static Voice questionVoice(Question q) =>
      Voice('${_safe(q.id)}_q', questionText(q));
  static Voice answerVoice(Question q) =>
      Voice('${_safe(q.id)}_a', answerText(q));
  static Voice explanationVoice(Question q) =>
      Voice('${_safe(q.id)}_e', explanationText(q));
  static Voice numberVoice(int n) =>
      Voice('sys_dai_${n.toString().padLeft(3, '0')}', '第$n問。');
  static Voice subjectVoice(String subject) => Voice(
      subject == Subjects.houki ? 'sys_houki' : 'sys_kougaku', '$subject。');
  static const correctVoice = Voice('sys_correct', '正解です。');
  static const wrongVoice = Voice('sys_wrong', '不正解です。');
  static const sampleVoice =
      Voice('sys_sample', '周波数は145MHz、空中線電力は20W、抵抗は50Ωです。');

  // ---- 記号・単位を読める形に変換 ----

  static const Map<String, String> _symbols = {
    '〔': '',
    '〕': '',
    'Ω': 'オーム',
    'λ': 'ラムダ',
    '×': 'かける',
    '÷': 'わる',
    '＝': 'イコール',
    '=': 'イコール',
    '√': 'ルート',
    'π': 'パイ',
    '≒': 'およそ',
    '→': '、',
    '～': 'から',
    '〜': 'から',
    '％': 'パーセント',
    '%': 'パーセント',
  };

  // 直前が英字の数字（A1A や J3E など型式名）には単位を付けない
  static const _num = r'(?<![A-Za-z0-9.])(\d[\d.]*)\s*';

  static final List<MapEntry<RegExp, String>> _units = [
    MapEntry(RegExp('${_num}GHz'), 'ギガヘルツ'),
    MapEntry(RegExp('${_num}MHz'), 'メガヘルツ'),
    MapEntry(RegExp('${_num}kHz'), 'キロヘルツ'),
    MapEntry(RegExp('${_num}Hz'), 'ヘルツ'),
    MapEntry(RegExp('${_num}mA'), 'ミリアンペア'),
    MapEntry(RegExp('${_num}kW'), 'キロワット'),
    MapEntry(RegExp('${_num}mW'), 'ミリワット'),
    MapEntry(RegExp('${_num}W(?![A-Za-z])'), 'ワット'),
    MapEntry(RegExp('${_num}V(?![A-Za-z])'), 'ボルト'),
    MapEntry(RegExp('${_num}A(?![A-Za-z0-9])'), 'アンペア'),
    MapEntry(RegExp('${_num}dB'), 'デシベル'),
    MapEntry(RegExp('${_num}km'), 'キロメートル'),
    MapEntry(RegExp('${_num}m(?![A-Za-z])'), 'メートル'),
  ];

  static final RegExp _blank = RegExp(r'[（(［\[][\s　]*[)）］\]]');

  static String normalize(String s) {
    var t = s.replaceAll(_blank, 'かっこ');
    _symbols.forEach((k, v) => t = t.replaceAll(k, v));
    for (final rule in _units) {
      t = t.replaceAllMapped(rule.key, (m) => '${m[1]}${rule.value}');
    }
    return t;
  }
}
