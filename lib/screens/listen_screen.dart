import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:wakelock_plus/wakelock_plus.dart';

import '../app_state.dart';
import '../models/question.dart';
import '../services/tts_service.dart';
import '../theme.dart';
import '../widgets/question_widgets.dart';

/// 問題 → 選択肢 → 考える時間 → 正解 → 解説 を自動で繰り返す。
/// 画面は点けたままにする（画面オフで再生が止まることがあるため）。
class ListenScreen extends StatefulWidget {
  final List<Question> questions;
  final String title;
  const ListenScreen({super.key, required this.questions, required this.title});

  @override
  State<ListenScreen> createState() => _ListenScreenState();
}

class _ListenScreenState extends State<ListenScreen>
    with WidgetsBindingObserver {
  late final AppState app;
  int index = 0;
  int step = -1;
  bool playing = false;
  bool loop = true;

  /// 自動で止めた理由（画面ロックなど）。null なら表示しない
  String? stoppedReason;

  // speakAll に渡す parts の並びと対応
  static const _stepLabels = ['問題番号', '科目', '問題', '考える時間', '正解', '解説', '次へ'];
  static const _answerStep = 4;

  int get total => widget.questions.length;

  @override
  void initState() {
    super.initState();
    app = AppScope.read(context);
    WidgetsBinding.instance.addObserver(this);
    // Web（iOS Safari 16.4 以降）は Screen Wake Lock API。未対応でも落とさない
    WakelockPlus.enable().catchError((e) => debugPrint('wakelock: $e'));
    WidgetsBinding.instance.addPostFrameCallback((_) => _play());
  }

  @override
  void dispose() {
    playing = false;
    WidgetsBinding.instance.removeObserver(this);
    app.tts.stop();
    WakelockPlus.disable().catchError((e) => debugPrint('wakelock: $e'));
    super.dispose();
  }

  /// ブラウザ版は、画面ロック・別アプリへの切り替えで JS が止められ
  /// 次の音声が始まらない。中途半端に止まるより、明示的に止めて理由を出す。
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!kIsWeb || !playing) return;
    if (state == AppLifecycleState.hidden ||
        state == AppLifecycleState.paused) {
      _pause();
      setState(() => stoppedReason = '画面ロック／アプリ切り替えのため停止しました。▶ で再開できます。');
    }
  }

  Future<void> _play() async {
    if (playing || total == 0) return;
    setState(() {
      playing = true;
      stoppedReason = null;
    });
    while (mounted && playing) {
      final q = widget.questions[index];
      final done = await app.tts.speakAll(
        [
          TtsService.numberVoice(index + 1),
          TtsService.subjectVoice(q.subject),
          TtsService.questionVoice(q),
          Duration(seconds: app.store.thinkSec),
          TtsService.answerVoice(q),
          TtsService.explanationVoice(q),
          const Duration(milliseconds: 1200),
        ],
        onStep: (s) {
          if (mounted) setState(() => step = s);
        },
      );
      if (!done || !mounted || !playing) break;
      setState(() {
        step = -1;
        if (index + 1 < total) {
          index++;
        } else if (loop) {
          index = 0;
        } else {
          playing = false;
        }
      });
    }
  }

  void _pause() {
    setState(() => playing = false);
    app.tts.stop();
  }

  void _jump(int delta) {
    final wasPlaying = playing;
    app.tts.stop();
    var next = index + delta;
    if (next < 0) next = 0;
    if (next > total - 1) next = total - 1;
    setState(() {
      playing = false;
      index = next;
      step = -1;
    });
    if (wasPlaying) Future.microtask(_play);
  }

  @override
  Widget build(BuildContext context) {
    if (total == 0) {
      return Scaffold(
        appBar: AppBar(title: Text(widget.title)),
        body: const Center(child: Text('この条件の問題はまだありません')),
      );
    }
    final q = widget.questions[index];
    final revealed = step >= _answerStep;

    return Scaffold(
      appBar: AppBar(title: Text('ながら聞き｜${widget.title}')),
      body: Column(
        children: [
          LinearProgressIndicator(
            value: (index + 1) / total,
            minHeight: 3,
            backgroundColor: AppColors.line,
            color: AppColors.amber,
          ),
          if (stoppedReason != null)
            _Notice(stoppedReason!, color: AppColors.amberDim),
          ValueListenableBuilder<String?>(
            valueListenable: app.tts.lastError,
            builder: (_, err, __) => err == null
                ? const SizedBox.shrink()
                : _Notice(err, color: AppColors.wrong),
          ),
          if (kIsWeb && !playing && !app.tts.audioUnlocked)
            const _Notice('iPhone では画面を1回タップすると音が出せるようになります。▶ を押してください。',
                color: AppColors.panel),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
              children: [
                Row(
                  children: [
                    Expanded(
                        child: QuestionHeader(index: index, total: total, q: q)),
                    if (step >= 0 && step < _stepLabels.length)
                      Text('いま：${_stepLabels[step]}',
                          style: const TextStyle(
                              color: AppColors.muted, fontSize: 12)),
                  ],
                ),
                const SizedBox(height: 12),
                QuestionBody(q: q),
                const SizedBox(height: 16),
                for (var i = 0; i < q.choices.length; i++)
                  ChoiceTile(
                    number: i + 1,
                    text: q.choices[i],
                    state: !revealed
                        ? ChoiceState.idle
                        : (i + 1 == q.answer
                            ? ChoiceState.correct
                            : ChoiceState.dimmed),
                  ),
                if (revealed) ExplanationCard(q: q),
              ],
            ),
          ),
          SafeArea(
            top: false,
            child: Container(
              color: AppColors.panel,
              padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
              child: Row(
                children: [
                  IconButton(
                    tooltip: loop ? '最後まで行ったら最初に戻る' : '最後で止める',
                    color: loop ? AppColors.amber : Colors.white54,
                    icon: const Icon(Icons.repeat),
                    onPressed: () => setState(() => loop = !loop),
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: '前の問題',
                    color: Colors.white,
                    iconSize: 32,
                    icon: const Icon(Icons.skip_previous),
                    onPressed: index > 0 ? () => _jump(-1) : null,
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    tooltip: playing ? '一時停止' : '再生',
                    style: IconButton.styleFrom(
                      backgroundColor: AppColors.amber,
                      foregroundColor: AppColors.panelDeep,
                      minimumSize: const Size(60, 60),
                    ),
                    iconSize: 34,
                    icon: Icon(playing ? Icons.pause : Icons.play_arrow),
                    onPressed: playing ? _pause : _play,
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    tooltip: '次の問題',
                    color: Colors.white,
                    iconSize: 32,
                    icon: const Icon(Icons.skip_next),
                    onPressed: index < total - 1 ? () => _jump(1) : null,
                  ),
                  const Spacer(),
                  Text('考える${app.store.thinkSec}秒',
                      style:
                          const TextStyle(color: Colors.white54, fontSize: 12)),
                ],
              ),
            ),
          ),
          if (kIsWeb)
            Container(
              width: double.infinity,
              color: AppColors.panelDeep,
              padding: const EdgeInsets.fromLTRB(12, 6, 12, 8),
              child: const Text(
                'ブラウザ版のため、画面をロックしたり他のアプリに切り替えると再生は止まります。画面は自動で点いたままにします。',
                style: TextStyle(color: Colors.white38, fontSize: 11),
              ),
            ),
        ],
      ),
    );
  }
}

class _Notice extends StatelessWidget {
  final String text;
  final Color color;
  const _Notice(this.text, {required this.color});

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        color: color,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Text(text,
            style: const TextStyle(color: Colors.white, fontSize: 13)),
      );
}
