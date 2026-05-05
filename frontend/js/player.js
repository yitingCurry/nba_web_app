async function fetchPlayer(name) {
  const resp = await fetch(`${API_BASE}/api/player/${encodeURIComponent(name)}`);
  if (!resp.ok) {
    const msg = await resp.text();
    throw new Error(msg || "查詢失敗");
  }
  return resp.json();
}
