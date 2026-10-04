import 'dart:async';

import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models/question.dart';
import '../services/progress_store.dart';
import '../services/tts_service.dart';
import '../theme.dart';
import '../widgets/question_widgets.dart';
import 'quiz_screen.dart';

/// 模擬試験。subject を指定しなければ本番と同じ 法規12問＋無線工学12問／60分、
/// 指定すればその科目だけ 12問／30分。採点まで正解は表示しない。
class ExamScreen extends StatefulWidget {
  /// null なら両科目（本番と同じ）。'法規' / '無線工学' ならその科目だけ
  final String? subject;
  const ExamScreen({super.key, this.subject});

  @override
  State<ExamScreen> createState() => _ExamScreenState();
}

class _ExamScreenState extends State<ExamScreen> {
  static const perSubject = 12;

  /// 本番は2科目で60分なので、1科目だけなら半分の30分
  Duration get examTime =>
      Duration(minutes: widget.subject == null ? 60 : 30);

  late final AppState app;
  late final List<Question> qs;
  late final DateTime endAt;
  final Map<int, int> answers = {};
  Timer? timer;
  late Duration left = examTime;
  int index = 0;
  bool finished = false;

  @override
  void initState() {
    super.initState();
    app = AppScope.read(context);
    // 本番と同じ出題：各科目からランダムに12問（subject 指定時はその科目だけ）
    qs = [
      for (final s in widget.subject == null ? Subjects.all : [widget.subject!])
        ...app.examSet(s, perSubject),
    ];
    endAt = DateTime.now().add(examTime);
    timer = Timer.periodic(const Duration(seconds: 1), (_) {
      final l = endAt.difference(DateTime.now());
      if (l <= Duration.zero) {
        _finish();
      } else if (mounted) {
        setState(() => left = l);
      }
    });
  }

  @override
  void dispose() {
    timer?.cancel();
    app.tts.stop();
    super.dispose();
  }

  String get title =>
      widget.subject == null ? '模擬試験' : '模擬試験｜${widget.subject}';

  String get clock {
    final m = left.inMinutes.toString().padLeft(2, '0');
    final s = (left.inSeconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  Future<void> _confirmFinish() async {
    final rest = qs.length - answers.length;
    if (rest > 0) {
      final ok = await showDialog<bool>(
        context: context,
        builder: (c) => AlertDialog(
          content: Text('未回答が$rest問あります。採点しますか？'),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: const Text('問題に戻る')),
            TextButton(
                onPressed: () => Navigator.pop(c, true),
                child: const Text('採点する')),
          ],
        ),
      );
      if (ok != true) return;
    }
    _finish();
  }

  void _finish() {
    if (finished || !mounted) return;
    finished = true;
    timer?.cancel();
    app.tts.stop();

    var h = 0, ht = 0, k = 0, kt = 0;
    final wrong = <Question>[];
    for (var i = 0; i < qs.length; i++) {
      final q = qs[i];
      final ok = answers[i] == q.answer;
      if (q.subject == Subjects.houki) {
        ht++;
        if (ok) h++;
      } else {
        kt++;
        if (ok) k++;
      }
      app.record(q, ok);
      if (!ok) wrong.add(q);
    }
    final r = ExamResult(
      at: DateTime.now(),
      houki: h,
      houkiTotal: ht,
      kougaku: k,
      kougakuTotal: kt,
    );
    // 間違えた問題を分野ごとにまとめる（結果画面から分野別に復習できるように）
    final byCategory = <String, List<Question>>{};
    for (final q in wrong) {
      byCategory.putIfAbsent('${q.subject}｜${q.category}', () => []).add(q);
    }
    app.addExam(r);
    Navigator.of(context).pushReplacement(MaterialPageRoute(
      builder: (_) =>
          ExamResultScreen(result: r, wrong: wrong, byCategory: byCategory),
    ));
  }

