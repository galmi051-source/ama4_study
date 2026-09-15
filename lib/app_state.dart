import 'package:flutter/widgets.dart';

import 'data/question_repository.dart';
import 'models/question.dart';
import 'services/progress_store.dart';
import 'services/tts_service.dart';

class AppState extends ChangeNotifier {
  final repo = QuestionRepository();
  final store = ProgressStore();
  final tts = TtsService();

  Future<void> load() async {
    await repo.load();
    await store.load();
    await tts.loadVoices();
    await tts.setRate(store.rate);
  }

  void record(Question q, bool correct) {
    store.record(q.id, correct);
    notifyListeners();
  }

  // ---- 出題セット ----

  List<Question> reviewDue() {
    final now = DateTime.now().millisecondsSinceEpoch;
    final list = repo.all.where((q) {
      final s = store.stat(q.id);
      return !s.isNew && s.due <= now;
    }).toList();
    list.sort((a, b) => store.stat(a.id).due.compareTo(store.stat(b.id).due));
    return list;
  }

  List<Question> unseen() =>
      repo.all.where((q) => store.stat(q.id).isNew).toList();

  /// 期限が来た復習 ＋ 未学習から最大 newLimit 問。
  List<Question> todaySet({int newLimit = 10}) {
    final fresh = unseen()..shuffle();
    return [...reviewDue(), ...fresh.take(newLimit)];
  }

  List<Question> weak() {
    final list = repo.all.where((q) {
      final s = store.stat(q.id);
      return s.wrong > 0 && s.box < 2;
    }).toList();
    list.shuffle();
    return list;
  }

  /// まだ解いていない問題を先に、解いたことのある問題を後に（それぞれシャッフル）。
  /// 途中でやめても、次に開いたときに続きから未学習の問題が出る。
  List<Question> subjectSet(String subject, {String? category}) {
    final list = repo
        .bySubject(subject)
        .where((q) => category == null || q.category == category)
        .toList();
    final fresh = list.where((q) => store.stat(q.id).isNew).toList()..shuffle();
    final seen = list.where((q) => !store.stat(q.id).isNew).toList()..shuffle();
    return [...fresh, ...seen];
  }

  /// 「分野を選んで解く」の進み具合を記録（ホームと範囲選択に表示）
  void markRange(String label, int done, int total) {
    store.setLastRange(label, done, total);
    notifyListeners();
  }

  /// 12問出題されたら何割取れそうか（0〜1）。未学習は4択の当てずっぽう＝0.25。
  double expectedRate(String subject) {
    const byBox = [0.25, 0.5, 0.75, 0.9, 0.95, 0.98];
    final qs = repo.bySubject(subject);
    if (qs.isEmpty) return 0;
    var sum = 0.0;
    for (final q in qs) {
      final s = store.stat(q.id);
      sum += s.isNew ? 0.25 : byBox[s.box];
    }
    return sum / qs.length;
  }

  ExamResult? get lastExam => store.exams.isEmpty ? null : store.exams.last;

  // ---- 設定 ----

  void updateSettings({double? rate, int? thinkSec, bool? autoRead}) {
    if (rate != null) {
      store.rate = rate;
      tts.setRate(rate);
    }
    if (thinkSec != null) store.thinkSec = thinkSec;
    if (autoRead != null) store.autoRead = autoRead;
    store.saveSettings();
    notifyListeners();
  }

  void addExam(ExamResult r) {
    store.addExam(r);
    notifyListeners();
  }

  void resetProgress() {
    store.reset();
    notifyListeners();
  }
}

class AppScope extends InheritedNotifier<AppState> {
  const AppScope({super.key, required AppState state, required super.child})
      : super(notifier: state);

  /// 変更があると再描画される（ホーム画面用）
  static AppState of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<AppScope>()!.notifier!;

  /// 再描画を伴わない参照（出題画面・initState用）
  static AppState read(BuildContext context) =>
      context.getInheritedWidgetOfExactType<AppScope>()!.notifier!;
}
