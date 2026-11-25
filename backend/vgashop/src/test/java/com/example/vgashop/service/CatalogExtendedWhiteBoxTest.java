package com.example.vgashop.service;

import com.example.vgashop.dto.ProductImageDTO;
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
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.*;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CatalogExtendedWhiteBoxTest {

    @Mock private ProductRepository productRepository;
    @Mock private BrandRepository brandRepository;
    @Mock private CategoryRepository categoryRepository;
    @Mock private OrderRepository orderRepository;
    @Mock private OrderItemRepository orderItemRepository;
    @Mock private CartRepository cartRepository;
    @Mock private UserRepository userRepository;
    @Mock private UserService userService;
    @Mock private PaymentRepository paymentRepository;

    private BrandService brandService;
    private CategoryService categoryService;
    private ProductService productService;
    private OrderService orderService;
    private final List<Path> uploadedFilesToCleanup = new ArrayList<>();

    @BeforeEach
    void setUp() {
        brandService = new BrandService(brandRepository);
        categoryService = new CategoryService(categoryRepository);
        productService = new ProductService(productRepository, brandService, categoryService);
        orderService = new OrderService(orderRepository, orderItemRepository, cartRepository,
                productRepository, userRepository, userService, paymentRepository);
    }

    @AfterEach
    void cleanup() throws IOException {
        for (Path p : uploadedFilesToCleanup) {
            Files.deleteIfExists(p);
        }
        uploadedFilesToCleanup.clear();
    }

    @Test
    @DisplayName("WB-PROD-04: updateProduct, deleteProduct, filterByBrand, searchAndFilter")
    void testProductExtendedCrud() {
        Product existing = new Product();
        existing.setId(1L);
        existing.setName("RTX 4070 Super");
        existing.setSku("SKU-4070S");
        existing.setPrice(new BigDecimal("19000000"));
        existing.setStock(5);

        Product update = new Product();
        update.setName("RTX 4070 Super OC");
        update.setPrice(new BigDecimal("19500000"));
        update.setStock(10);

        when(productRepository.findByBrand_Name(eq("ASUS"), any())).thenReturn(Page.empty());
        when(productRepository.findByNameContainingAndBrand_Name(eq("RTX"), eq("ASUS"), any())).thenReturn(Page.empty());
        assertNotNull(productService.filterByBrand("ASUS"));
        assertNotNull(productService.searchAndFilter("RTX", "ASUS", PageRequest.of(0, 5)));

        when(productRepository.findByIdAndDeleted(1L, false)).thenReturn(Optional.of(existing));
        when(productRepository.findByIdAndDeleted(999L, false)).thenReturn(Optional.empty());
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> inv.getArgument(0));

        assertEquals("RTX 4070 Super OC", productService.updateProduct(1L, update).getName());
        assertThrows(ResourceNotFoundException.class, () -> productService.updateProduct(999L, update));

        when(productRepository.existsByIdAndDeleted(999L, false)).thenReturn(false);
        assertThrows(ResourceNotFoundException.class, () -> productService.deleteProduct(999L));

        when(productRepository.existsByIdAndDeleted(1L, false)).thenReturn(true);
        productService.deleteProduct(1L);
        assertTrue(existing.isDeleted());
    }

    @Test
    @DisplayName("WB-PROD-05: createProductWithImage and updateProductWithImage with upload cleanup")
    void testProductWithImageBranches() {
        ProductImageDTO dto = new ProductImageDTO();
        dto.setName("RTX 5080 Gaming");
        dto.setSku("SKU-5080");
        dto.setPrice(new BigDecimal("35000000"));
        dto.setStock(4);
        dto.setBrandId(1L);
        dto.setCategoryId(2L);

        when(productRepository.existsByNameIgnoreCase("RTX 5080 Gaming")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> productService.createProductWithImage(dto));

        when(productRepository.existsByNameIgnoreCase("RTX 5080 Gaming")).thenReturn(false);
        when(productRepository.existsBySkuIgnoreCase("SKU-5080")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> productService.createProductWithImage(dto));

        when(productRepository.existsBySkuIgnoreCase("SKU-5080")).thenReturn(false);
        assertThrows(IllegalArgumentException.class, () -> productService.createProductWithImage(dto));

        MockMultipartFile file = new MockMultipartFile("imageFile", "vga_wb_test.jpg", "image/jpeg", new byte[]{10, 20, 30});
        dto.setImageFile(file);
        Brand brand = new Brand("ASUS");
        Category cat = new Category();
        cat.setName("RTX Series");
        when(brandRepository.findByIdAndDeleted(1L, false)).thenReturn(Optional.of(brand));
        when(categoryRepository.findByIdAndDeleted(2L, false)).thenReturn(Optional.of(cat));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> {
            Product p = inv.getArgument(0);
            if (p.getImgUrl() != null && p.getImgUrl().startsWith("/uploads/products/")) {
                uploadedFilesToCleanup.add(Paths.get("uploads", "products", p.getImgUrl().replace("/uploads/products/", "")));
            }
            return p;
        });

        Product created = productService.createProductWithImage(dto);
        assertTrue(created.getImgUrl().startsWith("/uploads/products/"));

        created.setId(5L);
        created.setSku("SKU-OLD");
        when(productRepository.findByIdAndDeleted(5L, false)).thenReturn(Optional.of(created));
        dto.setName("RTX 5080 OC");
        dto.setSku("SKU-5080-NEW");
        when(productRepository.existsByNameIgnoreCase("RTX 5080 OC")).thenReturn(false);
        when(productRepository.existsBySkuIgnoreCase("SKU-5080-NEW")).thenReturn(false);
        Product updated = productService.updateProductWithImage(5L, dto);
        assertEquals("RTX 5080 OC", updated.getName());
    }

    @Test
    @DisplayName("WB-CATBRAND-02: Extended CategoryService and BrandService update, delete, search branches")
    void testExtendedCategoryAndBrandBranches() {
        when(categoryRepository.findByDeletedFalse(any(Pageable.class))).thenReturn(Page.empty());
        when(categoryRepository.findByActiveTrue(any(Pageable.class))).thenReturn(Page.empty());
        when(categoryRepository.findByNameContaining(eq("RX"), any(Pageable.class))).thenReturn(Page.empty());
        categoryService.getAllCategories(PageRequest.of(0, 5));
        categoryService.getActiveCategories(PageRequest.of(0, 5));
        categoryService.searchCategory("", PageRequest.of(0, 5));
        categoryService.searchCategory("RX", PageRequest.of(0, 5));

        Category c = new Category();
        c.setId(1L);
        c.setName("Radeon");
        c.setActive(true);
        Category cUpd = new Category();
        cUpd.setName("Radeon RX");
        cUpd.setDescription("AMD GPU");
        cUpd.setActive(false);

        when(categoryRepository.findByIdAndDeleted(1L, false)).thenReturn(Optional.of(c));
        when(categoryRepository.existsByNameIgnoreCase("Radeon RX")).thenReturn(false);
        when(categoryRepository.save(any(Category.class))).thenAnswer(inv -> inv.getArgument(0));
        assertEquals("Radeon RX", categoryService.updateCategory(1L, cUpd).getName());

        when(categoryRepository.existsByIdAndDeleted(1L, false)).thenReturn(true);
        categoryService.deleteCategory(1L);
        verify(categoryRepository).delete(c);

        // BrandService
        when(brandRepository.findAll(any(Pageable.class))).thenReturn(Page.empty());
        when(brandRepository.findAll(any(Sort.class))).thenReturn(Collections.emptyList());
        when(brandRepository.findByNameContaining(eq("MSI"), any(Pageable.class))).thenReturn(Page.empty());
        brandService.getAllBrands(0, 10, "name", "asc");
        brandService.getAllNoPage();
        brandService.searchBrand("", 0, 10);
        brandService.searchBrand("MSI", 0, 10);

        Brand b = new Brand("GIGABYTE");
        b.setId(2L);
        b.setSlug("gigabyte");
        Brand bUpd = new Brand("AORUS GAMING");
        bUpd.setStatus(true);
        bUpd.setSlug("aorus-gaming");
        when(brandRepository.findByIdAndDeleted(2L, false)).thenReturn(Optional.of(b));
        when(brandRepository.existsByNameIgnoreCase("AORUS GAMING")).thenReturn(false);
        when(brandRepository.save(any(Brand.class))).thenAnswer(inv -> inv.getArgument(0));
        assertEquals("aorus-gaming", brandService.updateBrand(2L, bUpd).getSlug());

        bUpd.setName("AORUS GAMING");
        assertThrows(DuplicateResourceException.class, () -> {
            Brand dup = new Brand("DUP BRAND");
            when(brandRepository.existsByNameIgnoreCase("DUP BRAND")).thenReturn(true);
            brandService.updateBrand(2L, dup);
        });

        when(brandRepository.existsByIdAndDeleted(2L, false)).thenReturn(true);
        brandService.deleteBrand(2L);
        verify(brandRepository).delete(b);
    }

    @Test
    @DisplayName("WB-ORD-07: OrderService getMyOrders, getAllOrders, getOrderById success")
    void testOrderServicePaginationAndFetch() {
        User user = new User();
        user.setId(1L);
        user.setUsername("buyer");
        Order o = new Order();
        o.setId(55L);
        o.setOrderCode("VGA-55");
        o.setUser(user);
        o.setStatus(OrderStatus.CONFIRMED);
        o.setPaymentStatus(PaymentStatus.PAID);
        o.setTotalAmount(new BigDecimal("12000000"));

        when(userService.getCurrentUser()).thenReturn(user);
        when(orderRepository.findByUser_IdAndDeletedFalse(eq(1L), any(Pageable.class))).thenReturn(new PageImpl<>(List.of(o)));
        when(orderRepository.findByDeletedFalse(any(Pageable.class))).thenReturn(new PageImpl<>(List.of(o)));
        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(55L, 1L)).thenReturn(Optional.of(o));
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> inv.getArgument(0));

        assertEquals(1, orderService.getMyOrders(0, 10, "id", "desc").getTotalElements());
        assertEquals(1, orderService.getAllOrders(0, 10, "id", "asc").getTotalElements());
        assertEquals("VGA-55", orderService.getOrderById(55L).getOrderCode());
        assertEquals(OrderStatus.CANCEL_REQUESTED, orderService.cancelOrder(55L, "").getStatus());
    }
}
