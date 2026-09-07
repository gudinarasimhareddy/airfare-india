/**
 * AirfareX India — Central Supabase Authentication & Session Client
 *
 * Capabilities:
 * - Email / Password Sign Up
 * - Email / Password Login
 * - Password Reset (Supabase recovery email)
 * - Session persistence in localStorage & restoration after page refresh
 * - Listens to auth state changes & notifies subscribers
 * - Zero password storage: Passwords are handled strictly by Supabase Auth
 * - Public anon key only: Never exposes backend administrative keys
 * - Dual engine: Uses @supabase/supabase-js if loaded, with full REST fallback
 */

class AirfarexAuth {
  constructor() {
    this.user = null;
    this.session = null;
    this.token = null;
    this.config = null;
    this.supabaseClient = null;
    this.listeners = [];
    this.initialized = false;
    this.STORAGE_KEY = 'airfarex_auth_session';
  }

  async init() {
    if (this.initialized) return;

    try {
      // 1. Fetch public Supabase configuration from backend
      const res = await fetch('/api/v1/auth/config');
      if (res.ok) {
        this.config = await res.json();
      }
    } catch (e) {
      console.warn('[Auth] Could not load backend auth config:', e.message);
    }

    // Default fallback Supabase project URL
    const supabaseUrl = this.config?.supabase_url || 'https://thtwkhhccxmkkgwtoleb.supabase.co';
    const supabaseAnonKey = this.config?.supabase_anon_key || '';

    // 2. Initialize official Supabase JS client if available on window
    if (window.supabase && typeof window.supabase.createClient === 'function' && supabaseAnonKey) {
      try {
        this.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseAnonKey, {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
            storageKey: this.STORAGE_KEY
          }
        });

        // Listen to native Supabase auth changes
        this.supabaseClient.auth.onAuthStateChange(async (event, session) => {
          this._handleSessionChange(session);
        });
      } catch (err) {
        console.warn('[Auth] Supabase SDK init error, using REST mode:', err);
      }
    }

    // 3. Restore session from localStorage or Supabase
    await this.restoreSession();
    this.initialized = true;
    this._updateUI();
  }

  async restoreSession() {
    // A. Check Supabase client session
    if (this.supabaseClient) {
      try {
        const { data, error } = await this.supabaseClient.auth.getSession();
        if (data?.session && !error) {
          this._handleSessionChange(data.session);
          return;
        }
      } catch (e) {
        console.warn('[Auth] SDK session restore note:', e.message);
      }
    }

    // B. Check local persisted session (REST fallback)
    try {
      const raw = localStorage.getItem(this.STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.access_token && parsed.user) {
          // Check expiration
          const now = Math.floor(Date.now() / 1000);
          if (parsed.expires_at && parsed.expires_at < now) {
            this.signOut();
            return;
          }
          this.session = parsed;
          this.token = parsed.access_token;
          this.user = parsed.user;
          this._notifyListeners();
        }
      }
    } catch (e) {
      console.warn('[Auth] REST session restore note:', e.message);
    }
  }

  _handleSessionChange(session) {
    if (session) {
      this.session = session;
      this.token = session.access_token;
      this.user = session.user;
      try {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
          access_token: session.access_token,
          refresh_token: session.refresh_token,
          expires_at: session.expires_at,
          user: session.user
        }));
      } catch (e) {}
      // Sync profile to backend
      this._syncSessionToBackend();
    } else {
      this.session = null;
      this.token = null;
      this.user = null;
      try {
        localStorage.removeItem(this.STORAGE_KEY);
      } catch (e) {}
    }
    this._notifyListeners();
    this._updateUI();
  }

  async _syncSessionToBackend() {
    if (!this.token) return;
    try {
      await fetch('/api/v1/auth/sync-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        }
      });
    } catch (e) {}
  }

  /**
   * User Sign Up
   */
  async signUp(fullName, email, password, confirmPassword, phone = '') {
    if (!email || !password) {
      throw new Error('Please enter both email and password.');
    }
    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters long.');
    }
    if (password !== confirmPassword) {
      throw new Error('Passwords do not match. Please re-enter.');
    }

    // A. Use Supabase SDK if available
    if (this.supabaseClient) {
      const { data, error } = await this.supabaseClient.auth.signUp({
        email: email.trim(),
        password,
        options: {
          data: {
            full_name: fullName.trim(),
            name: fullName.trim(),
            phone: phone.trim()
          }
        }
      });
      if (error) throw error;

      if (data?.session) {
        this._handleSessionChange(data.session);
        return { success: true, user: data.user, session: data.session };
      }
      return {
        success: true,
        user: data.user,
        message: 'Account created! Please check your email to verify your address or sign in.'
      };
    }

    // B. Direct REST API Call
    const url = `${this._getSupabaseUrl()}/auth/v1/signup`;
    const res = await fetch(url, {
      method: 'POST',
      headers: this._getAuthHeaders(),
      body: JSON.stringify({
        email: email.trim(),
        password,
        data: {
          full_name: fullName.trim(),
          name: fullName.trim(),
          phone: phone.trim()
        }
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error_description || data.msg || data.message || 'Sign up failed.');
    }

    if (data.access_token) {
      const session = {
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_at: Math.floor(Date.now() / 1000) + (data.expires_in || 3600),
        user: data.user || data
      };
      this._handleSessionChange(session);
    }
    return { success: true, user: data.user || data };
  }

  /**
   * User Sign In
   */
  async signIn(email, password) {
    if (!email || !password) {
      throw new Error('Please enter your email and password.');
    }

    // A. Use Supabase SDK if available
    if (this.supabaseClient) {
      const { data, error } = await this.supabaseClient.auth.signInWithPassword({
        email: email.trim(),
        password
      });
      if (error) throw error;
      this._handleSessionChange(data.session);
      return { success: true, user: data.user, session: data.session };
    }

    // B. Direct REST API Call
    const url = `${this._getSupabaseUrl()}/auth/v1/token?grant_type=password`;
    const res = await fetch(url, {
      method: 'POST',
      headers: this._getAuthHeaders(),
      body: JSON.stringify({
        email: email.trim(),
        password
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error_description || data.msg || data.message || 'Invalid email or password.');
    }

    const session = {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      expires_at: Math.floor(Date.now() / 1000) + (data.expires_in || 3600),
      user: data.user
    };
    this._handleSessionChange(session);
    return { success: true, user: data.user, session };
  }

  /**
   * User Sign Out
   */
  async signOut() {
    if (this.supabaseClient) {
      try {
        await this.supabaseClient.auth.signOut();
      } catch (e) {}
    } else if (this.token) {
      try {
        await fetch(`${this._getSupabaseUrl()}/auth/v1/logout`, {
          method: 'POST',
          headers: {
            ...this._getAuthHeaders(),
            'Authorization': `Bearer ${this.token}`
          }
        });
      } catch (e) {}
    }

    this._handleSessionChange(null);
  }

  /**
   * Password Reset Flow
   */
  async resetPassword(email) {
    if (!email) throw new Error('Please enter your registered email address.');

    if (this.supabaseClient) {
      const { error } = await this.supabaseClient.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: window.location.origin
      });
      if (error) throw error;
      return { success: true, message: 'Password reset link sent to your email.' };
    }

    const url = `${this._getSupabaseUrl()}/auth/v1/recover`;
    const res = await fetch(url, {
      method: 'POST',
      headers: this._getAuthHeaders(),
      body: JSON.stringify({ email: email.trim() })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error_description || data.msg || data.message || 'Could not send reset email.');
    }
    return { success: true, message: 'Password reset instructions sent to your email.' };
  }

  isAuthenticated() {
    return Boolean(this.user && this.token);
  }

  getUser() {
    return this.user;
  }

  getUserDisplayName() {
    if (!this.user) return 'Guest';
    const meta = this.user.user_metadata || {};
    return meta.full_name || meta.name || this.user.email?.split('@')[0] || 'Traveler';
  }

  getToken() {
    return this.token;
  }

  onAuthStateChange(callback) {
    if (typeof callback === 'function') {
      this.listeners.push(callback);
      // Immediately invoke with current state
      callback(this.user, this.session);
    }
  }

  _notifyListeners() {
    this.listeners.forEach(cb => {
      try {
        cb(this.user, this.session);
      } catch (e) {
        console.error('[Auth] Listener callback error:', e);
      }
    });
  }

  _getSupabaseUrl() {
    return this.config?.supabase_url || 'https://thtwkhhccxmkkgwtoleb.supabase.co';
  }

  _getAuthHeaders() {
    const key = this.config?.supabase_anon_key || '';
    return {
      'apikey': key,
      'Content-Type': 'application/json'
    };
  }

  _updateUI() {
    // 1. Update Desktop Header Auth Widget
    const widget = document.getElementById('userNavWidget');
    if (widget) {
      if (this.isAuthenticated()) {
        const displayName = this.getUserDisplayName();
        const initial = displayName.charAt(0).toUpperCase();
        widget.innerHTML = `
          <div class="user-profile-menu-wrapper" style="position:relative; display:inline-block;">
            <button class="btn sm light user-avatar-btn" onclick="toggleUserDropdown(event)" style="display:inline-flex; align-items:center; gap:8px; font-weight:700;">
              <span class="user-avatar-circle" style="width:24px; height:24px; border-radius:50%; background:var(--brand-cyan, #0284c7); color:#fff; display:inline-flex; align-items:center; justify-content:center; font-size:12px;">${initial}</span>
              <span>${displayName}</span>
              <span style="font-size:10px; color:var(--text-muted);">▼</span>
            </button>
            <div class="user-dropdown-menu" id="userDropdownMenu" style="display:none; position:absolute; right:0; top:calc(100% + 6px); background:var(--bg-surface, #ffffff); border:1px solid var(--border-color, #e2e8f0); border-radius:var(--radius-md, 8px); box-shadow:var(--shadow-lg); min-width:210px; z-index:1100; padding:6px 0;">
              <div style="padding:10px 14px; border-bottom:1px solid var(--border-color); font-size:12px;">
                <div style="font-weight:700; color:var(--text-main);">${displayName}</div>
                <div style="color:var(--text-muted); font-size:11px; text-overflow:ellipsis; overflow:hidden;">${this.user.email}</div>
              </div>
              <a class="dropdown-item" onclick="showTab('trips'); closeUserDropdown();" style="display:flex; align-items:center; gap:8px; padding:9px 14px; font-size:13px; color:var(--text-main); cursor:pointer; text-decoration:none;">
                <span>🧳</span> <span>My Bookings</span>
              </a>
              <a class="dropdown-item" onclick="showTab('saved'); closeUserDropdown();" style="display:flex; align-items:center; gap:8px; padding:9px 14px; font-size:13px; color:var(--text-main); cursor:pointer; text-decoration:none;">
                <span>🔔</span> <span>Saved Flights & Alerts</span>
              </a>
              <div style="border-top:1px solid var(--border-color); margin:4px 0;"></div>
              <a class="dropdown-item" onclick="window.auth.signOut(); closeUserDropdown();" style="display:flex; align-items:center; gap:8px; padding:9px 14px; font-size:13px; color:var(--brand-rose, #e11d48); cursor:pointer; text-decoration:none;">
                <span>🚪</span> <span>Sign Out</span>
              </a>
            </div>
          </div>
        `;
      } else {
        widget.innerHTML = `
          <button class="btn sm primary" onclick="openAuthModal('login')" title="Customer Account Login / Sign Up" style="display:inline-flex; align-items:center; gap:6px;">
            <span>👤</span> <span>Sign In</span>
          </button>
        `;
      }
    }

    // 2. Update Mobile Drawer Auth Section
    const mobileAuth = document.getElementById('mobileDrawerAuth');
    if (mobileAuth) {
      if (this.isAuthenticated()) {
        const displayName = this.getUserDisplayName();
        mobileAuth.innerHTML = `
          <div style="padding:12px; background:var(--bg-muted); border-radius:var(--radius-md); margin-bottom:12px;">
            <div style="font-weight:700; font-size:14px; color:var(--text-main);">👤 ${displayName}</div>
            <div style="font-size:11.5px; color:var(--text-muted); margin-bottom:10px;">${this.user.email}</div>
            <div style="display:flex; gap:8px;">
              <button class="btn sm" style="flex:1;" onclick="showTab('trips'); toggleMobileMenu();">My Trips</button>
              <button class="btn sm light" onclick="window.auth.signOut(); toggleMobileMenu();">Logout</button>
            </div>
          </div>
        `;
      } else {
        mobileAuth.innerHTML = `
          <div style="margin-bottom:12px;">
            <button class="btn primary" style="width:100%;" onclick="openAuthModal('login'); toggleMobileMenu();">
              <span>👤 Sign In / Register</span>
            </button>
          </div>
        `;
      }
    }
  }
}

window.auth = new AirfarexAuth();

// Initialize auth on DOM load
document.addEventListener('DOMContentLoaded', () => {
  window.auth.init();
});

// Dropdown Helper Functions
function toggleUserDropdown(e) {
  if (e) e.stopPropagation();
  const menu = document.getElementById('userDropdownMenu');
  if (menu) {
    menu.style.display = menu.style.display === 'none' || !menu.style.display ? 'block' : 'none';
  }
}

function closeUserDropdown() {
  const menu = document.getElementById('userDropdownMenu');
  if (menu) menu.style.display = 'none';
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.user-profile-menu-wrapper')) {
    closeUserDropdown();
  }
});

window.toggleUserDropdown = toggleUserDropdown;
window.closeUserDropdown = closeUserDropdown;
