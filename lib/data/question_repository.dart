import 'dart:convert';

import 'package:flutter/services.dart';

import '../models/question.dart';

/// assets/questions/ にある .json をすべて読み込む。
/// 問題を増やすときは JSON ファイルをそのフォルダに置いてビルドし直すだけでよい。
class QuestionRepository {
  final List<Question> _all = [];
  final List<String> warnings = [];

  List<Question> get all => List.unmodifiable(_all);

  Future<void> load() async {
    final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
    final paths = manifest
        .listAssets()
        .where((p) => p.startsWith('assets/questions/') && p.endsWith('.json'))
        .toList()
      ..sort();

    final seen = <String>{};
    for (final path in paths) {
      try {
        final decoded = jsonDecode(await rootBundle.loadString(path));
        final List<dynamic> list =
            decoded is List ? decoded : (decoded['questions'] as List);
        for (final item in list) {
          final q = Question.fromJson(Map<String, dynamic>.from(item as Map));
          if (!q.isValid) {
            warnings.add('${q.id}：正解番号か選択肢が未設定のため除外（$path）');
            continue;
          }
          if (!seen.add(q.id)) {
            warnings.add('${q.id}：IDが重複しているため除外（$path）');
            continue;
          }
          _all.add(q);
        }
      } catch (e) {
        warnings.add('$path を読み込めませんでした：$e');
      }
    }
  }

  List<Question> bySubject(String subject) =>
      _all.where((q) => q.subject == subject).toList();

  List<String> categories(String subject) {
    final result = <String>[];
    for (final q in _all) {
      if (q.subject == subject && !result.contains(q.category)) {
        result.add(q.category);
      }
    }
    return result;
  }
}
