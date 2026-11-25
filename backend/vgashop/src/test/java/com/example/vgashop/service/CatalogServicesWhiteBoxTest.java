package com.example.vgashop.service;

import com.example.vgashop.entity.Brand;
import com.example.vgashop.entity.Category;
import com.example.vgashop.entity.Product;
import com.example.vgashop.exception.DuplicateResourceException;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.BrandRepository;
import com.example.vgashop.repository.CategoryRepository;
import com.example.vgashop.repository.ProductRepository;
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

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CatalogServicesWhiteBoxTest {

    @Mock private ProductRepository productRepository;
    @Mock private BrandRepository brandRepository;
    @Mock private CategoryRepository categoryRepository;

    private BrandService brandService;
    private CategoryService categoryService;
    private ProductService productService;

    @BeforeEach
    void setUp() {
        brandService = new BrandService(brandRepository);
        categoryService = new CategoryService(categoryRepository);
        productService = new ProductService(productRepository, brandService, categoryService);
    }

    @Test
    @DisplayName("WB-PROD-01: getAllProducts covers asc/desc sort branches and getProductById missing branch")
    void testProductSortAndGetById() {
        when(productRepository.findByDeletedFalse(any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(new Product())));

        assertEquals(1, productService.getAllProducts(0, 10, "price", "asc").getTotalElements());
        assertEquals(1, productService.getAllProducts(0, 10, "price", "desc").getTotalElements());

        when(productRepository.findByIdAndDeleted(404L, false)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> productService.getProductById(404L));
    }

    @Test
    @DisplayName("WB-PROD-02: searchProducts and filterProducts cover null, empty, and brandIds list branches")
    void testProductSearchAndFilterBranches() {
        when(productRepository.findAll(any(Pageable.class))).thenReturn(new PageImpl<>(Collections.emptyList()));
        when(productRepository.findByNameContaining(eq("RTX"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(new Product())));

        productService.searchProducts(null, PageRequest.of(0, 5));
        productService.searchProducts("   ", PageRequest.of(0, 5));
        Page<Product> res = productService.searchProducts("RTX", PageRequest.of(0, 5));
        assertEquals(1, res.getTotalElements());

        when(productRepository.findByNameContainingAndPriceBetween(anyString(), anyDouble(), anyDouble(), any()))
                .thenReturn(Page.empty());
        when(productRepository.findByNameContainingAndBrand_IdInAndPriceBetween(anyString(), anyList(), anyDouble(), anyDouble(), any()))
                .thenReturn(Page.empty());

        productService.filterProducts(null, null, null, null, 0, 10, "id", "asc");
        productService.filterProducts("RTX", Collections.emptyList(), 100.0, 5000.0, 0, 10, "price", "desc");
        productService.filterProducts("RTX", List.of(1L, 2L), 100.0, 5000.0, 0, 10, "id", "asc");

        verify(productRepository, times(2)).findByNameContainingAndPriceBetween(anyString(), anyDouble(), anyDouble(), any());
        verify(productRepository, times(1)).findByNameContainingAndBrand_IdInAndPriceBetween(anyString(), anyList(), anyDouble(), anyDouble(), any());
    }

    @Test
    @DisplayName("WB-PROD-03: creatProduct validates duplicate name, duplicate SKU, price<=0, stock<0, valid save")
    void testCreateProductValidationBranches() {
        Product p = new Product();
        p.setName("RTX 4080");
        p.setSku("SKU-4080");
        p.setPrice(new BigDecimal("30000000"));
        p.setStock(5);

        when(productRepository.existsByNameIgnoreCase("RTX 4080")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> productService.creatProduct(p));

        when(productRepository.existsByNameIgnoreCase("RTX 4080")).thenReturn(false);
        when(productRepository.existsBySkuIgnoreCase("SKU-4080")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> productService.creatProduct(p));

        when(productRepository.existsBySkuIgnoreCase("SKU-4080")).thenReturn(false);
        p.setPrice(BigDecimal.ZERO);
        assertThrows(IllegalArgumentException.class, () -> productService.creatProduct(p));

        p.setPrice(new BigDecimal("30000000"));
        p.setStock(-1);
        assertThrows(IllegalArgumentException.class, () -> productService.creatProduct(p));

        p.setStock(5);
        when(productRepository.save(p)).thenReturn(p);
        assertSame(p, productService.creatProduct(p));
    }

    @Test
    @DisplayName("WB-CAT-01: CategoryService covers all 4 filterCategories branches and CRUD errors")
    void testCategoryAllBranches() {
        when(categoryRepository.findAll(any(Pageable.class))).thenReturn(Page.empty());
        when(categoryRepository.findByActive(eq(true), any(Pageable.class))).thenReturn(Page.empty());
        when(categoryRepository.findByNameContaining(eq("RTX"), any(Pageable.class))).thenReturn(Page.empty());
        when(categoryRepository.findByNameContainingIgnoreCaseAndActive(eq("RTX"), eq(false), any(Pageable.class))).thenReturn(Page.empty());

        categoryService.filterCategories(null, null, 0, 10, "name", "asc");
        categoryService.filterCategories("", true, 0, 10, "name", "desc");
        categoryService.filterCategories("RTX", null, 0, 10, "id", "asc");
        categoryService.filterCategories("RTX", false, 0, 10, "id", "desc");

        Category c = new Category();
        c.setId(1L);
        c.setName("RTX Series");
        c.setActive(true);
        when(categoryRepository.existsByNameIgnoreCase("RTX Series")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> categoryService.createCategory(c));

        when(categoryRepository.existsByIdAndDeleted(99L, false)).thenReturn(false);
        assertThrows(ResourceNotFoundException.class, () -> categoryService.deleteCategory(99L));
    }

    @Test
    @DisplayName("WB-BRAND-01: BrandService covers slug generation, filter branches, and CRUD validation")
    void testBrandAllBranches() {
        when(brandRepository.findAll(any(Pageable.class))).thenReturn(Page.empty());
        when(brandRepository.findByStatus(eq(true), any(Pageable.class))).thenReturn(Page.empty());
        when(brandRepository.findByNameContaining(eq("ASUS"), any(Pageable.class))).thenReturn(Page.empty());
        when(brandRepository.findByNameContainingIgnoreCaseAndStatus(eq("ASUS"), eq(true), any(Pageable.class))).thenReturn(Page.empty());

        brandService.filterBrands(null, null, 0, 10, "name", "asc");
        brandService.filterBrands(" ", true, 0, 10, "name", "desc");
        brandService.filterBrands("ASUS", null, 0, 10, "id", "asc");
        brandService.filterBrands("ASUS", true, 0, 10, "id", "desc");

        Brand b = new Brand("ASUS ROG!");
        when(brandRepository.existsByNameIgnoreCase("ASUS ROG!")).thenReturn(false);
        when(brandRepository.save(any(Brand.class))).thenAnswer(inv -> inv.getArgument(0));
        Brand saved = brandService.createBrand(b);
        assertEquals("asus-rog", saved.getSlug());

        when(brandRepository.existsByNameIgnoreCase("ASUS ROG!")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> brandService.createBrand(new Brand("ASUS ROG!")));

        when(brandRepository.findByIdAndDeleted(88L, false)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> brandService.getBrandId(88L));
    }
}
