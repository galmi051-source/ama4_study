import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models/question.dart';
import '../services/tts_service.dart';
import '../theme.dart';
import '../widgets/s_meter.dart';
import 'exam_screen.dart';
import 'listen_screen.dart';
import 'quiz_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final app = AppScope.of(context);
    final review = app.reviewDue().length;
    final fresh = app.unseen().length;
    final todayCount = review + (fresh < 10 ? fresh : 10);
    final weak = app.weak();
    final last = app.lastExam;
    final houkiCount = app.repo.bySubject(Subjects.houki).length;
    final kougakuCount = app.repo.bySubject(Subjects.kougaku).length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('4アマ ながら学習'),
        actions: [
          IconButton(
            tooltip: '設定',
            icon: const Icon(Icons.tune),
            onPressed: () => showSettingsSheet(context),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
        children: [
          SMeterPanel(
            houki: app.expectedRate(Subjects.houki),
            kougaku: app.expectedRate(Subjects.kougaku),
            footer: last == null
                ? '収録 法規$houkiCount問・無線工学$kougakuCount問'
                : '前回の模擬試験　法規 ${last.houki}/${last.houkiTotal}　'
                    '工学 ${last.kougaku}/${last.kougakuTotal}　'
                    '${last.pass ? "合格ライン" : "不合格"}',
          ),
          if (app.repo.warnings.isNotEmpty) ...[
            const SizedBox(height: 12),
            _WarningCard(messages: app.repo.warnings),
          ],
          const SizedBox(height: 16),
          _ActionTile(
            primary: true,
            icon: Icons.play_arrow_rounded,
            title: '今日の復習',
            subtitle: todayCount == 0
                ? '今日の分は終わりました'
                : '$todayCount問（復習$review・新しい問題${todayCount - review}）',
            onTap: todayCount == 0
                ? null
                : () => _push(context,
                    QuizScreen(questions: app.todaySet(), title: '今日の復習')),
          ),
          _ActionTile(
            icon: Icons.headphones_rounded,
            title: 'ながら聞き',
            subtitle: '問題・正解・解説を続けて読み上げ',
            onTap: () => showRangeSheet(context, listen: true),
          ),
          _ActionTile(
            icon: Icons.list_alt_rounded,
            title: '分野を選んで解く',
            subtitle: app.store.lastRange == null
                ? '法規・無線工学の分野ごと'
                : '前回：${app.store.lastRange}　${app.store.lastRangeDone}/${app.store.lastRangeTotal}問まで'
                    '${app.store.lastStudied(app.repo.all.map((q) => q.id)) == null ? '' : '（${formatLast(app.store.lastStudied(app.repo.all.map((q) => q.id))!)}）'}',
            onTap: () => showRangeSheet(context, listen: false),
          ),
          _ActionTile(
            icon: Icons.replay_rounded,
            title: '苦手な問題',
            subtitle: weak.isEmpty ? 'まだありません' : '${weak.length}問',
            onTap: weak.isEmpty
                ? null
                : () => _push(
                    context, QuizScreen(questions: weak, title: '苦手な問題')),
          ),
          _ActionTile(
            icon: Icons.timer_outlined,
            title: '模擬試験',
            subtitle: '法規12問・無線工学12問／60分',
            onTap: () => _push(context, const ExamScreen()),
          ),
        ],
      ),
    );
  }
}

void _push(BuildContext context, Widget page) {
  Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;
  final bool primary;

  const _ActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
    this.primary = false,
  });

  @override
  Widget build(BuildContext context) {
    final fg = primary ? Colors.white : AppColors.ink;
    final disabled = onTap == null;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Opacity(
        opacity: disabled ? 0.55 : 1,
        child: Material(
          color: primary ? AppColors.panel : Colors.white,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: onTap,
            child: Padding(
              padding: EdgeInsets.symmetric(
                  horizontal: 16, vertical: primary ? 20 : 14),
              child: Row(
                children: [
                  Icon(icon,
                      size: primary ? 34 : 26,
                      color: primary ? AppColors.amber : AppColors.panel),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(title,
                            style: TextStyle(
                                color: fg,
                                fontSize: primary ? 19 : 16,
                                fontWeight: FontWeight.w700)),
                        const SizedBox(height: 2),
                        Text(subtitle,
                            style: TextStyle(
                                color: primary
                                    ? Colors.white70
                                    : AppColors.muted,
                                fontSize: 13)),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right,
                      color: primary ? Colors.white54 : AppColors.line),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _WarningCard extends StatelessWidget {
  final List<String> messages;
  const _WarningCard({required this.messages});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF6E5),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.amber),
      ),
      child: Text(
        '読み込めなかった問題があります\n${messages.take(5).join('\n')}'
        '${messages.length > 5 ? '\nほか${messages.length - 5}件' : ''}',
        style: const TextStyle(fontSize: 12, height: 1.5),
      ),
    );
  }
}

