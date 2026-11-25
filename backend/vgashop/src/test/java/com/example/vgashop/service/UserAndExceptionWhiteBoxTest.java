package com.example.vgashop.service;

import com.example.vgashop.dto.ChangePasswordRequest;
import com.example.vgashop.dto.UserAddressDto;
import com.example.vgashop.dto.UserDTO;
import com.example.vgashop.dto.UserProfileRequest;
import com.example.vgashop.dto.UserProfileResponse;
import com.example.vgashop.entity.Role;
import com.example.vgashop.entity.User;
import com.example.vgashop.entity.UserAddress;
import com.example.vgashop.exception.DuplicateResourceException;
import com.example.vgashop.exception.GlobalExceptionHandler;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.ApiResponse;
import com.example.vgashop.repository.UserRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.core.MethodParameter;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserAndExceptionWhiteBoxTest {

    @Mock private UserRepository userRepository;
    private UserService userService;
    private User user;

    @BeforeEach
    void setUp() {
        userService = new UserService(userRepository);
        user = new User();
        user.setId(1L);
        user.setUsername("trongtd");
        user.setEmail("trongtd@vga.vn");
        user.setPassword(new BCryptPasswordEncoder().encode("oldPass123"));
        user.setRole(Role.USER);
        user.setAddresses(new java.util.ArrayList<>());
    }

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    @DisplayName("WB-USR-01: profile, changePassword, addAddress and deleteAddress branches")
    void testUserProfileAndAddresses() {
        when(userRepository.findByUsername("trongtd")).thenReturn(Optional.of(user));
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User saved = inv.getArgument(0);
            long addrSeq = 100L;
            if (saved.getAddresses() != null) {
                for (UserAddress a : saved.getAddresses()) {
                    if (a.getId() == null) a.setId(addrSeq++);
                }
            }
            return saved;
        });

        UserProfileResponse profile = userService.getUserProfile("trongtd");
        assertEquals("trongtd", profile.getUsername());

        UserProfileRequest updateReq = new UserProfileRequest("trongtd", "0908123456", "Nam", LocalDate.of(2004, 1, 1));
        assertEquals("0908123456", userService.updateProfile("trongtd", updateReq).getPhone());

        assertThrows(RuntimeException.class,
                () -> userService.changePassword("trongtd", new ChangePasswordRequest("wrong", "new12345")));
        userService.changePassword("trongtd", new ChangePasswordRequest("oldPass123", "new12345"));

        UserAddressDto addrDto = new UserAddressDto(null, "Trong", "0908123456", "Q1 HCM", true);
        UserProfileResponse withAddr = userService.addAddress("trongtd", addrDto);
        assertEquals(1, withAddr.getAddresses().size());
        assertTrue(withAddr.getAddresses().get(0).getIsDefault());

        UserAddress existingAddr = user.getAddresses().get(0);
        existingAddr.setId(77L);
        UserAddressDto secondAddr = new UserAddressDto(null, "Trong 2", "0909111222", "Thu Duc", false);
        assertEquals(2, userService.addAddress("trongtd", secondAddr).getAddresses().size());

        assertEquals(1, userService.deleteAddress("trongtd", 77L).getAddresses().size());
    }

    @Test
    @DisplayName("WB-USR-02: search, getCurrentUser, createUser, updateUser, deleteUser branches")
    void testUserCrudAndSecurityContext() {
        when(userRepository.findByDeletedFalse(any(Pageable.class))).thenReturn(new PageImpl<>(List.of(user)));
        when(userRepository.findByUsernameContainingIgnoreCaseOrEmailContainingIgnoreCase(eq("trong"), eq("trong"), any()))
                .thenReturn(new PageImpl<>(List.of(user)));

        assertEquals(1, userService.getAllUsers(0, 10, "id", "asc").getTotalElements());
        assertEquals(1, userService.getAllUsers(0, 10, "id", "desc").getTotalElements());
        assertEquals(1, userService.searchUsers("", 0, 10).getTotalElements());
        assertEquals(1, userService.searchUsers("trong", 0, 10).getTotalElements());

        when(userRepository.findByIdAndDeleted(999L, false)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> userService.getUserById(999L));

        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken("trongtd", null, List.of()));
        when(userRepository.findByUsernameAndDeletedFalse("trongtd")).thenReturn(Optional.of(user));
        assertEquals("trongtd", userService.getCurrentUser().getUsername());

        UserDTO dto = new UserDTO();
        dto.setUsername("u_new");
        dto.setEmail("u_new@vga.vn");
        dto.setPassword("123456");

        when(userRepository.existsByUsername("u_new")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> userService.createUser(dto));

        when(userRepository.existsByUsername("u_new")).thenReturn(false);
        when(userRepository.existsByEmail("u_new@vga.vn")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> userService.createUser(dto));

        when(userRepository.existsByEmail("u_new@vga.vn")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User saved = inv.getArgument(0);
            long addrSeq = 100L;
            if (saved.getAddresses() != null) {
                for (UserAddress a : saved.getAddresses()) {
                    if (a.getId() == null) a.setId(addrSeq++);
                }
            }
            return saved;
        });
        assertEquals(Role.USER, userService.createUser(dto).getRole());

        when(userRepository.findByIdAndDeleted(1L, false)).thenReturn(Optional.of(user));
        when(userRepository.existsByUsername("u_new")).thenReturn(false);
        when(userRepository.existsByEmail("u_new@vga.vn")).thenReturn(false);
        dto.setRole("ADMIN");
        assertEquals(Role.ADMIN, userService.updateUser(1L, dto).getRole());

        when(userRepository.existsByIdAndDeleted(1L, false)).thenReturn(true);
        userService.deleteUser(1L);
        assertTrue(user.isDeleted());
    }

    @Test
    @DisplayName("WB-EXC-01: GlobalExceptionHandler maps all exception types to expected HTTP status codes")
    void testGlobalExceptionHandlerAllHandlers() throws NoSuchMethodException {
        GlobalExceptionHandler handler = new GlobalExceptionHandler();

        assertEquals(HttpStatus.NOT_FOUND, handler.handleNotFound(new ResourceNotFoundException("Not found")).getStatusCode());
        assertEquals(HttpStatus.CONFLICT, handler.handleDuplicateResource(new DuplicateResourceException("Dup")).getStatusCode());
        assertEquals(HttpStatus.BAD_REQUEST, handler.handleIllegalState(new IllegalStateException("Bad state")).getStatusCode());
        assertEquals(HttpStatus.BAD_REQUEST, handler.handleIllegalArgument(new IllegalArgumentException("Bad arg")).getStatusCode());

        DataIntegrityViolationException dive = new DataIntegrityViolationException("FK error", new RuntimeException("Constraint"));
        assertEquals(HttpStatus.CONFLICT, handler.handleDataIntegrity(dive).getStatusCode());

        ResponseEntity<ApiResponse<Object>> gen = handler.handleGeneral(new RuntimeException("Crash"));
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, gen.getStatusCode());

        BeanPropertyBindingResult br = new BeanPropertyBindingResult(new Object(), "req");
        br.addError(new FieldError("req", "phone", "Invalid phone"));
        MethodParameter mp = new MethodParameter(Object.class.getMethod("toString"), -1);
        MethodArgumentNotValidException manve = new MethodArgumentNotValidException(mp, br);
        assertEquals(HttpStatus.BAD_REQUEST, handler.handleValidation(manve).getStatusCode());
    }
}
