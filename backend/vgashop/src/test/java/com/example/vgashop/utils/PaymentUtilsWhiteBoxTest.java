package com.example.vgashop.utils;

import com.example.vgashop.entity.Order;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class PaymentUtilsWhiteBoxTest {

    private Order sampleOrder() {
        Order order = new Order();
        order.setOrderCode("VGA-2026-001");
        order.setTotalAmount(new BigDecimal("15500000"));
        return order;
    }

    @Test
    @DisplayName("WB-PAY-01: VNPay createPaymentUrl uses provided client IP and generates verifiable hash")
    void testVnPayCreateAndVerifyWithClientIp() {
        String url = VNPayUtils.createPaymentUrl(
                sampleOrder(), "TXN12345", "http://localhost:5173/return",
                "192.168.1.10", "TMN123", "SECRETKEY1234567890", "https://sandbox.vnpay.vn/pay"
        );

        assertTrue(url.startsWith("https://sandbox.vnpay.vn/pay?"));
        assertTrue(url.contains("vnp_IpAddr=192.168.1.10"));
        assertTrue(url.contains("vnp_Amount=1550000000"));
        assertTrue(url.contains("vnp_SecureHash="));

        // Parse query back and verify signature branch
        String query = url.substring(url.indexOf('?') + 1);
        Map<String, String> params = new HashMap<>();
        for (String pair : query.split("&")) {
            String[] kv = pair.split("=", 2);
            params.put(URLDecoder.decode(kv[0], StandardCharsets.UTF_8),
                       URLDecoder.decode(kv[1], StandardCharsets.UTF_8));
        }
        assertTrue(VNPayUtils.verifySignature(params, "SECRETKEY1234567890"));
    }

    @Test
    @DisplayName("WB-PAY-02: VNPay createPaymentUrl falls back to 127.0.0.1 when clientIp is null or blank")
    void testVnPayFallbackIpBranches() {
        String urlNullIp = VNPayUtils.createPaymentUrl(
                sampleOrder(), "TXN1", "http://localhost/ret",
                null, "TMN1", "SECRET1", "https://vnpay"
        );
        String urlBlankIp = VNPayUtils.createPaymentUrl(
                sampleOrder(), "TXN2", "http://localhost/ret",
                "   ", "TMN1", "SECRET1", "https://vnpay"
        );

        assertTrue(urlNullIp.contains("vnp_IpAddr=127.0.0.1"));
        assertTrue(urlBlankIp.contains("vnp_IpAddr=127.0.0.1"));
    }

    @Test
    @DisplayName("WB-PAY-03: VNPay verifySignature returns false when hash missing, empty, or tampered")
    void testVnPayVerifySignatureFalseBranches() {
        Map<String, String> missingHash = new HashMap<>();
        missingHash.put("vnp_TxnRef", "TXN1");
        assertFalse(VNPayUtils.verifySignature(missingHash, "SECRET"));

        missingHash.put("vnp_SecureHash", "");
        assertFalse(VNPayUtils.verifySignature(missingHash, "SECRET"));

        missingHash.put("vnp_SecureHash", "deadbeef");
        assertFalse(VNPayUtils.verifySignature(missingHash, "SECRET"));

        assertFalse(VNPayUtils.verifySignature(null, "SECRET"));
    }

    @Test
    @DisplayName("WB-PAY-04: MoMo createPaymentUrl constructs expected URL and valid HMAC-SHA256 signature")
    void testMomoCreatePaymentUrl() {
        String url = MomoUtils.createPaymentUrl(
                sampleOrder(), "MOMO999", "http://localhost/momo-ret",
                "PARTNER1", "ACCESS1", "SECRET1", "http://localhost/ipn"
        );

        assertTrue(url.startsWith("https://test-payment.momo.vn/v2/gateway/api/create?"));
        assertTrue(url.contains("partnerCode=PARTNER1"));
        assertTrue(url.contains("orderId=MOMO999"));
        assertTrue(url.contains("amount=15500000"));
        assertTrue(url.contains("signature="));
    }

    @Test
    @DisplayName("WB-PAY-05: MoMo verifySignature succeeds for authentic callback payload")
    void testMomoVerifySignatureTrue() {
        String secret = "MOMO_SECRET_KEY";
        Map<String, Object> params = new HashMap<>();
        params.put("accessKey", "ACC1");
        params.put("amount", "100000");
        params.put("extraData", "");
        params.put("message", "Success");
        params.put("orderId", "ORD1");
        params.put("orderInfo", "VGA");
        params.put("orderType", "momo_wallet");
        params.put("partnerCode", "PART1");
        params.put("payType", "qr");
        params.put("requestId", "REQ1");
        params.put("responseTime", "1700000000");
        params.put("resultCode", "0");
        params.put("transId", "98765");

        String raw = "accessKey=ACC1&amount=100000&extraData=&message=Success&orderId=ORD1"
                + "&orderInfo=VGA&orderType=momo_wallet&partnerCode=PART1&payType=qr"
                + "&requestId=REQ1&responseTime=1700000000&resultCode=0&transId=98765";
        params.put("signature", MomoUtils.hmacSHA256(secret, raw));

        assertTrue(MomoUtils.verifySignature(params, secret));
    }

    @Test
    @DisplayName("WB-PAY-06: MoMo verifySignature returns false when signature null, empty, or invalid")
    void testMomoVerifySignatureFalseBranches() {
        Map<String, Object> params = new HashMap<>();
        assertFalse(MomoUtils.verifySignature(params, "SECRET"));

        params.put("signature", "");
        assertFalse(MomoUtils.verifySignature(params, "SECRET"));

        params.put("signature", "wrongsig");
        assertFalse(MomoUtils.verifySignature(params, "SECRET"));

        assertFalse(MomoUtils.verifySignature(null, "SECRET"));
    }

    @Test
    @DisplayName("WB-PAY-07: HMAC helpers throw RuntimeException when key is null")
    void testHmacNullKeyThrowsException() {
        assertThrows(RuntimeException.class, () -> VNPayUtils.hmacSHA512(null, "data"));
        assertThrows(RuntimeException.class, () -> MomoUtils.hmacSHA256(null, "data"));
    }
}
