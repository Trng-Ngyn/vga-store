package com.example.vgashop.service;

import com.example.vgashop.dto.*;
import com.example.vgashop.entity.*;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceWhiteBoxTest {

    @Mock private OrderRepository orderRepository;
    @Mock private OrderItemRepository orderItemRepository;
    @Mock private CartRepository cartRepository;
    @Mock private ProductRepository productRepository;
    @Mock private UserRepository userRepository;
    @Mock private UserService userService;
    @Mock private PaymentRepository paymentRepository;

    private OrderService orderService;
    private User user;
    private Product product;

    @BeforeEach
    void setUp() {
        orderService = new OrderService(orderRepository, orderItemRepository, cartRepository,
                productRepository, userRepository, userService, paymentRepository);

        user = new User();
        user.setId(1L);
        user.setUsername("buyer01");
        user.setEmail("buyer01@vga.vn");
        user.setFullName("Nguyễn Văn Mua");

        product = new Product();
        product.setId(50L);
        product.setName("RTX 4070 Ti");
        product.setPrice(new BigDecimal("22000000"));
        product.setStock(10);
    }

    @Test
    @DisplayName("WB-ORD-01: placeOrder throws for missing user, missing product, or insufficient stock")
    void testPlaceOrderErrorBranches() {
        OrderRequest req = new OrderRequest();
        OrderRequest.OrderItemRequest itemReq = new OrderRequest.OrderItemRequest();
        itemReq.setProductId(50L);
        itemReq.setQuantity(2);
        req.setItems(List.of(itemReq));

        when(userRepository.findByUsername("unknown")).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> orderService.placeOrder(req, "unknown"));

        when(userRepository.findByUsername("buyer01")).thenReturn(Optional.of(user));
        when(productRepository.findById(50L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> orderService.placeOrder(req, "buyer01"));

        product.setStock(1);
        when(productRepository.findById(50L)).thenReturn(Optional.of(product));
        assertThrows(IllegalArgumentException.class, () -> orderService.placeOrder(req, "buyer01"));
    }

    @Test
    @DisplayName("WB-ORD-02: placeOrder deducts stock and calculates total successfully")
    void testPlaceOrderSuccess() {
        OrderRequest req = new OrderRequest();
        req.setFullName("Tran Dinh Trong");
        req.setPhone("0908123456");
        req.setAddress("So 1 Vo Van Ngan, Thu Duc");
        req.setNote("Giao gio hanh chinh");

        OrderRequest.OrderItemRequest itemReq = new OrderRequest.OrderItemRequest();
        itemReq.setProductId(50L);
        itemReq.setQuantity(2);
        req.setItems(List.of(itemReq));

        when(userRepository.findByUsername("buyer01")).thenReturn(Optional.of(user));
        when(productRepository.findById(50L)).thenReturn(Optional.of(product));
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> {
            Order o = inv.getArgument(0);
            o.setId(88L);
            return o;
        });

        Map<String, Object> resp = orderService.placeOrder(req, "buyer01");

        assertEquals(88L, resp.get("orderId"));
        assertEquals("PENDING", resp.get("status"));
        assertEquals(8, product.getStock());
    }

    @Test
    @DisplayName("WB-ORD-03: createOrderFromCart handles missing cart, empty cart, insufficient stock, and success")
    void testCreateOrderFromCartAllBranches() {
        when(userService.getCurrentUser()).thenReturn(user);
        CreateOrderRequest req = new CreateOrderRequest();
        req.setPhone("0901234567");
        req.setShippingAddress("123 Nguyen Trai, Q1");

        // Missing cart branch
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> orderService.createOrderFromCart(req));

        // Empty cart branch
        Cart cart = new Cart();
        cart.setId(5L);
        when(cartRepository.findByUser_IdAndDeletedFalse(1L)).thenReturn(Optional.of(cart));
        assertThrows(IllegalArgumentException.class, () -> orderService.createOrderFromCart(req));

        // Insufficient stock branch
        CartItem item = new CartItem();
        item.setProduct(product);
        item.setQuantity(15);
        cart.getCartItems().add(item);
        assertThrows(IllegalArgumentException.class, () -> orderService.createOrderFromCart(req));

        // Success branch (also tests fullName null fallback to username)
        item.setQuantity(3);
        user.setFullName("");
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> {
            Order o = inv.getArgument(0);
            o.setId(99L);
            return o;
        });

        OrderResponse resp = orderService.createOrderFromCart(req);
        assertEquals(99L, resp.getOrderId());
        assertEquals("buyer01", resp.getFullName());
        assertEquals(7, product.getStock());
        assertTrue(cart.getCartItems().isEmpty());
    }

    @Test
    @DisplayName("WB-ORD-04: cancelOrder validates state transition and appends cancel reason")
    void testCancelOrderStateTransition() {
        when(userService.getCurrentUser()).thenReturn(user);

        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(1L, 1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> orderService.cancelOrder(1L, "reason"));

        Order shippingOrder = new Order();
        shippingOrder.setId(2L);
        shippingOrder.setUser(user);
        shippingOrder.setStatus(OrderStatus.SHIPPING);
        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(2L, 1L)).thenReturn(Optional.of(shippingOrder));
        assertThrows(IllegalArgumentException.class, () -> orderService.cancelOrder(2L, "too late"));

        Order pendingOrder = new Order();
        pendingOrder.setId(3L);
        pendingOrder.setUser(user);
        pendingOrder.setStatus(OrderStatus.PENDING);
        pendingOrder.setNote("Existing note");
        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(3L, 1L)).thenReturn(Optional.of(pendingOrder));
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> inv.getArgument(0));

        OrderResponse cancelled = orderService.cancelOrder(3L, "Doi y");
        assertEquals(OrderStatus.CANCEL_REQUESTED, cancelled.getStatus());
        assertTrue(cancelled.getNote().contains("[CANCEL REASON]: Doi y"));
    }

    @Test
    @DisplayName("WB-ORD-05: updateOrderStatus covers CONFIRMED, SHIPPING, DELIVERED, CANCELLED stock restoration")
    void testUpdateOrderStatusSwitchBranches() {
        Order order = new Order();
        order.setId(10L);
        order.setUser(user);
        order.setStatus(OrderStatus.PENDING);
        order.setPaymentStatus(PaymentStatus.UNPAID);
        OrderItem oi = new OrderItem();
        oi.setProduct(product);
        oi.setQuantity(2);
        oi.setPrice(product.getPrice());
        order.getItems().add(oi);

        when(orderRepository.findByIdAndDeletedFalse(10L)).thenReturn(Optional.of(order));
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> inv.getArgument(0));

        OrderStatusUpdateRequest req = new OrderStatusUpdateRequest();

        req.setStatus(OrderStatus.CONFIRMED);
        OrderResponse r1 = orderService.updateOrderStatus(10L, req);
        assertEquals(PaymentStatus.PAID, r1.getPaymentStatus());
        assertNotNull(order.getConfirmedAt());

        order.setPaymentStatus(PaymentStatus.UNPAID);
        req.setStatus(OrderStatus.SHIPPING);
        OrderResponse r2 = orderService.updateOrderStatus(10L, req);
        assertEquals(PaymentStatus.PAID, r2.getPaymentStatus());
        assertNotNull(order.getShippedAt());

        order.setPaymentStatus(PaymentStatus.UNPAID);
        req.setStatus(OrderStatus.DELIVERED);
        OrderResponse r3 = orderService.updateOrderStatus(10L, req);
        assertEquals(PaymentStatus.PAID, r3.getPaymentStatus());
        assertNotNull(order.getDeliveredAt());

        // CANCELLED restores stock once
        req.setStatus(OrderStatus.CANCELLED);
        orderService.updateOrderStatus(10L, req);
        assertEquals(12, product.getStock());

        // Already CANCELLED does not restore stock twice
        orderService.updateOrderStatus(10L, req);
        assertEquals(12, product.getStock());
    }

    @Test
    @DisplayName("WB-ORD-06: getUserOrders and getOrderById map fields and throw when not found")
    void testGetOrdersMappingBranches() {
        when(userRepository.findByUsername("buyer01")).thenReturn(Optional.of(user));
        Order o = new Order();
        o.setId(7L);
        o.setOrderCode("VGA-007");
        o.setStatus(OrderStatus.PENDING);
        o.setTotalAmount(new BigDecimal("1000"));
        when(orderRepository.findByUserIdOrderByIdDesc(1L)).thenReturn(List.of(o));

        List<Map<String, Object>> list = orderService.getUserOrders("buyer01");
        assertEquals(1, list.size());
        assertEquals("VGA-007", list.get(0).get("orderCode"));

        when(userService.getCurrentUser()).thenReturn(user);
        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(999L, 1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> orderService.getOrderById(999L));
    }
}