  @override
  Widget build(BuildContext context) {
    if (qs.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: Text(title)),
        body: const Center(child: Text('問題がありません')),
      );
    }
    final q = qs[index];
    final chosen = answers[index];

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(clock,
                  style: TextStyle(
                      color: left.inMinutes < 5 ? AppColors.amber : Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      fontFeatures: const [FontFeature.tabularFigures()])),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          SizedBox(
            height: 52,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              itemCount: qs.length,
              separatorBuilder: (_, __) => const SizedBox(width: 6),
              itemBuilder: (_, i) {
                final current = i == index;
                final done = answers.containsKey(i);
                return InkWell(
                  onTap: () => setState(() => index = i),
                  borderRadius: BorderRadius.circular(18),
                  child: Container(
                    width: 36,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: current
                          ? AppColors.panel
                          : (done ? AppColors.amber : Colors.white),
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: AppColors.line),
                    ),
                    child: Text('${i + 1}',
                        style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: current ? Colors.white : AppColors.ink)),
                  ),
                );
              },
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
              children: [
                Row(
                  children: [
                    Expanded(
                        child: QuestionHeader(
                            index: index, total: qs.length, q: q)),
                    IconButton(
                      tooltip: '問題を読み上げる',
                      icon: const Icon(Icons.volume_up),
                      onPressed: () =>
                          app.tts.speakVoice(TtsService.questionVoice(q)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                QuestionBody(q: q),
                const SizedBox(height: 16),
                for (var i = 0; i < q.choices.length; i++)
                  ChoiceTile(
                    number: i + 1,
                    text: q.choices[i],
                    state: chosen == i + 1
                        ? ChoiceState.selected
                        : ChoiceState.idle,
                    onTap: () => setState(() => answers[index] = i + 1),
                  ),
              ],
            ),
          ),
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
                    child: OutlinedButton(
                      onPressed:
                          index > 0 ? () => setState(() => index--) : null,
                      child: const Text('前へ'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: index < qs.length - 1
                          ? () => setState(() => index++)
                          : null,
                      child: const Text('次へ'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              FilledButton(
                onPressed: _confirmFinish,
                child: Text('採点する（${answers.length}/${qs.length}問回答）'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ExamResultScreen extends StatelessWidget {
  final ExamResult result;
  final List<Question> wrong;

  /// 「科目｜分野」→ 間違えた問題
  final Map<String, List<Question>> byCategory;
  const ExamResultScreen(
      {super.key,
      required this.result,
      required this.wrong,
      this.byCategory = const {}});

  Widget _subjectRow(String name, int c, int t, bool pass) {
    final score = t == 12 ? '（${c * 5}点）' : '';
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Text(name, style: const TextStyle(fontSize: 16)),
          const Spacer(),
          Text('$c / $t$score',
              style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  fontFeatures: [FontFeature.tabularFigures()])),
          const SizedBox(width: 12),
          Text(pass ? '合格' : '不合格',
              style: TextStyle(
                  color: pass ? AppColors.correct : AppColors.wrong,
                  fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('模擬試験の結果')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const SizedBox(height: 8),
          Center(
            child: Text(result.pass ? '合格ライン到達' : 'あと少し',
                style: TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w800,
                    color: result.pass ? AppColors.correct : AppColors.ink)),
          ),
          const SizedBox(height: 4),
          Center(
            child: Text(
                result.singleSubject
                    ? '12問中8問（40点）以上で合格'
                    : '両科目とも12問中8問（40点）以上で合格',
                style: const TextStyle(color: AppColors.muted, fontSize: 13)),
          ),
          const SizedBox(height: 20),
          if (result.houkiTotal > 0)
            _subjectRow(
                '法規', result.houki, result.houkiTotal, result.houkiPass),
          if (result.kougakuTotal > 0)
            _subjectRow('無線工学', result.kougaku, result.kougakuTotal,
                result.kougakuPass),
          const SizedBox(height: 16),
          if (byCategory.isNotEmpty) ...[
            const Text('間違えた分野（押すとその分野を復習）',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
            const SizedBox(height: 8),
            for (final e in (byCategory.entries.toList()
              ..sort((a, b) => b.value.length.compareTo(a.value.length))))
              _WeakCategoryTile(label: e.key, wrong: e.value),
            const SizedBox(height: 16),
          ],
          if (wrong.isNotEmpty)
            FilledButton(
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute(
                  builder: (_) =>
                      QuizScreen(questions: wrong, title: '模擬試験の復習'),
                ),
              ),
              child: Text('間違えた${wrong.length}問を復習'),
            ),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('ホームに戻る'),
          ),
          if (wrong.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('間違えた問題の解説',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
            const SizedBox(height: 8),
            for (final q in wrong)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ExplanationCard(q: q, showQuestion: true),
              ),
          ],
        ],
      ),
    );
  }
}

/// 間違えた分野のカード。押すとその分野を復習できる。
/// 「この試験で間違えた問題だけ」と「この分野の全問」を選べる。
class _WeakCategoryTile extends StatelessWidget {
  final String label;
  final List<Question> wrong;
  const _WeakCategoryTile({required this.label, required this.wrong});

  @override
  Widget build(BuildContext context) {
    final app = AppScope.read(context);
    final parts = label.split('｜');
    final all = app.subjectSet(parts[0], category: parts.length > 1 ? parts[1] : null);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF6E5),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.amber),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(14, 10, 10, 10),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label,
                      style: const TextStyle(
                          fontSize: 15, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 2),
                  Text('${wrong.length}問まちがい・この分野は全${all.length}問',
                      style: const TextStyle(
                          color: AppColors.muted, fontSize: 12)),
                ],
              ),
            ),
            TextButton(
              style: TextButton.styleFrom(minimumSize: const Size(0, 40)),
              onPressed: () => Navigator.of(context).push(MaterialPageRoute(
                builder: (_) =>
                    QuizScreen(questions: List.of(wrong), title: '$label の復習'),
              )),
              child: Text('この${wrong.length}問'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                  minimumSize: const Size(0, 40),
                  padding: const EdgeInsets.symmetric(horizontal: 14)),
              onPressed: all.isEmpty
                  ? null
                  : () => Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => QuizScreen(
                            questions: all, title: label, trackRange: true),
                      )),
              child: const Text('分野ごと'),
            ),
          ],
        ),
      ),
    );
  }
}
