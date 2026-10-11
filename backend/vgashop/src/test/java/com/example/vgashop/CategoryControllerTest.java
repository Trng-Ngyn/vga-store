package com.example.vgashop;

import com.example.vgashop.entity.Category;
import com.example.vgashop.service.CategoryService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class CategoryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CategoryService categoryService;

    @Test
    @DisplayName("Unit Test: Lấy danh sách danh mục thành công trả về HTTP 200")
    void testGetAllCategories() throws Exception {
        Category cat = new Category();
        cat.setId(1L);
        cat.setName("Card Đồ Họa Gaming");
        cat.setActive(true);

        Mockito.when(categoryService.getAllCategories(Mockito.any(PageRequest.class)))
                .thenReturn(new PageImpl<>(List.of(cat)));

        mockMvc.perform(get("/api/categories")
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.message").value("Lấy danh sách danh mục thành công!"));
    }
}
