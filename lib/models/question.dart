class Subjects {
  static const houki = '法規';
  static const kougaku = '無線工学';
  static const all = [houki, kougaku];
}

class Question {
  final String id;
  final String subject;
  final String category;
  final String question;
  final List<String> choices;

  /// 正解の番号（1〜4）。試験の選択肢番号と同じく1始まり。
  final int answer;
  final String explanation;
  final String? image;

  /// 読み上げ専用の文（記号や型式名が読みにくいときに使う）。無ければ question を読む。
  final String? readQuestion;
  final String? readExplanation;
  final String source;

  const Question({
    required this.id,
    required this.subject,
    required this.category,
    required this.question,
    required this.choices,
    required this.answer,
    required this.explanation,
    this.image,
    this.readQuestion,
    this.readExplanation,
    this.source = '',
  });

  factory Question.fromJson(Map<String, dynamic> j) => Question(
        id: j['id'].toString(),
        subject: (j['subject'] ?? '').toString(),
        category: (j['category'] ?? '').toString(),
        question: (j['question'] ?? '').toString(),
        choices: ((j['choices'] as List?) ?? const [])
            .map((e) => e.toString())
            .toList(),
        answer: (j['answer'] as num?)?.toInt() ?? 0,
        explanation: (j['explanation'] ?? '').toString(),
        image: j['image'] as String?,
        readQuestion: j['readQuestion'] as String?,
        readExplanation: j['readExplanation'] as String?,
        source: (j['source'] ?? '').toString(),
      );

  bool get isValid =>
      question.isNotEmpty &&
      choices.length >= 2 &&
      answer >= 1 &&
      answer <= choices.length;

  String get correctChoice => choices[answer - 1];
}
