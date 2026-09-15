import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models/question.dart';
import '../services/tts_service.dart';
import '../theme.dart';
import '../widgets/question_widgets.dart';

class QuizScreen extends StatefulWidget {
  final List<Question> questions;
  final String title;

  /// 「分野を選んで解く」から開いたときは、どこまでやったかを記録する
  final bool trackRange;
  const QuizScreen(
      {super.key,
      required this.questions,
      required this.title,
      this.trackRange = false});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  late final AppState app;
  int index = 0;
  int? selected;
  int correctCount = 0;
  final List<Question> missed = [];

  Question get q => widget.questions[index];
  bool get answered => selected != null;
  bool get isLast => index + 1 >= widget.questions.length;

  @override
  void initState() {
    super.initState();
    app = AppScope.read(context);
    WidgetsBinding.instance.addPostFrameCallback((_) => _autoReadQuestion());
  }

  @override
  void dispose() {
    app.tts.stop();
    super.dispose();
  }

  void _autoReadQuestion() {
    if (app.store.autoRead) app.tts.speakVoice(TtsService.questionVoice(q));
  }

  void _select(int n) {
    if (answered) return;
    final current = q;
    final ok = n == current.answer;
    setState(() {
      selected = n;
      if (ok) {
        correctCount++;
      } else {
        missed.add(current);
      }
    });
    app.record(current, ok);
    if (widget.trackRange) {
      app.markRange(widget.title, index + 1, widget.questions.length);
    }
    if (app.store.autoRead) {
      app.tts.speakAll([
        ok ? TtsService.correctVoice : TtsService.wrongVoice,
        TtsService.answerVoice(current),
        TtsService.explanationVoice(current),
      ]);
    }
  }

  void _next() {
    app.tts.stop();
    if (isLast) {
      Navigator.of(context).pushReplacement(MaterialPageRoute(
        builder: (_) => QuizResultScreen(
          title: widget.title,
          total: widget.questions.length,
          correct: correctCount,
          missed: missed,
        ),
      ));
      return;
    }
    setState(() {
      index++;
      selected = null;
    });
    _autoReadQuestion();
  }

  ChoiceState _stateFor(int n) {
    if (!answered) return ChoiceState.idle;
    if (n == q.answer) return ChoiceState.correct;
    if (n == selected) return ChoiceState.wrong;
    return ChoiceState.dimmed;
  }

  @override
  Widget build(BuildContext context) {
    final auto = app.store.autoRead;
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            tooltip: auto ? '自動読み上げをオフにする' : '自動読み上げをオンにする',
            icon: Icon(auto ? Icons.volume_up : Icons.volume_off),
            onPressed: () {
              app.updateSettings(autoRead: !auto);
              if (auto) app.tts.stop();
              setState(() {});
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        children: [
          QuestionHeader(index: index, total: widget.questions.length, q: q),
          const SizedBox(height: 12),
          QuestionBody(q: q),
          const SizedBox(height: 16),
          for (var i = 0; i < q.choices.length; i++)
            ChoiceTile(
              number: i + 1,
              text: q.choices[i],
              state: _stateFor(i + 1),
              onTap: answered ? null : () => _select(i + 1),
            ),
          if (answered) ...[
            const SizedBox(height: 6),
            ExplanationCard(q: q, correct: selected == q.answer),
          ],
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Expanded(
                    child: ReadButton(
                      label: '問題',
                      onPressed: () =>
                          app.tts.speakVoice(TtsService.questionVoice(q)),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ReadButton(
                      label: '答え',
                      onPressed: answered
                          ? () => app.tts.speakVoice(TtsService.answerVoice(q))
                          : null,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ReadButton(
                      label: '解説',
                      onPressed: answered
                          ? () => app.tts.speakVoice(TtsService.explanationVoice(q))
                          : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              FilledButton(
                onPressed: answered ? _next : null,
                child: Text(isLast ? '結果を見る' : '次の問題'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class QuizResultScreen extends StatelessWidget {
  final String title;
  final int total;
  final int correct;
  final List<Question> missed;

  const QuizResultScreen({
    super.key,
    required this.title,
    required this.total,
    required this.correct,
    required this.missed,
  });

  @override
  Widget build(BuildContext context) {
    final pct = total == 0 ? 0 : (correct * 100 / total).round();
    return Scaffold(
      appBar: AppBar(title: Text('$titleの結果')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const SizedBox(height: 12),
          Center(
            child: Text('$correct / $total',
                style: const TextStyle(
                    fontSize: 44,
                    fontWeight: FontWeight.w800,
                    color: AppColors.ink,
                    fontFeatures: [FontFeature.tabularFigures()])),
          ),
          Center(
            child: Text('正答率 $pct%',
                style: const TextStyle(color: AppColors.muted, fontSize: 15)),
          ),
          const SizedBox(height: 24),
          if (missed.isNotEmpty)
            FilledButton(
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute(
                  builder: (_) => QuizScreen(
                      questions: List.of(missed), title: '間違えた問題'),
                ),
              ),
              child: Text('間違えた${missed.length}問をもう一度'),
            ),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('ホームに戻る'),
          ),
          if (missed.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('間違えた問題',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
            const SizedBox(height: 8),
            for (final m in missed)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ExplanationCard(q: m, showQuestion: true),
              ),
          ],
        ],
      ),
    );
  }
}