/// 出題範囲を選ぶシート（ながら聞き／分野別の両方で使う）
/// 出題範囲を選ぶシート（ながら聞き／分野別の両方で使う）。
/// 最初に「今日の復習・苦手・すべて」と科目（法規／無線工学）を出し、
/// 科目を選ぶとその分野の一覧に切り替わる（全部を一度に並べると長くなるため）。
void showRangeSheet(BuildContext context, {required bool listen}) {
  final app = AppScope.read(context);
  String? subject; // 選んだ科目。null なら最初の画面

  showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    isScrollControlled: true,
    builder: (ctx) => StatefulBuilder(
      builder: (ctx, setSheet) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        builder: (ctx, controller) {
          final entries = <(String, List<Question>)>[];
          if (subject == null) {
            entries.addAll([
              ('今日の復習', app.todaySet()),
              ('苦手な問題', app.weak()),
              ('すべて（シャッフル）', List.of(app.repo.all)..shuffle()),
            ]);
          } else {
            entries.add(('$subject（すべて）', app.subjectSet(subject!)));
            for (final c in app.repo.categories(subject!)) {
              entries.add(('$subject｜$c', app.subjectSet(subject!, category: c)));
            }
          }
          return ListView(
            controller: controller,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(8, 0, 20, 8),
                child: Row(
                  children: [
                    if (subject != null)
                      IconButton(
                        icon: const Icon(Icons.arrow_back),
                        tooltip: '科目の選択に戻る',
                        onPressed: () => setSheet(() => subject = null),
                      )
                    else
                      const SizedBox(width: 12),
                    Text(
                      subject == null
                          ? (listen ? 'ながら聞きの範囲' : '解く範囲')
                          : '$subject の分野',
                      style: const TextStyle(
                          fontSize: 17, fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
              ),
              if (subject == null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
                  child: Row(
                    children: [
                      for (final s in Subjects.all) ...[
                        Expanded(
                          child: _SubjectButton(
                            subject: s,
                            count: app.repo.bySubject(s).length,
                            last: app.store.lastStudied(
                                app.repo.bySubject(s).map((q) => q.id)),
                            onTap: () => setSheet(() => subject = s),
                          ),
                        ),
                        if (s != Subjects.all.last) const SizedBox(width: 10),
                      ],
                    ],
                  ),
                ),
              for (final (label, qs) in entries)
                _RangeTile(
                  label: label,
                  qs: qs,
                  listen: listen,
                  onTap: () {
                    Navigator.pop(ctx);
                    _push(
                      context,
                      listen
                          ? ListenScreen(questions: qs, title: label)
                          : QuizScreen(
                              questions: qs, title: label, trackRange: true),
                    );
                  },
                ),
              const SizedBox(height: 16),
            ],
          );
        },
      ),
    ),
  );
}

class _SubjectButton extends StatelessWidget {
  final String subject;
  final int count;
  final DateTime? last;
  final VoidCallback onTap;
  const _SubjectButton(
      {required this.subject,
      required this.count,
      required this.last,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.panel,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(subject,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 17,
                            fontWeight: FontWeight.w700)),
                    const SizedBox(height: 2),
                    Text(
                      '$count問${last == null ? '' : '・${formatLast(last!)}'}',
                      style:
                          const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.white54),
            ],
          ),
        ),
      ),
    );
  }
}

