export async function getCSRFToken() {
  // Call any authenticated endpoint
  const res = await fetch("/api/method/frappe.auth.get_logged_user", {
    credentials: "include", // 🔥 VERY IMPORTANT
  });

  if (!res.ok) {
    return null;
  }

  // CSRF token is stored in cookie by Frappe
  const match = document.cookie.match(/csrf_token=([^;]+)/);

  return match ? decodeURIComponent(match[1]) : null;
}
