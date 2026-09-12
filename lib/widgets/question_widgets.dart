import 'package:flutter/material.dart';

import '../models/question.dart';
import '../theme.dart';

enum ChoiceState { idle, selected, correct, wrong, dimmed }

class QuestionHeader extends StatelessWidget {
  final int index;
  final int total;
  final Question q;
  const QuestionHeader(
      {super.key, required this.index, required this.total, required this.q});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text('${index + 1} / $total',
            style: const TextStyle(
                color: AppColors.muted,
                fontWeight: FontWeight.w600,
                fontFeatures: [FontFeature.tabularFigures()])),
        const SizedBox(width: 10),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: AppColors.panel,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            q.category.isEmpty ? q.subject : '${q.subject}｜${q.category}',
            style: const TextStyle(color: Colors.white, fontSize: 12),
          ),
        ),
      ],
    );
  }
}

class QuestionBody extends StatelessWidget {
  final Question q;
  const QuestionBody({super.key, required this.q});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(q.question,
            style: const TextStyle(
                fontSize: 18, height: 1.65, color: AppColors.ink)),
        if (q.image != null)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Image.asset(q.image!, fit: BoxFit.contain),
          ),
      ],
    );
  }
}

class ChoiceTile extends StatelessWidget {
  final int number;
  final String text;
  final ChoiceState state;
  final VoidCallback? onTap;

  const ChoiceTile({
    super.key,
    required this.number,
    required this.text,
    required this.state,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    Color border = AppColors.line;
    Color bg = Colors.white;
    Color numBg = AppColors.paper;
    Color numFg = AppColors.ink;
    Color textColor = AppColors.ink;
    IconData? mark;

    switch (state) {
      case ChoiceState.idle:
        break;
      case ChoiceState.selected:
        border = AppColors.amber;
        bg = const Color(0xFFFFF6E5);
        numBg = AppColors.amber;
        break;
      case ChoiceState.correct:
        border = AppColors.correct;
        bg = const Color(0xFFE9F6EF);
        numBg = AppColors.correct;
        numFg = Colors.white;
        mark = Icons.check_circle;
        break;
      case ChoiceState.wrong:
        border = AppColors.wrong;
        bg = const Color(0xFFFBECEA);
        numBg = AppColors.wrong;
        numFg = Colors.white;
        mark = Icons.cancel;
        break;
      case ChoiceState.dimmed:
        textColor = AppColors.muted;
        break;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: bg,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: BorderSide(color: border, width: 1.5),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 28,
                  height: 28,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(color: numBg, shape: BoxShape.circle),
                  child: Text('$number',
                      style: TextStyle(
                          color: numFg, fontWeight: FontWeight.w700)),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 3),
                    child: Text(text,
                        style: TextStyle(
                            fontSize: 16, height: 1.5, color: textColor)),
                  ),
                ),
                if (mark != null) ...[
                  const SizedBox(width: 8),
                  Icon(mark, color: border),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class ExplanationCard extends StatelessWidget {
  final Question q;
  final bool? correct; // null＝ながら聞きなど正誤なし
  final bool showQuestion;
  const ExplanationCard(
      {super.key, required this.q, this.correct, this.showQuestion = false});

  @override
  Widget build(BuildContext context) {
    final color = correct == false ? AppColors.wrong : AppColors.correct;
    final title = switch (correct) {
      true => '正解',
      false => '不正解　正解は ${q.answer} 番',
      null => '正解は ${q.answer} 番',
    };
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border(left: BorderSide(color: color, width: 4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (showQuestion) ...[
            Text(q.question,
                style: const TextStyle(
                    fontSize: 14, height: 1.6, color: AppColors.muted)),
            const SizedBox(height: 8),
          ],
          Text(showQuestion ? '${q.answer}．${q.correctChoice}' : title,
              style: TextStyle(
                  color: color, fontSize: 16, fontWeight: FontWeight.w700)),
          if (q.explanation.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(q.explanation,
                style: const TextStyle(
                    fontSize: 15, height: 1.65, color: AppColors.ink)),
          ],
          if (q.source.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text('出典：${q.source}',
                style: const TextStyle(fontSize: 11, color: AppColors.muted)),
          ],
        ],
      ),
    );
  }
}

class ReadButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  const ReadButton({super.key, required this.label, this.onPressed});

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: onPressed,
      icon: const Icon(Icons.volume_up, size: 18),
      label: Text(label),
    );
  }
}
