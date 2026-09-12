/* 4アマ ながら学習 – Service Worker（オフライン対応）
 *
 * キャッシュは 2 種類：
 *   ama4-app-<VERSION> … アプリ本体（index.html / main.dart.js / CanvasKit / 問題 JSON など）
 *                        インストール時にまとめて取得し、以後はキャッシュ優先。
 *                        新しい版が公開されると VERSION が変わり、古いものは消す。
 *   ama4-media         … VOICEVOX 音声（約450ファイル・35MB）。
 *                        初回に全部は取らず、再生したものから順に貯める（キャッシュ優先）。
 *                        アプリの版が上がっても消さない。設定の「まとめてダウンロード」で
 *                        全部取り込める。
 *
 * VERSION と QUESTION_FILES はビルド後に tools/stamp_sw.py が埋める（GitHub Actions / tools/build_web.ps1）。
 */
const VERSION = '__BUILD_VERSION__';
const APP_CACHE = 'ama4-app-' + VERSION;
const MEDIA_CACHE = 'ama4-media';

// 問題 JSON の一覧。ビルド時に assets/questions/ の中身で置き換える（tools/stamp_sw.py）
const QUESTION_FILES = (function () {
  try { return JSON.parse('__QUESTION_FILES__'); } catch (e) { return []; } // 未埋め込み（flutter run）なら空
})();

// 起動に必要なもの（初回アクセス時にまとめて取得）
const APP_SHELL = [
  ...QUESTION_FILES.map((f) => 'assets/assets/questions/' + f),
  'assets/packages/wakelock_plus/assets/no_sleep.js',
  'assets/shaders/ink_sparkle.frag',
  'assets/shaders/stretch_effect.frag',
  './',
  'index.html',
  'flutter_bootstrap.js',
  'flutter.js',
  'main.dart.js',
  'manifest.json',
  'favicon.png',
  'icons/Icon-192.png',
  'icons/Icon-512.png',
  'assets/AssetManifest.bin.json',
  'assets/AssetManifest.bin',
  'assets/FontManifest.json',
  'assets/fonts/MaterialIcons-Regular.otf',
  'canvaskit/canvaskit.js',
  'canvaskit/canvaskit.wasm',
  'canvaskit/chromium/canvaskit.js',
  'canvaskit/chromium/canvaskit.wasm',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(APP_CACHE).then(async (cache) => {
      // 1 つ失敗しても全体を失敗させない（存在しないファイル対策）
      await Promise.all(APP_SHELL.map((u) =>
        cache.add(new Request(u, { cache: 'reload' })).catch((e) => console.warn('precache skip', u, e))));
      await self.skipWaiting();
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((k) => k.startsWith('ama4-app-') && k !== APP_CACHE)
      .map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

const isVoice = (url) => url.pathname.includes('/assets/assets/voice/');

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (isVoice(url)) {
    event.respondWith(cacheFirst(MEDIA_CACHE, req));
    return;
  }
  if (req.mode === 'navigate') {
    // アプリの入口。キャッシュ優先で即起動、無ければネット
    event.respondWith(cacheFirst(APP_CACHE, new Request('index.html')).catch(() => fetch(req)));
    return;
  }
  event.respondWith(staleWhileRevalidate(APP_CACHE, req));
});

async function cacheFirst(cacheName, req) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req, { ignoreSearch: true });
  if (hit) return hit;
  const res = await fetch(req);
  if (res && res.ok) cache.put(req, res.clone());
  return res;
}

// キャッシュがあれば即返し、裏でネットから更新しておく。無ければネット、それも駄目なら他のキャッシュも探す
async function staleWhileRevalidate(cacheName, req) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req, { ignoreSearch: true });
  const network = fetch(req).then((res) => {
    if (res && res.ok) cache.put(req, res.clone());
    return res;
  }).catch(() => undefined);
  if (hit) return hit;
  const res = await network;
  if (res) return res;
  const any = await caches.match(req, { ignoreSearch: true });
  if (any) return any;
  return new Response('offline', { status: 503, statusText: 'offline' });
}
