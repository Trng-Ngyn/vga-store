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
vi.mock('../../utils/alertUtils', () => ({ toastError: vi.fn(), toastSuccess: vi.fn() }));
vi.mock('../../services/cartService', () => ({ default: {} }));

let authReducer, authActions;
let cartReducer, cartActions;
let compareReducer, compareActions;
let wishlistReducer, wishlistActions;

beforeAll(async () => {
  const authMod = await import('../authSlice.js');
  authReducer = authMod.default;
  authActions = authMod;

  const cartMod = await import('../cartSlice.js');
  cartReducer = cartMod.default;
  cartActions = cartMod;

  const compareMod = await import('../compareSlice.js');
  compareReducer = compareMod.default;
  compareActions = compareMod;

  const wishMod = await import('../wishlistSlice.js');
  wishlistReducer = wishMod.default;
  wishlistActions = wishMod;
});

beforeEach(() => {
  localStorage.clear();
});

describe('FE-USER-AUTH: authSlice reducer White-Box & State tests', () => {
  it('handles loginStart, loginSuccess, updateUser, loginFailure, logout', () => {
    let state = authReducer(undefined, authActions.loginStart());
    expect(state.loading).toBe(true);
    expect(state.error).toBeNull();

    state = authReducer(state, authActions.loginSuccess({
      user: { username: 'trong', role: 'USER' },
      token: 'jwt-123',
    }));
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toBe('jwt-123');
    expect(localStorage.getItem('token')).toBe('jwt-123');

    state = authReducer(state, authActions.updateUser({ phone: '0908123456' }));
    expect(state.user.phone).toBe('0908123456');

    state = authReducer(state, authActions.logout());
    expect(state.isAuthenticated).toBe(false);
    expect(state.token).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();

    state = authReducer(state, authActions.loginFailure('Sai mat khau'));
    expect(state.error).toBe('Sai mat khau');
    expect(state.isAuthenticated).toBe(false);
  });

  it('handles registration and auth modal flags', () => {
    let state = authReducer(undefined, authActions.registerStart());
    expect(state.loading).toBe(true);
    state = authReducer(state, authActions.registerFailure('Email invalid'));
    expect(state.error).toBe('Email invalid');
    state = authReducer(state, authActions.registerSuccess());
    expect(state.loading).toBe(false);
    state = authReducer(state, authActions.openAuthModal());
    expect(state.isAuthModalOpen).toBe(true);
    state = authReducer(state, authActions.closeAuthModal());
    expect(state.isAuthModalOpen).toBe(false);
  });
});

describe('FE-USER-CART: cartSlice quantity & totals calculation', () => {
  it('adds, increments, decrements, removes and clears cart items', () => {
    const gpu1 = { id: 1, name: 'RTX 4070', price: 15000000 };
    const gpu2 = { id: 2, name: 'RTX 4090', price: 45000000 };

    let state = cartReducer(undefined, cartActions.addToCart(gpu1));
    state = cartReducer(state, cartActions.addToCart(gpu1));
    state = cartReducer(state, cartActions.addToCart(gpu2));
    expect(state.cartTotalQuantity).toBe(3);
    expect(state.cartTotalAmount).toBe(75000000);

    state = cartReducer(state, cartActions.decreaseCart(gpu1));
    expect(state.cartTotalQuantity).toBe(2);
    state = cartReducer(state, cartActions.decreaseCart(gpu1));
    expect(state.cartItems.length).toBe(1);

    state = cartReducer(state, cartActions.removeFromCart(gpu2));
    expect(state.cartTotalAmount).toBe(0);

    state = cartReducer(state, cartActions.addToCart(gpu1));
    state = cartReducer(state, cartActions.clearCart());
    expect(state.cartItems).toEqual([]);
  });
});

describe('FE-USER-COMPARE & WISHLIST: compareSlice BVA max=3 & wishlistSlice', () => {
  it('enforces max 3 products in compare list (FIFO replacement) and toggles', () => {
    let state = compareReducer(undefined, compareActions.toggleCompare({ id: 1 }));
    state = compareReducer(state, compareActions.toggleCompare({ id: 2 }));
    state = compareReducer(state, compareActions.toggleCompare({ id: 3 }));
    expect(state.compareItems.map(i => i.id)).toEqual([1, 2, 3]);

    // 4th product replaces oldest (1)
    state = compareReducer(state, compareActions.toggleCompare({ id: 4 }));
    expect(state.compareItems.map(i => i.id)).toEqual([2, 3, 4]);

    // Toggle existing item removes it
    state = compareReducer(state, compareActions.toggleCompare({ id: 3 }));
    expect(state.compareItems.map(i => i.id)).toEqual([2, 4]);

    state = compareReducer(state, compareActions.setCompareModalOpen(true));
    expect(state.isCompareModalOpen).toBe(true);
    state = compareReducer(state, compareActions.clearCompare());
    expect(state.compareItems).toEqual([]);
  });

  it('toggles, removes and clears wishlist items', () => {
    let state = wishlistReducer(undefined, wishlistActions.toggleWishlist({ id: 10, name: 'RTX' }));
    expect(state.wishlistItems.length).toBe(1);
    state = wishlistReducer(state, wishlistActions.toggleWishlist({ id: 10 }));
    expect(state.wishlistItems.length).toBe(0);
    state = wishlistReducer(state, wishlistActions.toggleWishlist({ id: 11 }));
    state = wishlistReducer(state, wishlistActions.clearWishlist());
    expect(state.wishlistItems).toEqual([]);
  });
});
