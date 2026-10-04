import 'dart:convert';
import 'dart:math';

import 'package:shared_preferences/shared_preferences.dart';

/// 1問ごとの記録。box は間隔反復の段階（0〜5）。
class QStat {
  int box;
  int correct;
  int wrong;

  /// 次に出題すべき日時（ミリ秒）。0 は未学習。
  int due;

  /// 最後に解いた日時（ミリ秒）。0 は未学習（古い記録には無い）。
  int last;

  QStat({this.box = 0, this.correct = 0, this.wrong = 0, this.due = 0, this.last = 0});

  bool get isNew => correct + wrong == 0;

  Map<String, dynamic> toJson() =>
      {'b': box, 'c': correct, 'w': wrong, 'd': due, 'l': last};

  factory QStat.fromJson(Map<String, dynamic> j) => QStat(
        box: (j['b'] as num?)?.toInt() ?? 0,
        correct: (j['c'] as num?)?.toInt() ?? 0,
        wrong: (j['w'] as num?)?.toInt() ?? 0,
        due: (j['d'] as num?)?.toInt() ?? 0,
        last: (j['l'] as num?)?.toInt() ?? 0,
      );
}

/// ある日にその範囲を何問解いたか
class StudyDay {
  final int day; // yyyymmdd
  int count;
  StudyDay({required this.day, required this.count});

  DateTime get date =>
      DateTime(day ~/ 10000, (day ~/ 100) % 100, day % 100);

  Map<String, dynamic> toJson() => {'d': day, 'n': count};
  factory StudyDay.fromJson(Map<String, dynamic> j) =>
      StudyDay(day: (j['d'] as num).toInt(), count: (j['n'] as num?)?.toInt() ?? 0);
}

class ExamResult {
  final DateTime at;
  final int houki;
  final int houkiTotal;
  final int kougaku;
  final int kougakuTotal;

  const ExamResult({
    required this.at,
    required this.houki,
    required this.houkiTotal,
    required this.kougaku,
    required this.kougakuTotal,
  });

  /// 12問中8問（3分の2）以上で科目合格。
  static bool passes(int correct, int total) =>
      total > 0 && correct * 3 >= total * 2;

  bool get houkiPass => passes(houki, houkiTotal);
  bool get kougakuPass => passes(kougaku, kougakuTotal);

  /// 出題された科目だけで判定（科目別の模擬試験では片方が 0 問になる）
  bool get pass =>
      (houkiTotal == 0 || houkiPass) && (kougakuTotal == 0 || kougakuPass);

  /// 1 科目だけの模擬試験か
  bool get singleSubject => houkiTotal == 0 || kougakuTotal == 0;

  Map<String, dynamic> toJson() => {
        'at': at.millisecondsSinceEpoch,
        'h': houki,
        'ht': houkiTotal,
        'k': kougaku,
        'kt': kougakuTotal,
      };

  factory ExamResult.fromJson(Map<String, dynamic> j) => ExamResult(
        at: DateTime.fromMillisecondsSinceEpoch((j['at'] as num).toInt()),
        houki: (j['h'] as num).toInt(),
        houkiTotal: (j['ht'] as num).toInt(),
        kougaku: (j['k'] as num).toInt(),
        kougakuTotal: (j['kt'] as num).toInt(),
      );
}

class ProgressStore {
  static const _kProgress = 'progress_v1';
  static const _kSettings = 'settings_v1';
  static const _kExams = 'exams_v1';
  static const _kHistory = 'history_v1';

  /// 正解を重ねるごとに次の出題までの日数が伸びる。
  static const intervalsDays = [0, 1, 3, 7, 14, 30];

  late SharedPreferences _prefs;
  final Map<String, QStat> _stats = {};
  final List<ExamResult> exams = [];

  double rate = 0.5;
  int thinkSec = 4;
  bool autoRead = true;

  /// 学習の履歴。範囲名 → [{d: 日付(yyyymmdd), n: 解いた問題数}]（新しい順）
  final Map<String, List<StudyDay>> _history = {};

  /// 「分野を選んで解く」で最後に解いた範囲と進み具合（どこまでやったか表示用）
  String? lastRange;
  int lastRangeDone = 0;
  int lastRangeTotal = 0;

