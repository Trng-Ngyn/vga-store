import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';

const createLocalStorageMock = () => {
  let store = {};
  return {
    getItem: (key) => (key in store ? store[key] : null),
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; },
  };
};

vi.stubGlobal('localStorage', createLocalStorageMock());

import { formatCurrency, formatDate, truncate, getInitials } from '../helpers.js';
import { getSeenOrderIds, markOrdersAsSeen, isOrderNew, countNewOrders } from '../orderNewUtils.js';

let adminAuthReducer, adminAuthActions;

beforeAll(async () => {
  const mod = await import('../../redux/authSlice.js');
  adminAuthReducer = mod.default;
  adminAuthActions = mod;
});

beforeEach(() => {
  localStorage.clear();
});

describe('FE-ADMIN-UTILS: helpers.js EP & BVA tests', () => {
  it('formats currency, empty fallback, dates, truncate boundaries, initials', () => {
    expect(formatCurrency(0)).toBe('--');
    expect(formatCurrency(null)).toBe('--');
    expect(formatCurrency(15000000)).toContain('đ');

    expect(formatDate(null)).toBe('--');
    expect(formatDate('2026-11-25T10:00:00')).toMatch(/25/);

    expect(truncate(null)).toBe('--');
    expect(truncate('short', 10)).toBe('short');
    expect(truncate('exacttench', 10)).toBe('exacttench');
    expect(truncate('elevenchars', 10)).toBe('elevenchar...');

    expect(getInitials('')).toBe('?');
    expect(getInitials('trong')).toBe('T');
  });

  it('tracks seen/new order IDs via orderNewUtils', () => {
    expect(isOrderNew(101)).toBe(true);
    markOrdersAsSeen([101, 102]);
    expect(isOrderNew(101)).toBe(false);
    expect(isOrderNew(103)).toBe(true);
    expect(getSeenOrderIds().size).toBe(2);

    const orders = [{ id: 101 }, { orderId: 103 }, { id: 104 }];
    expect(countNewOrders(orders)).toBe(2);
  });
});

describe('FE-ADMIN-AUTH: admin authSlice reducer', () => {
  it('handles admin loginStart, loginSuccess, loginFailure, logout', () => {
    let state = adminAuthReducer(undefined, adminAuthActions.loginStart());
    expect(state.loading).toBe(true);

    state = adminAuthReducer(state, adminAuthActions.loginSuccess({
      user: { username: 'admin', role: 'ADMIN' },
      token: 'adm-tok',
    }));
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem('adminToken')).toBe('adm-tok');

    state = adminAuthReducer(state, adminAuthActions.logout());
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem('adminToken')).toBeNull();

    state = adminAuthReducer(state, adminAuthActions.loginFailure('Denied'));
    expect(state.error).toBe('Denied');
  });
});
