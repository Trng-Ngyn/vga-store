package com.example.vgashop.security;

import com.example.vgashop.entity.Role;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class JwtUtilWhiteBoxTest {

    private static final String SECRET = "VGAStore2026SuperSecretKeyForWhiteBoxTestingMustBeAtLeast256Bits!";
    private JwtUtil jwtUtil;

    @BeforeEach
    void setUp() {
        jwtUtil = new JwtUtil(SECRET, 3600000L);
    }

    @Test
    @DisplayName("WB-JWT-01: Generate and extract claims using Role enum")
    void testGenerateTokenWithRoleEnum() {
        String token = jwtUtil.generateToken("trongtd", Role.ADMIN);

        assertNotNull(token);
        assertEquals("trongtd", jwtUtil.extractUsername(token));
        assertEquals("ADMIN", jwtUtil.extractRole(token));
        assertTrue(jwtUtil.validateToken(token));
    }

    @Test
    @DisplayName("WB-JWT-02: Generate and extract claims using String role")
    void testGenerateTokenWithStringRole() {
        String token = jwtUtil.generateToken("khachhang1", "USER");

        assertNotNull(token);
        assertEquals("khachhang1", jwtUtil.extractUsername(token));
        assertEquals("USER", jwtUtil.extractRole(token));
        assertTrue(jwtUtil.validateToken(token));
    }

    @Test
    @DisplayName("WB-JWT-03: validateToken returns false for malformed token")
    void testValidateMalformedToken() {
        assertFalse(jwtUtil.validateToken("not.a.valid.jwt.token"));
    }

    @Test
    @DisplayName("WB-JWT-04: validateToken returns false for null or blank token")
    void testValidateEmptyOrNullToken() {
        assertFalse(jwtUtil.validateToken(null));
        assertFalse(jwtUtil.validateToken(""));
        assertFalse(jwtUtil.validateToken("   "));
    }

    @Test
    @DisplayName("WB-JWT-05: validateToken returns false when token signature is tampered")
    void testValidateTamperedToken() {
        String token = jwtUtil.generateToken("user1", Role.USER);
        String tampered = token.substring(0, token.length() - 4) + "abcd";
        assertFalse(jwtUtil.validateToken(tampered));
    }

    @Test
    @DisplayName("WB-JWT-06: validateToken returns false when token is expired")
    void testValidateExpiredToken() {
        JwtUtil expiredUtil = new JwtUtil(SECRET, -1000L);
        String expiredToken = expiredUtil.generateToken("user1", Role.USER);
        assertFalse(jwtUtil.validateToken(expiredToken));
    }

    @Test
    @DisplayName("WB-JWT-07: validateToken returns false for token signed with different secret")
    void testValidateDifferentSecretToken() {
        JwtUtil otherUtil = new JwtUtil("AnotherCompletelyDifferentSecretKeyWithEnoughLengthForHMAC256!", 3600000L);
        String otherToken = otherUtil.generateToken("hacker", Role.ADMIN);
        assertFalse(jwtUtil.validateToken(otherToken));
    }
}
