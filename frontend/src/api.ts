export async function api<T>(
  path: string,
  data?: object | FormData,
): Promise<T> {
  const form = data instanceof FormData;
  const res = await fetch("/api/" + path, {
    method: data ? "POST" : "GET",
    headers: data
      ? {
          "X-Meridian-Action": "analyst",
          ...(!form ? { "Content-Type": "application/json" } : {}),
        }
      : {},
    body: data ? (form ? data : JSON.stringify(data)) : undefined,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `Request failed (${res.status}). Check your entries and try again.`,
    );
  }
  return res.json();
}
