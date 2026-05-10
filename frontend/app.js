const DEFAULT_API_BASE = "http://localhost:8000";
const TOKEN_KEY = "oauth_login_access_token";
const API_BASE_KEY = "oauth_login_api_base";

const loginView = document.querySelector("#login-view");
const profileView = document.querySelector("#profile-view");
const loginButton = document.querySelector("#login-button");
const logoutButton = document.querySelector("#logout-button");
const refreshButton = document.querySelector("#refresh-button");
const saveApiButton = document.querySelector("#save-api-button");
const apiBaseInput = document.querySelector("#api-base");
const statusBar = document.querySelector("#status-bar");
const statusText = document.querySelector("#status-text");
const username = document.querySelector("#username");
const email = document.querySelector("#email");
const avatar = document.querySelector("#avatar");
const tokenState = document.querySelector("#token-state");
const tokenStep = document.querySelector("#token-step");
const profileStep = document.querySelector("#profile-step");

function getApiBase() {
  return (localStorage.getItem(API_BASE_KEY) || DEFAULT_API_BASE).replace(/\/$/, "");
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function setStatus(state, text) {
  statusBar.classList.remove("is-online", "is-offline");
  if (state) {
    statusBar.classList.add(`is-${state}`);
  }
  statusText.textContent = text;
}

function parseTokenFromHash() {
  const hash = window.location.hash.replace(/^#/, "");
  if (!hash) {
    return;
  }

  const params = new URLSearchParams(hash);
  const token = params.get("access_token");
  if (token) {
    setToken(token);
    history.replaceState(null, "", window.location.pathname + window.location.search);
  }
}

function updateFlow(isSignedIn) {
  tokenStep.classList.toggle("is-complete", isSignedIn);
  profileStep.classList.toggle("is-complete", isSignedIn);
}

function showLoggedOut(message = "Ready for Google login") {
  loginView.classList.remove("is-hidden");
  profileView.classList.add("is-hidden");
  tokenState.textContent = "Not active";
  updateFlow(false);
  setStatus("online", message);
}

function showProfile(user) {
  const displayName = user.username || "User";
  username.textContent = displayName;
  email.textContent = user.email || "-";
  avatar.textContent = displayName.trim().charAt(0).toUpperCase() || "U";
  tokenState.textContent = "Active";
  loginView.classList.add("is-hidden");
  profileView.classList.remove("is-hidden");
  updateFlow(true);
  setStatus("online", "Signed in");
}

async function checkBackend() {
  try {
    const response = await fetch(`${getApiBase()}/health`);
    if (!response.ok) {
      throw new Error("Backend is not healthy");
    }
    setStatus("online", "Backend online");
  } catch (error) {
    setStatus("offline", "Backend offline");
  }
}

async function loadProfile() {
  const token = getToken();
  if (!token) {
    await checkBackend();
    showLoggedOut();
    return;
  }

  try {
    const response = await fetch(`${getApiBase()}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      clearToken();
      showLoggedOut("Session expired");
      return;
    }

    if (!response.ok) {
      throw new Error("Profile request failed");
    }

    const user = await response.json();
    showProfile(user);
  } catch (error) {
    setStatus("offline", "Could not reach backend");
  }
}

function startGoogleLogin() {
  window.location.href = `${getApiBase()}/auth/login/google`;
}

function saveApiBase() {
  const value = apiBaseInput.value.trim().replace(/\/$/, "");
  if (!value) {
    return;
  }

  localStorage.setItem(API_BASE_KEY, value);
  checkBackend();
}

parseTokenFromHash();
apiBaseInput.value = getApiBase();

loginButton.addEventListener("click", startGoogleLogin);
logoutButton.addEventListener("click", () => {
  clearToken();
  showLoggedOut("Logged out");
});
refreshButton.addEventListener("click", loadProfile);
saveApiButton.addEventListener("click", saveApiBase);
apiBaseInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    saveApiBase();
  }
});

loadProfile();
