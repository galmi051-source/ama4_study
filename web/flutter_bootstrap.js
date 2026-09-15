{{flutter_js}}
{{flutter_build_config}}

// Flutter 標準の Service Worker は廃止済み（自前の sw.js を index.html で登録）。
// CanvasKit を CDN（gstatic）ではなく同梱のものから読むことで、オフラインでも起動できる。
_flutter.loader.load({
  config: { canvasKitBaseUrl: 'canvaskit/' },
  onEntrypointLoaded: async function (engineInitializer) {
    const appRunner = await engineInitializer.initializeEngine();
    const splash = document.getElementById('splash');
    if (splash) splash.remove();
    await appRunner.runApp();
  }
});
