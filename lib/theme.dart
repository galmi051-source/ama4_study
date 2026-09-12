import 'package:flutter/material.dart';

/// 無線機のフロントパネル（濃紺）と、表示窓のアンバー照明がモチーフ。
class AppColors {
  static const panel = Color(0xFF1E2B38);
  static const panelDeep = Color(0xFF142029);
  static const amber = Color(0xFFF5B041);
  static const amberDim = Color(0xFF3A3322);
  static const paper = Color(0xFFF2F4F6);
  static const ink = Color(0xFF1A1F24);
  static const muted = Color(0xFF66727F);
  static const line = Color(0xFFD9DEE3);
  static const correct = Color(0xFF2E9E62);
  static const wrong = Color(0xFFC8463D);
}

ThemeData buildTheme() {
  final scheme = ColorScheme.fromSeed(seedColor: AppColors.panel).copyWith(
    primary: AppColors.panel,
    onPrimary: Colors.white,
    secondary: AppColors.amber,
    surface: Colors.white,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: AppColors.paper,
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.panel,
      foregroundColor: Colors.white,
      elevation: 0,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: AppColors.panel,
        foregroundColor: Colors.white,
        minimumSize: const Size.fromHeight(52),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.panel,
        minimumSize: const Size.fromHeight(44),
        side: const BorderSide(color: AppColors.line),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    ),
  );
}
