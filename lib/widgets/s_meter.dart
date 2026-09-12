import 'package:flutter/material.dart';

import '../theme.dart';

/// 無線機のSメーター風に「12問中何問取れそうか」を表示する。
/// 12コマ＝12問。8コマ目の右に合格ラインの目盛りを入れている。
class SMeterPanel extends StatelessWidget {
  final double houki;
  final double kougaku;
  final String? footer;

  const SMeterPanel({
    super.key,
    required this.houki,
    required this.kougaku,
    this.footer,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: BoxDecoration(
        color: AppColors.panelDeep,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Text('合格見込み',
                  style: TextStyle(
                      color: AppColors.amber,
                      fontSize: 14,
                      fontWeight: FontWeight.w700)),
              Spacer(),
              Text('12問中8問で合格',
                  style: TextStyle(color: Colors.white54, fontSize: 12)),
            ],
          ),
          const SizedBox(height: 12),
          _MeterRow(label: '法規', rate: houki),
          const SizedBox(height: 10),
          _MeterRow(label: '工学', rate: kougaku),
          const SizedBox(height: 6),
          const _ScaleLabels(),
          if (footer != null) ...[
            const SizedBox(height: 10),
            Text(footer!,
                style: const TextStyle(color: Colors.white70, fontSize: 12)),
          ],
        ],
      ),
    );
  }
}

const _labelWidth = 40.0;
const _valueWidth = 56.0;
const _passIndex = 8;

List<Widget> _cells(Widget Function(int i) build, {bool tick = true}) {
  final out = <Widget>[];
  for (var i = 0; i < 12; i++) {
    if (i == _passIndex) {
      out.add(tick
          ? Container(width: 2, height: 24, color: Colors.white70)
          : const SizedBox(width: 2));
      out.add(const SizedBox(width: 2));
    }
    out.add(Expanded(child: build(i)));
    if (i != 11 && i != _passIndex - 1) out.add(const SizedBox(width: 3));
  }
  return out;
}

class _MeterRow extends StatelessWidget {
  final String label;
  final double rate;
  const _MeterRow({required this.label, required this.rate});

  @override
  Widget build(BuildContext context) {
    final expected = rate * 12;
    final lit = expected.round();
    return Row(
      children: [
        SizedBox(
          width: _labelWidth,
          child: Text(label,
              style: const TextStyle(color: Colors.white70, fontSize: 13)),
        ),
        Expanded(
          child: Row(
            children: _cells((i) => Container(
                  height: 18,
                  decoration: BoxDecoration(
                    color: i < lit ? AppColors.amber : AppColors.amberDim,
                    borderRadius: BorderRadius.circular(2),
                  ),
                )),
          ),
        ),
        SizedBox(
          width: _valueWidth,
          child: Text(
            '${expected.toStringAsFixed(1)}問',
            textAlign: TextAlign.right,
            style: TextStyle(
              color: expected >= _passIndex ? AppColors.amber : Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w700,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ),
      ],
    );
  }
}

class _ScaleLabels extends StatelessWidget {
  const _ScaleLabels();

  static const _labels = {0: '1', 2: '3', 4: '5', 6: '7', 8: '9', 10: '+20'};

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const SizedBox(width: _labelWidth),
        Expanded(
          child: Row(
            children: _cells((i) => Text(
                  _labels[i] ?? '',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white38, fontSize: 10),
                ),
                tick: false),
          ),
        ),
        const SizedBox(width: _valueWidth),
      ],
    );
  }
}