class _RangeTile extends StatelessWidget {
  final String label;
  final List<Question> qs;
  final bool listen;
  final VoidCallback onTap;
  const _RangeTile(
      {required this.label,
      required this.qs,
      required this.listen,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    final app = AppScope.read(context);
    final isLast = !listen && label == app.store.lastRange;
    final ids = qs.map((q) => q.id);
    final last = app.store.lastStudied(ids);
    String? sub;
    if (!listen && qs.isNotEmpty) {
      // 解いた問題数・最後に解いた日・前回どこまで進んだか
      sub = '解いた ${app.store.doneCount(ids)}/${qs.length}問';
      sub += last == null ? '　未着手' : '　最後：${formatLast(last)}';
      if (isLast) {
        sub += '　← 前回ここまで（${app.store.lastRangeDone}/${app.store.lastRangeTotal}問目）';
      }
    }
    return ListTile(
      enabled: qs.isNotEmpty,
      selected: isLast,
      selectedTileColor: const Color(0xFFFFF6E5),
      title: Text(label),
      subtitle: sub == null
          ? null
          : Text(sub,
              style: TextStyle(
                  fontSize: 12,
                  color: isLast ? AppColors.ink : AppColors.muted)),
      trailing: Text('${qs.length}問',
          style: const TextStyle(color: AppColors.muted)),
      onTap: onTap,
    );
  }
}

/// 最後に解いた日の表示（今日／昨日／N日前／M/D）
String formatLast(DateTime t) {
  final now = DateTime.now();
  final d0 = DateTime(now.year, now.month, now.day);
  final d1 = DateTime(t.year, t.month, t.day);
  final days = d0.difference(d1).inDays;
  if (days <= 0) return '今日';
  if (days == 1) return '昨日';
  if (days < 7) return '$days日前';
  return '${t.month}/${t.day}';
}

void showSettingsSheet(BuildContext context) {
  final app = AppScope.read(context);
  showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    builder: (ctx) => StatefulBuilder(
      builder: (ctx, setSheet) {
        final s = app.store;
        return Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('読み上げの速さ　${s.rate.toStringAsFixed(2)}'),
              Slider(
                value: s.rate,
                min: 0.2,
                max: 0.8,
                divisions: 12,
                onChanged: (v) {
                  app.updateSettings(rate: v);
                  setSheet(() {});
                },
              ),
              Text('ながら聞きで考える時間　${s.thinkSec}秒'),
              Slider(
                value: s.thinkSec.toDouble(),
                min: 0,
                max: 10,
                divisions: 10,
                onChanged: (v) {
                  app.updateSettings(thinkSec: v.round());
                  setSheet(() {});
                },
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('問題を開いたら自動で読み上げる'),
                value: s.autoRead,
                onChanged: (v) {
                  app.updateSettings(autoRead: v);
                  setSheet(() {});
                },
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 44)),
                    onPressed: () => app.tts.speakVoice(TtsService.sampleVoice),
                    icon: const Icon(Icons.volume_up, size: 18),
                    label: const Text('試しに読む'),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () async {
                      final ok = await showDialog<bool>(
                        context: ctx,
                        builder: (c) => AlertDialog(
                          content: const Text('学習記録と模擬試験の結果をすべて消します。'),
                          actions: [
                            TextButton(
                                onPressed: () => Navigator.pop(c, false),
                                child: const Text('やめる')),
                            TextButton(
                                onPressed: () => Navigator.pop(c, true),
                                child: const Text('消す',
                                    style:
                                        TextStyle(color: AppColors.wrong))),
                          ],
                        ),
                      );
                      if (ok == true) app.resetProgress();
                    },
                    child: const Text('学習記録を消す',
                        style: TextStyle(color: AppColors.wrong)),
                  ),
                ],
              ),
              if (kIsWeb) ...[
                const Divider(height: 24),
                const _OfflineDownload(),
              ],
            ],
          ),
        );
      },
    ),
  );
}

/// ブラウザ版：電波の無い場所でも聞けるように音声ファイルを全部キャッシュする。
/// 通常は再生した音声から順にキャッシュされる（Service Worker）が、
/// 電車に乗る前などにまとめて取り込みたいとき用。
class _OfflineDownload extends StatefulWidget {
  const _OfflineDownload();

  @override
  State<_OfflineDownload> createState() => _OfflineDownloadState();
}

class _OfflineDownloadState extends State<_OfflineDownload> {
  int done = 0;
  int total = 0;
  bool running = false;
  String? message;

  Future<void> _start() async {
    final app = AppScope.read(context);
    setState(() {
      running = true;
      message = null;
      done = 0;
      total = app.tts.voicePaths.length;
    });
    try {
      await app.tts.prefetchAll((d, t) {
        if (!mounted) return;
        setState(() {
          done = d;
          total = t;
        });
      });
      if (mounted) setState(() => message = '完了：$total 個の音声をこの端末に保存しました。');
    } catch (e) {
      if (mounted) setState(() => message = '途中で失敗しました（$e）。電波の良い所でもう一度試してください。');
    } finally {
      if (mounted) setState(() => running = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final app = AppScope.read(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('オフラインで使う', style: TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 4),
        Text(
          '音声は一度再生すると端末に残ります。まとめて取り込むと電波の無い場所でも全問聞けます'
          '（${app.tts.voiceCount} ファイル・約35MB。Wi-Fi 推奨）。',
          style: const TextStyle(color: AppColors.muted, fontSize: 12),
        ),
        const SizedBox(height: 8),
        if (running) ...[
          LinearProgressIndicator(value: total == 0 ? null : done / total),
          const SizedBox(height: 4),
          Text('$done / $total', style: const TextStyle(fontSize: 12)),
        ] else
          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(minimumSize: const Size(0, 44)),
            onPressed: _start,
            icon: const Icon(Icons.download, size: 18),
            label: const Text('音声をまとめてダウンロード'),
          ),
        if (message != null)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(message!, style: const TextStyle(fontSize: 12)),
          ),
      ],
    );
  }
}
