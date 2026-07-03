const TOKEN_KEY = "creatoros.access_token";
const USER_ID_KEY = "creatoros.user_id";
const EMAIL_KEY = "creatoros.email";

export type AuthSession = {
  accessToken?: string;
  userId: string;
  email: string;
};

export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  const userId = sessionStorage.getItem(USER_ID_KEY) ?? localStorage.getItem(USER_ID_KEY);
  const email = sessionStorage.getItem(EMAIL_KEY) ?? localStorage.getItem(EMAIL_KEY) ?? "";
  const accessToken = localStorage.getItem(TOKEN_KEY) ?? undefined;
  if (!userId) return null;
  return { accessToken, userId, email };
}

export function setSession(session: AuthSession): void {
  sessionStorage.setItem(USER_ID_KEY, session.userId);
  sessionStorage.setItem(EMAIL_KEY, session.email);
  localStorage.setItem(USER_ID_KEY, session.userId);
  localStorage.setItem(EMAIL_KEY, session.email);
  if (session.accessToken) {
    localStorage.setItem(TOKEN_KEY, session.accessToken);
  }
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(EMAIL_KEY);
  sessionStorage.removeItem(USER_ID_KEY);
  sessionStorage.removeItem(EMAIL_KEY);
}

export function getAuthHeaders(): Record<string, string> {
  const session = getSession();
  if (!session) return {};
  return { Authorization: `Bearer ${session.accessToken}` };
}

export function getUserId(): string {
  return getSession()?.userId ?? process.env.NEXT_PUBLIC_CREATOR_USER_ID ?? "demo-user";
}
