/**
 * AutoTrade Pro v4.0 - Service Worker
 * 웹 브라우저 PUSH 알림 처리
 */

const CACHE_NAME = 'autotrade-pro-v4';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js'
];

// 설치
self.addEventListener('install', event => {
    console.log('[SW] Installing Service Worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching app shell');
                return cache.addAll(urlsToCache);
            })
    );
});

// 활성화
self.addEventListener('activate', event => {
    console.log('[SW] Activating Service Worker...');
    event.waitUntil(
        caches.keys().then(keyList => {
            return Promise.all(keyList.map(key => {
                if (key !== CACHE_NAME) {
                    console.log('[SW] Removing old cache:', key);
                    return caches.delete(key);
                }
            }));
        })
    );
    return self.clients.claim();
});

// 푸시 알림 수신
self.addEventListener('push', event => {
    console.log('[SW] Push received:', event);

    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data = { title: 'AutoTrade Pro', body: event.data.text() };
        }
    }

    const title = data.title || 'AutoTrade Pro';
    const options = {
        body: data.body || '새로운 알림이 있습니다.',
        icon: '/static/img/icon.png',
        badge: '/static/img/badge.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: data.primaryKey || 1
        },
        actions: [
            {
                action: 'explore',
                title: '확인',
                icon: '/static/img/checkmark.png'
            },
            {
                action: 'close',
                title: '닫기',
                icon: '/static/img/close.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// 알림 클릭
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification click:', event);

    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Fetch 이벤트 (캐싱)
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});