  Future<void> load() async {
    _prefs = await SharedPreferences.getInstance();

    final p = _prefs.getString(_kProgress);
    if (p != null) {
      final m = jsonDecode(p) as Map<String, dynamic>;
      m.forEach((k, v) {
        _stats[k] = QStat.fromJson(Map<String, dynamic>.from(v as Map));
      });
    }

    final s = _prefs.getString(_kSettings);
    if (s != null) {
      final m = jsonDecode(s) as Map<String, dynamic>;
      rate = (m['rate'] as num?)?.toDouble() ?? rate;
      thinkSec = (m['thinkSec'] as num?)?.toInt() ?? thinkSec;
      autoRead = (m['autoRead'] as bool?) ?? autoRead;
      lastRange = m['lastRange'] as String?;
      lastRangeDone = (m['lastRangeDone'] as num?)?.toInt() ?? 0;
      lastRangeTotal = (m['lastRangeTotal'] as num?)?.toInt() ?? 0;
    }

    final h = _prefs.getString(_kHistory);
    if (h != null) {
      final m = jsonDecode(h) as Map<String, dynamic>;
      m.forEach((k, v) {
        _history[k] = (v as List)
            .map((x) => StudyDay.fromJson(Map<String, dynamic>.from(x as Map)))
            .toList();
      });
    }

    final e = _prefs.getString(_kExams);
    if (e != null) {
      exams.addAll((jsonDecode(e) as List)
          .map((x) => ExamResult.fromJson(Map<String, dynamic>.from(x as Map))));
    }
  }

  QStat stat(String id) => _stats[id] ?? QStat();

  void record(String id, bool correct) {
    final s = _stats.putIfAbsent(id, () => QStat());
    final now = DateTime.now();
    s.last = now.millisecondsSinceEpoch;
    if (correct) {
      s.correct++;
      s.box = min(s.box + 1, intervalsDays.length - 1);
      final today = DateTime(now.year, now.month, now.day);
      s.due = today.add(Duration(days: intervalsDays[s.box])).millisecondsSinceEpoch;
    } else {
      s.wrong++;
      s.box = 0;
      s.due = now.millisecondsSinceEpoch; // 間違えたら今日中にもう一度
    }
    _prefs.setString(
        _kProgress, jsonEncode(_stats.map((k, v) => MapEntry(k, v.toJson()))));
  }

  void saveSettings() {
    _prefs.setString(
        _kSettings,
        jsonEncode({
          'rate': rate,
          'thinkSec': thinkSec,
          'autoRead': autoRead,
          'lastRange': lastRange,
          'lastRangeDone': lastRangeDone,
          'lastRangeTotal': lastRangeTotal,
        }));
  }

  void setLastRange(String label, int done, int total) {
    lastRange = label;
    lastRangeDone = done;
    lastRangeTotal = total;
    saveSettings();
  }

  static int _dayKey(DateTime t) => t.year * 10000 + t.month * 100 + t.day;

  /// 範囲 label を今日 1 問解いたことを履歴に足す（同じ日は問題数を増やす）
  void addHistory(String label) {
    final today = _dayKey(DateTime.now());
    final list = _history.putIfAbsent(label, () => []);
    if (list.isNotEmpty && list.first.day == today) {
      list.first.count++;
    } else {
      list.insert(0, StudyDay(day: today, count: 1));
      if (list.length > 60) list.removeRange(60, list.length);
    }
    _prefs.setString(
        _kHistory,
        jsonEncode(_history
            .map((k, v) => MapEntry(k, v.map((e) => e.toJson()).toList()))));
  }

  /// 範囲 label の学習履歴（新しい順）
  List<StudyDay> history(String label) => List.unmodifiable(_history[label] ?? const []);

  /// 範囲の中で最後に解いた日時。一度も解いていなければ null
  DateTime? lastStudied(Iterable<String> ids) {
    var m = 0;
    for (final id in ids) {
      final l = stat(id).last;
      if (l > m) m = l;
    }
    return m == 0 ? null : DateTime.fromMillisecondsSinceEpoch(m);
  }

  /// 一度でも解いたことのある問題の数
  int doneCount(Iterable<String> ids) =>
      ids.where((id) => !stat(id).isNew).length;

  void addExam(ExamResult r) {
    exams.add(r);
    _prefs.setString(_kExams, jsonEncode(exams.map((e) => e.toJson()).toList()));
  }

  void reset() {
    _stats.clear();
    exams.clear();
    lastRange = null;
    lastRangeDone = 0;
    lastRangeTotal = 0;
    _history.clear();
    _prefs.remove(_kHistory);
    saveSettings();
    _prefs.remove(_kProgress);
    _prefs.remove(_kExams);
  }
}
