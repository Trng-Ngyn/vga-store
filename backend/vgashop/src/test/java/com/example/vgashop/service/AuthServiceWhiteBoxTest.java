package com.example.vgashop.service;

import com.example.vgashop.dto.AuthResponse;
import com.example.vgashop.dto.GoogleLoginRequest;
import com.example.vgashop.dto.RegisterRequest;
import com.example.vgashop.dto.UserDTO;
import com.example.vgashop.entity.Role;
import com.example.vgashop.entity.User;
import com.example.vgashop.exception.DuplicateResourceException;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.UserRepository;
import com.example.vgashop.security.JwtUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceWhiteBoxTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private JwtUtil jwtUtil;

    private AuthService authService;

    @BeforeEach
    void setUp() {
        authService = new AuthService(userRepository, jwtUtil);
    }

    @Test
    @DisplayName("WB-AUTH-01: register(RegisterRequest) throws when email already exists")
    void testRegisterDuplicateEmail() {
        RegisterRequest req = new RegisterRequest();
        req.setEmail("dup@vga.vn");
        when(userRepository.existsByEmail("dup@vga.vn")).thenReturn(true);

        assertThrows(DuplicateResourceException.class, () -> authService.register(req));
        verify(userRepository, never()).save(any());
    }

    @Test
    @DisplayName("WB-AUTH-02: register(RegisterRequest) throws when username already exists")
    void testRegisterDuplicateUsername() {
        RegisterRequest req = new RegisterRequest();
        req.setEmail("new@vga.vn");
        req.setUsername("existingUser");
        when(userRepository.existsByEmail("new@vga.vn")).thenReturn(false);
        when(userRepository.existsByUsername("existingUser")).thenReturn(true);

        assertThrows(DuplicateResourceException.class, () -> authService.register(req));
        verify(userRepository, never()).save(any());
    }

    @Test
    @DisplayName("WB-AUTH-03: register(RegisterRequest) succeeds and hashes password + issues JWT")
    void testRegisterSuccess() {
        RegisterRequest req = new RegisterRequest();
        req.setUsername("tester01");
        req.setEmail("tester01@vga.vn");
        req.setPassword("secret123");
        req.setFullName("Tester One");

        when(userRepository.existsByEmail("tester01@vga.vn")).thenReturn(false);
        when(userRepository.existsByUsername("tester01")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User u = inv.getArgument(0);
            u.setId(10L);
            return u;
        });
        when(jwtUtil.generateToken("tester01", Role.USER)).thenReturn("jwt-token-01");

        AuthResponse resp = authService.register(req);

        assertEquals("jwt-token-01", resp.getToken());
        assertEquals("tester01", resp.getUsername());
        assertEquals("USER", resp.getRole());
        assertEquals("Registration successful", resp.getMessage());
    }

    @Test
    @DisplayName("WB-AUTH-04: register(UserDTO) handles duplicate username, duplicate email, explicit and null role")
    void testRegisterUserDtoBranches() {
        UserDTO dto = new UserDTO();
        dto.setUsername("u1");
        dto.setEmail("u1@vga.vn");
        dto.setPassword("123456");

        when(userRepository.existsByUsername("u1")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> authService.register(dto));

        when(userRepository.existsByUsername("u1")).thenReturn(false);
        when(userRepository.existsByEmail("u1@vga.vn")).thenReturn(true);
        assertThrows(DuplicateResourceException.class, () -> authService.register(dto));

        when(userRepository.existsByEmail("u1@vga.vn")).thenReturn(false);
        dto.setRole("admin");
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User u = inv.getArgument(0);
            u.setId(20L);
            return u;
        });
        when(jwtUtil.generateToken(eq("u1"), any(Role.class))).thenReturn("jwt-admin");

        AuthResponse resp = authService.register(dto);
        assertEquals("ADMIN", resp.getRole());

        // Branch with role == null defaults to USER
        dto.setRole(null);
        AuthResponse respDefault = authService.register(dto);
        assertEquals("USER", respDefault.getRole());
    }

    @Test
    @DisplayName("WB-AUTH-05: login fails when user not found")
    void testLoginUserNotFound() {
        when(userRepository.findByUsername("missing")).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> authService.login("missing", "123456"));
    }

    @Test
    @DisplayName("WB-AUTH-06: login fails when user is soft-deleted")
    void testLoginUserDeleted() {
        User user = new User();
        user.setUsername("deletedUser");
        user.setDeleted(true);
        when(userRepository.findByUsername("deletedUser")).thenReturn(Optional.of(user));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> authService.login("deletedUser", "123456"));
        assertTrue(ex.getMessage().contains("removed"));
    }

    @Test
    @DisplayName("WB-AUTH-07: login fails when user status is disabled")
    void testLoginUserDisabled() {
        User user = new User();
        user.setUsername("lockedUser");
        user.setDeleted(false);
        user.setStatus(false);
        when(userRepository.findByUsername("lockedUser")).thenReturn(Optional.of(user));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> authService.login("lockedUser", "123456"));
        assertTrue(ex.getMessage().contains("disabled"));
    }

    @Test
    @DisplayName("WB-AUTH-08: login fails when password does not match BCrypt hash")
    void testLoginWrongPassword() {
        User user = new User();
        user.setUsername("validUser");
        user.setDeleted(false);
        user.setStatus(true);
        user.setPassword(new BCryptPasswordEncoder().encode("correctPass"));
        when(userRepository.findByUsername("validUser")).thenReturn(Optional.of(user));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> authService.login("validUser", "wrongPass"));
        assertTrue(ex.getMessage().contains("Invalid"));
    }

    @Test
    @DisplayName("WB-AUTH-09: login succeeds for valid active non-deleted user")
    void testLoginSuccess() {
        User user = new User();
        user.setId(5L);
        user.setUsername("activeUser");
        user.setEmail("active@vga.vn");
        user.setRole(Role.USER);
        user.setDeleted(false);
        user.setStatus(true);
        user.setPassword(new BCryptPasswordEncoder().encode("pass123"));

        when(userRepository.findByUsername("activeUser")).thenReturn(Optional.of(user));
        when(jwtUtil.generateToken("activeUser", Role.USER)).thenReturn("token-ok");

        AuthResponse resp = authService.login("activeUser", "pass123");
        assertEquals("token-ok", resp.getToken());
        assertEquals("Login successful", resp.getMessage());
    }

    @Test
    @DisplayName("WB-AUTH-10: googleLogin resolves username collision loop for new user")
    void testGoogleLoginNewUserWithUsernameCollision() {
        GoogleLoginRequest req = new GoogleLoginRequest();
        req.setEmail("hieu@ut.edu.vn");
        req.setName("Lê Minh Hiếu");

        when(userRepository.findByEmail("hieu@ut.edu.vn")).thenReturn(Optional.empty());
        when(userRepository.existsByUsername("hieu")).thenReturn(true);
        when(userRepository.existsByUsername("hieu1")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User u = inv.getArgument(0);
            u.setId(30L);
            return u;
        });
        when(jwtUtil.generateToken("hieu1", Role.USER)).thenReturn("google-jwt");

        AuthResponse resp = authService.googleLogin(req);
        assertEquals("hieu1", resp.getUsername());
        assertEquals("google-jwt", resp.getToken());
    }

    @Test
    @DisplayName("WB-AUTH-11: googleLogin throws when existing user is disabled, succeeds when active")
    void testGoogleLoginExistingUserBranches() {
        GoogleLoginRequest req = new GoogleLoginRequest();
        req.setEmail("member@ut.edu.vn");
        req.setName("Member");

        User existing = new User();
        existing.setId(9L);
        existing.setUsername("member");
        existing.setEmail("member@ut.edu.vn");
        existing.setRole(Role.USER);
        existing.setStatus(false);

        when(userRepository.findByEmail("member@ut.edu.vn")).thenReturn(Optional.of(existing));
        assertThrows(RuntimeException.class, () -> authService.googleLogin(req));

        existing.setStatus(true);
        when(jwtUtil.generateToken("member", Role.USER)).thenReturn("existing-google-jwt");
        AuthResponse ok = authService.googleLogin(req);
        assertEquals("existing-google-jwt", ok.getToken());
    }
}
