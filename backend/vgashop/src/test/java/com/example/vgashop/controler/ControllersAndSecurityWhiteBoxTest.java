package com.example.vgashop.controler;

import com.example.vgashop.dto.*;
import com.example.vgashop.entity.*;
import com.example.vgashop.repository.*;
import com.example.vgashop.security.JwtAuthFilter;
import com.example.vgashop.security.JwtFilter;
import com.example.vgashop.security.JwtUtil;
import com.example.vgashop.service.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import java.math.BigDecimal;
import java.security.Principal;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ControllersAndSecurityWhiteBoxTest {

    @Mock private AuthService authService;
    @Mock private CartService cartService;
    @Mock private OrderService orderService;
    @Mock private PaymentService paymentService;
    @Mock private PaymentRepository paymentRepository;
    @Mock private OrderRepository orderRepository;
    @Mock private SystemSettingService settingService;
    @Mock private BlogRepository blogRepository;
    @Mock private ReviewRepository reviewRepository;
    @Mock private ProductRepository productRepository;
    @Mock private UserRepository userRepository;
    @Mock private OrderItemRepository orderItemRepository;
    @Mock private JwtUtil jwtUtil;

    @InjectMocks private BlogController blogController;
    @InjectMocks private ReviewController reviewController;

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    @DisplayName("WB-CTRL-01: AuthController covers register, registerAdmin, login, googleLogin ok & error")
    void testAuthControllerBranches() {
        AuthController ctrl = new AuthController(authService);

        RegisterRequest rr = new RegisterRequest();
        rr.setUsername("u1");
        when(authService.register(rr)).thenReturn(new AuthResponse("tok", "u1", "e@v.vn", "USER", 1L));
        assertEquals(HttpStatus.OK, ctrl.register(rr).getStatusCode());

        when(authService.register(rr)).thenThrow(new RuntimeException("dup"));
        assertEquals(HttpStatus.BAD_REQUEST, ctrl.register(rr).getStatusCode());

        UserDTO ud = new UserDTO();
        when(authService.register(ud)).thenReturn(new AuthResponse("tok", "admin", "a@v.vn", "ADMIN", 2L));
        assertTrue(ctrl.registerAdmin(ud).isSuccess());

        LoginRequest lr = new LoginRequest();
        lr.setUsername("u1");
        lr.setPassword("p1");
        when(authService.login("u1", "p1")).thenReturn(new AuthResponse("tok", "u1", "e@v.vn", "USER", 1L));
        assertEquals(HttpStatus.OK, ctrl.login(lr).getStatusCode());
        when(authService.login("u1", "p1")).thenThrow(new RuntimeException("bad"));
        assertEquals(HttpStatus.BAD_REQUEST, ctrl.login(lr).getStatusCode());

        GoogleLoginRequest gr = new GoogleLoginRequest();
        gr.setEmail("g@v.vn");
        when(authService.googleLogin(gr)).thenReturn(new AuthResponse("tok", "g", "g@v.vn", "USER", 3L));
        assertEquals(HttpStatus.OK, ctrl.googleLogin(gr).getStatusCode());
        when(authService.googleLogin(gr)).thenThrow(new RuntimeException("err"));
        assertEquals(HttpStatus.BAD_REQUEST, ctrl.googleLogin(gr).getStatusCode());
    }

    @Test
    @DisplayName("WB-CTRL-02: CartController and OrderController endpoint wrappers")
    void testCartAndOrderControllers() {
        CartController cartCtrl = new CartController(cartService);
        when(cartService.getMyCart()).thenReturn(new CartResponse());
        when(cartService.addToCart(any())).thenReturn(new CartResponse());
        when(cartService.updateCartItem(eq(1L), any())).thenReturn(new CartResponse());
        when(cartService.removeCartItem(1L)).thenReturn(new CartResponse());

        assertTrue(cartCtrl.getMyCart().isSuccess());
        assertTrue(cartCtrl.addToCart(new AddToCartRequest(1L, 1)).isSuccess());
        assertTrue(cartCtrl.updateCartItem(1L, new UpdateCartItemRequest(2)).isSuccess());
        assertTrue(cartCtrl.removeCartItem(1L).isSuccess());
        assertTrue(cartCtrl.clearCart().isSuccess());

        OrderController orderCtrl = new OrderController(orderService);
        Authentication auth = mock(Authentication.class);
        when(auth.getName()).thenReturn("buyer");
        OrderRequest oreq = new OrderRequest();

        when(orderService.placeOrder(oreq, "buyer")).thenReturn(Map.of("orderId", 1L));
        assertEquals(HttpStatus.OK, orderCtrl.placeOrder(oreq, auth).getStatusCode());
        when(orderService.placeOrder(oreq, "buyer")).thenThrow(new RuntimeException("fail"));
        assertEquals(HttpStatus.BAD_REQUEST, orderCtrl.placeOrder(oreq, auth).getStatusCode());

        when(orderService.getUserOrders("buyer")).thenReturn(List.of());
        assertEquals(HttpStatus.OK, orderCtrl.getMyOrdersList(auth).getStatusCode());
        when(orderService.getUserOrders("buyer")).thenThrow(new RuntimeException("fail"));
        assertEquals(HttpStatus.BAD_REQUEST, orderCtrl.getMyOrdersList(auth).getStatusCode());

        when(orderService.getMyOrders(0, 10, "createdAt", "desc")).thenReturn(Page.empty());
        when(orderService.getAllOrders(0, 10, "createdAt", "desc")).thenReturn(Page.empty());
        assertTrue(orderCtrl.createOrder(new CreateOrderRequest()).isSuccess());
        assertTrue(orderCtrl.getMyOrdersPage(0, 10, "createdAt", "desc").isSuccess());
        assertTrue(orderCtrl.getOrderById(1L).isSuccess());
        assertEquals(HttpStatus.OK, orderCtrl.cancelOrder(1L, "reason").getStatusCode());
        assertTrue(orderCtrl.getAllOrders(0, 10, "createdAt", "desc").isSuccess());
        assertTrue(orderCtrl.updateOrderStatus(1L, new OrderStatusUpdateRequest()).isSuccess());
    }

    @Test
    @DisplayName("WB-CTRL-03: PaymentController, SystemSettingController, BlogController, ReviewController")
    void testPaymentSettingsBlogReviewControllers() {
        PaymentController payCtrl = new PaymentController(paymentService, paymentRepository, orderRepository);
        MockHttpServletRequest req = new MockHttpServletRequest();
        req.addHeader("X-Forwarded-For", "10.0.0.1, 10.0.0.2");

        assertTrue(payCtrl.createPayment(1L, new PaymentRequest(), req).isSuccess());
        when(paymentService.getMyPayments(10, 0, "createdAt", "desc")).thenReturn(Page.empty());
        when(paymentService.getAllPayments(10, 0, "createdAt", "desc")).thenReturn(Page.empty());
        when(paymentService.getPaymentsByStatus(PaymentStatus.PENDING, 10, 0, "createdAt", "desc")).thenReturn(Page.empty());
        assertTrue(payCtrl.getMyPayments(0, 10, "createdAt", "desc").isSuccess());
        assertTrue(payCtrl.getAllPayments(0, 10, "createdAt", "desc").isSuccess());
        assertTrue(payCtrl.getPaymentById(1L).isSuccess());
        assertTrue(payCtrl.getPaymentsByStatus(PaymentStatus.PENDING, 0, 10, "createdAt", "desc").isSuccess());
        assertTrue(payCtrl.updatePaymentStatus(1L, PaymentStatus.SUCCESS, "TXN").isSuccess());

        // Callback signature verification failed branches
        when(paymentService.getVnpayHashSecret()).thenReturn("SECRET");
        when(paymentService.getMomoSecretKey()).thenReturn("SECRET");
        assertFalse(payCtrl.vnpayCallback(new HashMap<>(Map.of("vnp_SecureHash", "bad"))).isSuccess());
        assertFalse(payCtrl.momoCallback(new HashMap<>(Map.of("signature", "bad"))).isSuccess());

        // Settings
        SystemSettingController setCtrl = new SystemSettingController(settingService);
        when(settingService.getAllSettings()).thenReturn(Map.of("site", "VGA Store"));
        assertEquals("VGA Store", setCtrl.getPublicSettings().getBody().get("site"));
        assertEquals("VGA Store", setCtrl.getAdminSettings().getBody().get("site"));
        assertEquals(HttpStatus.OK, setCtrl.updateSettings(Map.of("k", "v")).getStatusCode());

        // Blog
        Blog b = new Blog();
        b.setId(1L);
        b.setViews(null);
        when(blogRepository.findAll(any(Sort.class))).thenReturn(List.of(b));
        when(blogRepository.findById(1L)).thenReturn(Optional.of(b));
        when(blogRepository.findById(99L)).thenReturn(Optional.empty());
        when(blogRepository.findByFeaturedTrue()).thenReturn(List.of(b));
        when(blogRepository.findByCategory("GPU")).thenReturn(List.of(b));
        assertEquals(1, blogController.getAllBlogs().getBody().size());
        assertEquals(1, blogController.getBlogById(1L).getBody().getViews());
        assertEquals(HttpStatus.NOT_FOUND, blogController.getBlogById(99L).getStatusCode());
        assertEquals(1, blogController.getFeaturedBlogs().getBody().size());
        assertEquals(1, blogController.getBlogsByCategory("GPU").getBody().size());

        // Review
        Review rev = new Review();
        rev.setId(10L);
        rev.setRating(5);
        rev.setComment("Tot");
        User u = new User();
        u.setId(1L);
        u.setUsername("u1");
        u.setFullName("User One");
        Product prod = new Product();
        prod.setId(2L);
        prod.setName("RTX 4070");
        rev.setUser(u);
        rev.setProduct(prod);

        when(reviewRepository.findByProductIdOrderByCreatedAtDesc(2L)).thenReturn(List.of(rev));
        when(reviewRepository.findByBlogIdOrderByCreatedAtDesc(1L)).thenReturn(List.of(rev));
        assertEquals(1, reviewController.getReviewsByProduct(2L).getBody().size());
        assertEquals(1, reviewController.getReviewsByBlog(1L).getBody().size());

        Principal principal = () -> "u1";
        assertFalse(reviewController.canReview(2L, null).getBody());
        when(userRepository.findByUsername("u1")).thenReturn(Optional.of(u));
        when(orderItemRepository.existsByOrder_User_IdAndOrder_StatusAndProduct_Id(1L, OrderStatus.DELIVERED, 2L)).thenReturn(true);
        when(reviewRepository.existsByUser_IdAndProduct_Id(1L, 2L)).thenReturn(false);
        assertTrue(reviewController.canReview(2L, principal).getBody());

        when(productRepository.findProductsPendingReview(1L)).thenReturn(List.of(prod));
        assertEquals(1, reviewController.getPendingReviews(principal).getBody().size());
        assertTrue(reviewController.getPendingReviews(null).getBody().isEmpty());
    }

    @Test
    @DisplayName("WB-SEC-01: JwtAuthFilter and JwtFilter set SecurityContext on valid Bearer token and clear on exception")
    void testJwtFilters() throws Exception {
        JwtAuthFilter f1 = new JwtAuthFilter(jwtUtil);
        JwtFilter f2 = new JwtFilter(jwtUtil);

        MockHttpServletRequest req = new MockHttpServletRequest();
        req.addHeader("Authorization", "Bearer valid.jwt.token");
        MockHttpServletResponse res = new MockHttpServletResponse();

        when(jwtUtil.validateToken("valid.jwt.token")).thenReturn(true);
        when(jwtUtil.extractUsername("valid.jwt.token")).thenReturn("admin");
        when(jwtUtil.extractRole("valid.jwt.token")).thenReturn("ADMIN");

        f1.doFilter(req, res, new MockFilterChain());
        assertNotNull(SecurityContextHolder.getContext().getAuthentication());
        assertEquals("admin", SecurityContextHolder.getContext().getAuthentication().getName());

        SecurityContextHolder.clearContext();
        f2.doFilter(req, res, new MockFilterChain());
        assertNotNull(SecurityContextHolder.getContext().getAuthentication());

        // Exception branch clears context
        when(jwtUtil.validateToken("bad.token")).thenThrow(new RuntimeException("tampered"));
        MockHttpServletRequest badReq = new MockHttpServletRequest();
        badReq.addHeader("Authorization", "Bearer bad.token");
        f1.doFilter(badReq, res, new MockFilterChain());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        f2.doFilter(badReq, res, new MockFilterChain());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
}
