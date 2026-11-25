package com.example.vgashop.service;

import com.example.vgashop.dto.AddToCartRequest;
import com.example.vgashop.dto.CartResponse;
import com.example.vgashop.dto.UpdateCartItemRequest;
import com.example.vgashop.entity.Cart;
import com.example.vgashop.entity.CartItem;
import com.example.vgashop.entity.Product;
import com.example.vgashop.entity.User;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.CartItemRepository;
import com.example.vgashop.repository.CartRepository;
import com.example.vgashop.repository.ProductRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CartServiceWhiteBoxTest {

    @Mock private CartRepository cartRepository;
    @Mock private CartItemRepository cartItemRepository;
    @Mock private ProductRepository productRepository;
    @Mock private UserService userService;

    private CartService cartService;
    private User user;
    private Product product;

    @BeforeEach
    void setUp() {
        cartService = new CartService(cartRepository, cartItemRepository, productRepository, userService);
        user = new User();
        user.setId(1L);
        user.setUsername("buyer");

        product = new Product();
        product.setId(100L);
        product.setName("RTX 4090");
        product.setPrice(new BigDecimal("50000000"));
        product.setStock(5);

        when(userService.getCurrentUser()).thenReturn(user);
    }

    @Test
    @DisplayName("WB-CART-01: getMyCart creates new cart when absent and returns existing when present")
    void testGetMyCartBranches() {
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.empty());
        when(cartRepository.save(any(Cart.class))).thenAnswer(inv -> {
            Cart c = inv.getArgument(0);
            c.setId(10L);
            return c;
        });

        CartResponse created = cartService.getMyCart();
        assertEquals(10L, created.getCartId());
        assertEquals(0, created.getTotalItems());
        assertEquals(BigDecimal.ZERO, created.getTotalAmount());

        Cart existing = new Cart();
        existing.setId(22L);
        existing.setUser(user);
        existing.setTotalAmount(BigDecimal.ZERO);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(existing));

        CartResponse loaded = cartService.getMyCart();
        assertEquals(22L, loaded.getCartId());
    }

    @Test
    @DisplayName("WB-CART-02: addToCart throws ResourceNotFoundException when product does not exist")
    void testAddToCartProductNotFound() {
        Cart cart = new Cart();
        cart.setId(1L);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));
        when(productRepository.findByIdAndDeleted(999L, false)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
                () -> cartService.addToCart(new AddToCartRequest(999L, 1)));
    }

    @Test
    @DisplayName("WB-CART-03: addToCart throws IllegalArgumentException when requested qty exceeds stock")
    void testAddToCartInsufficientStock() {
        Cart cart = new Cart();
        cart.setId(1L);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));
        when(productRepository.findByIdAndDeleted(100L, false)).thenReturn(Optional.of(product));

        assertThrows(IllegalArgumentException.class,
                () -> cartService.addToCart(new AddToCartRequest(100L, 6)));
    }

    @Test
    @DisplayName("WB-CART-04: addToCart adds new item and merges quantity when same product added again")
    void testAddToCartNewAndExistingItemBranches() {
        Cart cart = new Cart();
        cart.setId(1L);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));
        when(productRepository.findByIdAndDeleted(100L, false)).thenReturn(Optional.of(product));

        CartResponse first = cartService.addToCart(new AddToCartRequest(100L, 2));
        assertEquals(2, first.getTotalItems());
        assertEquals(new BigDecimal("100000000"), first.getTotalAmount());

        // Second call merges into existing item (2 + 2 = 4 <= 5)
        CartResponse merged = cartService.addToCart(new AddToCartRequest(100L, 2));
        assertEquals(4, merged.getTotalItems());
        assertEquals(new BigDecimal("200000000"), merged.getTotalAmount());

        // Third call overflows stock (4 + 2 = 6 > 5)
        assertThrows(IllegalArgumentException.class,
                () -> cartService.addToCart(new AddToCartRequest(100L, 2)));
    }

    @Test
    @DisplayName("WB-CART-05: updateCartItem covers missing cart, missing item, <=0 removal, >stock error, valid update")
    void testUpdateCartItemAllBranches() {
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class,
                () -> cartService.updateCartItem(5L, new UpdateCartItemRequest(2)));

        Cart cart = new Cart();
        cart.setId(1L);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));
        assertThrows(ResourceNotFoundException.class,
                () -> cartService.updateCartItem(5L, new UpdateCartItemRequest(2)));

        CartItem item = new CartItem();
        item.setId(5L);
        item.setCart(cart);
        item.setProduct(product);
        item.setQuantity(2);
        cart.getCartItems().add(item);

        // Exceeds stock branch
        assertThrows(IllegalArgumentException.class,
                () -> cartService.updateCartItem(5L, new UpdateCartItemRequest(10)));

        // Valid quantity update branch
        CartResponse updated = cartService.updateCartItem(5L, new UpdateCartItemRequest(3));
        assertEquals(3, updated.getTotalItems());

        // Quantity <= 0 removes item branch
        CartResponse removed = cartService.updateCartItem(5L, new UpdateCartItemRequest(0));
        assertEquals(0, removed.getTotalItems());
    }

    @Test
    @DisplayName("WB-CART-06: removeCartItem covers missing cart, missing item, and success removal")
    void testRemoveCartItemBranches() {
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> cartService.removeCartItem(7L));

        Cart cart = new Cart();
        cart.setId(1L);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));
        assertThrows(ResourceNotFoundException.class, () -> cartService.removeCartItem(7L));

        CartItem item = new CartItem();
        item.setId(7L);
        item.setProduct(product);
        item.setQuantity(1);
        cart.getCartItems().add(item);

        CartResponse resp = cartService.removeCartItem(7L);
        assertEquals(0, resp.getTotalItems());
        assertEquals(BigDecimal.ZERO, resp.getTotalAmount());
    }

    @Test
    @DisplayName("WB-CART-07: clearCart clears items and resets total, throws when cart missing")
    void testClearCartBranches() {
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> cartService.clearCart());

        Cart cart = new Cart();
        cart.setId(1L);
        CartItem item = new CartItem();
        item.setId(8L);
        item.setProduct(product);
        item.setQuantity(1);
        cart.getCartItems().add(item);
        cart.setTotalAmount(new BigDecimal("50000000"));
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));

        cartService.clearCart();
        assertTrue(cart.getCartItems().isEmpty());
        assertEquals(BigDecimal.ZERO, cart.getTotalAmount());
        assertTrue(item.isDeleted());
    }
}
