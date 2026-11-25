package com.example.vgashop.service;

import com.example.vgashop.dto.*;
import com.example.vgashop.entity.*;
import com.example.vgashop.exception.DuplicateResourceException;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AdminServiceWhiteBoxTest {

    @Mock private BrandRepository brandRepository;
    @Mock private CategoryRepository categoryRepository;
    @Mock private OrderRepository orderRepository;
    @Mock private PaymentRepository paymentRepository;
    @Mock private ProductRepository productRepository;
    @Mock private UserRepository userRepository;
    @Mock private BlogRepository blogRepository;

    private AdminService adminService;
    private final List<Path> uploadedFilesToCleanup = new ArrayList<>();

    @BeforeEach
    void setUp() {
        adminService = new AdminService(
                brandRepository, categoryRepository, orderRepository,
                paymentRepository, productRepository, userRepository, blogRepository);
    }

    @AfterEach
    void cleanup() throws IOException {
        for (Path p : uploadedFilesToCleanup) {
            Files.deleteIfExists(p);
        }
        uploadedFilesToCleanup.clear();
    }

    @Test
    @DisplayName("WB-ADM-01: getDashboard computes non-cancelled orders, today stats, and handles lowStock failure")
    void testGetDashboard() {
        Order deliveredToday = new Order();
        deliveredToday.setId(1L);
        deliveredToday.setStatus(OrderStatus.DELIVERED);
        deliveredToday.setTotalAmount(new BigDecimal("10000000"));
        deliveredToday.setCreatedAt(LocalDateTime.now());

        Order oldPending = new Order();
        oldPending.setId(2L);
        oldPending.setStatus(OrderStatus.PENDING);
        oldPending.setTotalAmount(null);
        oldPending.setCreatedAt(LocalDateTime.now().minusDays(2));

        Order cancelled = new Order();
        cancelled.setId(3L);
        cancelled.setStatus(OrderStatus.CANCELLED);
        cancelled.setTotalAmount(new BigDecimal("5000000"));

        Order deletedOrder = new Order();
        deletedOrder.setId(4L);
        deletedOrder.setDeleted(true);

        when(orderRepository.findAll()).thenReturn(List.of(deliveredToday, oldPending, cancelled, deletedOrder));
        when(userRepository.countByDeletedFalse()).thenReturn(12L);
        when(productRepository.countByDeletedFalse()).thenReturn(30L);
        when(productRepository.countLowStock(10)).thenThrow(new RuntimeException("DB error"));

        AdminDashboardResponse res = adminService.getDashboard();
        assertEquals(2L, res.getTotalOrders());
        assertEquals(1L, res.getTodayOrders());
        assertEquals(new BigDecimal("10000000"), res.getTotalRevenue());
        assertEquals(12L, res.getTotalUsers());
        assertEquals(30L, res.getTotalProducts());
        assertEquals(0L, res.getLowStockProducts());
    }

    @Test
    @DisplayName("WB-ADM-02: getAllUsers, createUser, changeUserRole, toggleUserStatus, softDeleteUser")
    void testUserManagementBranches() {
        User normalUser = new User();
        normalUser.setId(10L);
        normalUser.setUsername("cust01");
        normalUser.setEmail("cust01@vga.vn");
        normalUser.setRole(Role.USER);
        normalUser.setStatus(true);

        when(userRepository.searchActiveUsers(any(), any(), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(normalUser)));
        assertEquals(1, adminService.getAllUsers(0, 10, "id", "asc", "cust", "USER").getTotalElements());
        assertEquals(1, adminService.getAllUsers(0, 10, "id", "desc", " ", "INVALID_ROLE").getTotalElements());

        UserDTO dto = new UserDTO();
        dto.setUsername("newuser");
        dto.setEmail("new@vga.vn");
        dto.setPassword("123456");

        when(userRepository.existsByUsername("newuser")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> adminService.createUser(dto));

        when(userRepository.existsByUsername("newuser")).thenReturn(false);
        when(userRepository.existsByEmail("new@vga.vn")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> adminService.createUser(dto));

        when(userRepository.existsByEmail("new@vga.vn")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User u = inv.getArgument(0);
            u.setId(55L);
            return u;
        });
        dto.setRole(null);
        assertEquals(Role.USER, adminService.createUser(dto).getRole());
        dto.setRole("ADMIN");
        assertEquals(Role.ADMIN, adminService.createUser(dto).getRole());

        // changeUserRole
        when(userRepository.findByIdAndDeleted(10L, false)).thenReturn(Optional.of(normalUser));
        assertThrows(IllegalArgumentException.class, () -> adminService.changeUserRole(10L, "SUPERUSER"));
        adminService.changeUserRole(10L, "STAFF");
        assertEquals(Role.STAFF, normalUser.getRole());

        // toggleUserStatus & softDeleteUser guards
        User selfAdmin = new User();
        selfAdmin.setId(1L);
        selfAdmin.setUsername("admin");
        selfAdmin.setRole(Role.ADMIN);
        selfAdmin.setStatus(true);
        when(userRepository.findByIdAndDeleted(1L, false)).thenReturn(Optional.of(selfAdmin));
        assertThrows(IllegalStateException.class, () -> adminService.toggleUserStatus(1L, "admin"));
        assertThrows(IllegalStateException.class, () -> adminService.softDeleteUser(1L, "admin"));

        User otherAdmin = new User();
        otherAdmin.setId(2L);
        otherAdmin.setUsername("admin2");
        otherAdmin.setRole(Role.ADMIN);
        when(userRepository.findByIdAndDeleted(2L, false)).thenReturn(Optional.of(otherAdmin));
        assertThrows(IllegalStateException.class, () -> adminService.toggleUserStatus(2L, "admin"));
        assertThrows(IllegalStateException.class, () -> adminService.softDeleteUser(2L, "admin"));

        adminService.toggleUserStatus(10L, "admin");
        assertFalse(normalUser.getStatus());
        adminService.softDeleteUser(10L, "admin");
        assertTrue(normalUser.isDeleted());
    }

    @Test
    @DisplayName("WB-ADM-03: getAllOrders, updateOrderStatus, getOrderDetailsForAdmin, getDashboardCharts")
    void testOrderAndChartOperations() {
        User u = new User();
        u.setUsername("u1");
        u.setEmail("u1@vga.vn");

        Brand brand = new Brand("NVIDIA");
        Product prod = new Product();
        prod.setId(7L);
        prod.setName("RTX 4090");
        prod.setBrand(brand);
        prod.setPrice(new BigDecimal("45000000"));
        prod.setStock(5);

        Order o = new Order();
        o.setId(20L);
        o.setOrderCode("VGA-20");
        o.setUser(u);
        o.setStatus(OrderStatus.DELIVERED);
        o.setPaymentStatus(PaymentStatus.SUCCESS);
        o.setTotalAmount(new BigDecimal("45000000"));
        o.setCreatedAt(LocalDateTime.now());
        OrderItem oi = new OrderItem();
        oi.setProduct(prod);
        oi.setQuantity(1);
        oi.setPrice(new BigDecimal("45000000"));
        o.getItems().add(oi);

        when(orderRepository.findByStatusAndDeletedFalse(eq(OrderStatus.DELIVERED), any())).thenReturn(new PageImpl<>(List.of(o)));
        when(orderRepository.findByDeletedFalse(any())).thenReturn(new PageImpl<>(List.of(o)));
        assertEquals(1, adminService.getAllOrders(0, 10, "id", "asc", "DELIVERED").getTotalElements());
        assertEquals(1, adminService.getAllOrders(0, 10, "id", "desc", "BAD_STATUS").getTotalElements());
        assertEquals(1, adminService.getAllOrders(0, 10, "id", "asc", null).getTotalElements());

        when(orderRepository.findByIdAndDeletedFalse(20L)).thenReturn(Optional.of(o));
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> inv.getArgument(0));
        Payment p = new Payment();
        p.setPaymentMethod(PaymentMethod.VNPAY);
        when(paymentRepository.findByOrder_IdAndDeletedFalse(20L)).thenReturn(Optional.of(p));

        OrderStatusUpdateRequest req = new OrderStatusUpdateRequest();
        req.setStatus(OrderStatus.CONFIRMED);
        assertEquals("VNPAY", adminService.updateOrderStatus(20L, req).getPaymentMethod());
        req.setStatus(OrderStatus.SHIPPING);
        assertNotNull(adminService.updateOrderStatus(20L, req));
        req.setStatus(OrderStatus.DELIVERED);
        assertEquals("VGA-20", adminService.getOrderDetailsForAdmin(20L).getOrderCode());

        Order cancelledOrder = new Order();
        cancelledOrder.setId(21L);
        cancelledOrder.setStatus(OrderStatus.CANCELLED);
        cancelledOrder.setCreatedAt(LocalDateTime.now());
        when(orderRepository.findAll()).thenReturn(List.of(o, cancelledOrder));

        for (String period : List.of("today", "7days", "1month", "1year", "6months")) {
            Map<String, Object> chart = adminService.getDashboardCharts(period);
            assertNotNull(chart.get("chartData"));
            assertNotNull(chart.get("brandData"));
        }
    }

    @Test
    @DisplayName("WB-ADM-04: Catalog, Stock, Blog CRUD and pinToTop all entity switch cases")
    void testCatalogBlogAndPinOperations() {
        Product p = new Product();
        p.setId(1L);
        p.setName("RTX 4070");
        p.setPrice(new BigDecimal("18000000"));
        p.setStock(5);
        p.setStatus(true);

        when(productRepository.searchAdminProducts(eq("RTX"), any())).thenReturn(new PageImpl<>(List.of(p)));
        when(productRepository.findByDeletedFalse(any())).thenReturn(new PageImpl<>(List.of(p)));
        assertEquals(1, adminService.getAllProductForAdmin(0, 10, "RTX").getTotalElements());
        assertEquals(1, adminService.getAllProductForAdmin(0, 10, "").getTotalElements());

        when(productRepository.findByIdAndDeletedFalse(1L)).thenReturn(Optional.of(p));
        assertThrows(IllegalArgumentException.class, () -> adminService.updateProductStock(1L, -5));
        adminService.updateProductStock(1L, 12);
        assertEquals(12, p.getStock());
        adminService.softDeleteProduct(1L);
        assertTrue(p.isDeleted());

        when(categoryRepository.findByDeletedFalse(any())).thenReturn(Page.empty());
        when(brandRepository.findByDeletedFalse(any())).thenReturn(Page.empty());
        adminService.getAllCategoriesForAdmin(0, 10);
        adminService.getAllBrandsForAdmin(0, 10);

        Category c = new Category();
        c.setId(2L);
        c.setName("Mid-range");
        when(categoryRepository.existsByNameIgnoreCase("Mid-range")).thenReturn(true);
        assertThrows(IllegalArgumentException.class, () -> adminService.addCategories(c));
        when(categoryRepository.existsByNameIgnoreCase("Mid-range")).thenReturn(false);
        when(categoryRepository.save(c)).thenReturn(c);
        assertSame(c, adminService.addCategories(c));
        when(categoryRepository.findByIdAndDeleted(2L, false)).thenReturn(Optional.of(c));
        assertSame(c, adminService.updateCategory(2L, c));
        adminService.deleteCategory(2L);
        verify(categoryRepository).delete(c);

        Brand b = new Brand("MSI");
        b.setId(3L);
        when(brandRepository.existsByNameIgnoreCase("MSI")).thenReturn(true);
        assertThrows(IllegalArgumentException.class, () -> adminService.addBrand(b));
        when(brandRepository.existsByNameIgnoreCase("MSI")).thenReturn(false);
        when(brandRepository.save(b)).thenReturn(b);
        assertSame(b, adminService.addBrand(b));
        when(brandRepository.findByIdAndDeleted(3L, false)).thenReturn(Optional.of(b));
        assertSame(b, adminService.updateBrand(3L, b));
        adminService.deleteBrand(3L);
        verify(brandRepository).delete(b);

        // Blog CRUD + file upload
        BlogDTO bdto = new BlogDTO();
        bdto.setTitle("Review RTX 5090");
        bdto.setCategory("News");
        bdto.setExcerpt("Short");
        bdto.setContent("Long content");
        bdto.setFeatured(true);
        bdto.setTags("rtx,nvidia");

        MockMultipartFile img = new MockMultipartFile("image", "thumb_wb_test.png", "image/png", new byte[]{1, 2, 3});
        when(blogRepository.save(any(Blog.class))).thenAnswer(inv -> {
            Blog saved = inv.getArgument(0);
            if (saved.getThumbnail() != null && saved.getThumbnail().startsWith("/uploads/blogs/")) {
                uploadedFilesToCleanup.add(Paths.get("uploads", "blogs", saved.getThumbnail().replace("/uploads/blogs/", "")));
            }
            return saved;
        });
        Blog createdBlog = adminService.createBlog(bdto, img);
        assertTrue(createdBlog.getThumbnail().startsWith("/uploads/blogs/"));

        createdBlog.setId(4L);
        createdBlog.setViews(null);
        when(blogRepository.findById(4L)).thenReturn(Optional.of(createdBlog));
        assertEquals(0, adminService.updateBlog(4L, bdto, null).getViews());
        adminService.deleteBlog(4L);
        assertTrue(createdBlog.isDeleted());

        // pinToTop all cases
        when(productRepository.findById(1L)).thenReturn(Optional.of(p));
        when(blogRepository.findById(4L)).thenReturn(Optional.of(createdBlog));
        when(categoryRepository.findById(2L)).thenReturn(Optional.of(c));
        when(brandRepository.findById(3L)).thenReturn(Optional.of(b));
        adminService.pinToTop("product", 1L);
        adminService.pinToTop("blog", 4L);
        adminService.pinToTop("category", 2L);
        adminService.pinToTop("brand", 3L);
        assertThrows(IllegalArgumentException.class, () -> adminService.pinToTop("unknown", 1L));
    }
}
