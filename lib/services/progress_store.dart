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

  QStat({this.box = 0, this.correct = 0, this.wrong = 0, this.due = 0});

  bool get isNew => correct + wrong == 0;

  Map<String, dynamic> toJson() => {'b': box, 'c': correct, 'w': wrong, 'd': due};

  factory QStat.fromJson(Map<String, dynamic> j) => QStat(
        box: (j['b'] as num?)?.toInt() ?? 0,
        correct: (j['c'] as num?)?.toInt() ?? 0,
        wrong: (j['w'] as num?)?.toInt() ?? 0,
        due: (j['d'] as num?)?.toInt() ?? 0,
      );
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
  bool get pass => houkiPass && kougakuPass;

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

  /// 正解を重ねるごとに次の出題までの日数が伸びる。
  static const intervalsDays = [0, 1, 3, 7, 14, 30];

  late SharedPreferences _prefs;
  final Map<String, QStat> _stats = {};
  final List<ExamResult> exams = [];

  double rate = 0.5;
  int thinkSec = 4;
  bool autoRead = true;

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
    _prefs.setString(_kSettings,
        jsonEncode({'rate': rate, 'thinkSec': thinkSec, 'autoRead': autoRead}));
  }

  void addExam(ExamResult r) {
    exams.add(r);
    _prefs.setString(_kExams, jsonEncode(exams.map((e) => e.toJson()).toList()));
  }

  void reset() {
    _stats.clear();
    exams.clear();
    _prefs.remove(_kProgress);
    _prefs.remove(_kExams);
  }
}
