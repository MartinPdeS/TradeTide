// Drafts and named strategies are small; full results live in IndexedDB.
const prefix = 'tradetide.v2.';
let database;
export function readLocal(key, fallback) {
  try { return JSON.parse(localStorage.getItem(prefix + key)) ?? fallback; }
  catch { return fallback; }
}
export function writeLocal(key, value) {
  localStorage.setItem(prefix + key, JSON.stringify(value));
}
function openDatabase() {
  if (!database) database = new Promise((resolve, reject) => {
    const request = indexedDB.open('tradetide-research', 1);
    request.onupgradeneeded = () => request.result.createObjectStore('runs', {keyPath: 'id'});
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
  return database;
}
export async function readRuns() {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction('runs').objectStore('runs').getAll();
    request.onsuccess = () => resolve(request.result.sort((a, b) => b.createdAt - a.createdAt));
    request.onerror = () => reject(request.error);
  });
}
export async function storeRun(run, expiredIds = []) {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('runs', 'readwrite'), store = transaction.objectStore('runs');
    store.put(run);
    expiredIds.forEach(id => store.delete(id));
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
    transaction.onabort = () => reject(transaction.error || Error('Saving this run was interrupted.'));
  });
}
