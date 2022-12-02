'use strict';

const CACHE_NAME = "offlineCache-v1";
const OFFLINE_URL = "/assets/offline.html";

self.addEventListener("install", () => {
	const cacheOfflinePage = async () => {
		const cache = await caches.open(CACHE_NAME);
		await cache.add(new Request(OFFLINE_URL, {cache: "reload"}));
	};

	cacheOfflinePage().then(() => {
		this.skipWaiting();
	});
});

self.addEventListener("activate", (event) => {
	const expectedCaches = [CACHE_NAME];

	event.waitUntil(
		caches.keys().then(keys => Promise.all(
			keys.map(key => {
				if (!expectedCaches.includes(key)) {
					return caches.delete(key);
				}
			})
		))
	);
});

self.addEventListener("fetch", (event) => {
	if (event.request.mode === "navigate") {
		event.respondWith((async () => {
			try {
				const preloadResponse = await event.preloadResponse;
				if (preloadResponse) return preloadResponse;

				const networkResponse = await fetch(event.request);
				return networkResponse;
			} catch (error) {
				const cachedResponse = await caches.match(OFFLINE_URL);
				return cachedResponse;
			}
		})());
	}
});

self.addEventListener('push', function(event) {
	const pushData = event.data.text();
	let data, title, body, url, icon;
	try {
		data = JSON.parse(pushData);
		title = data.title;
		body = data.body;
		url = data.url;
		icon = data.icon;
	} catch(e) {
		title = "Untitled";
		body = pushData;
	}
	const options = {
		body: body,
		data: {url: url},
		icon: icon
	};

	event.waitUntil(
		self.registration.showNotification(title, options)
	);
});

self.addEventListener('notificationclick', (e) => {
	if (e.notification.data.url)
		e.waitUntil(clients.openWindow(e.notification.data.url));
	e.notification.close();
});
