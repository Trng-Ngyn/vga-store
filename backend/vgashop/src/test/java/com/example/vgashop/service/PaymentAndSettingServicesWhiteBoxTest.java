package com.example.vgashop.service;

import com.example.vgashop.dto.PaymentRequest;
import com.example.vgashop.dto.PaymentResponse;
import com.example.vgashop.entity.*;
import com.example.vgashop.exception.ResourceNotFoundException;
import com.example.vgashop.repository.OrderRepository;
import com.example.vgashop.repository.PaymentRepository;
import com.example.vgashop.repository.ProductRepository;
import com.example.vgashop.repository.SystemSettingRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.test.util.ReflectionTestUtils;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PaymentAndSettingServicesWhiteBoxTest {

    @Mock private PaymentRepository paymentRepository;
    @Mock private OrderRepository orderRepository;
    @Mock private UserService userService;
    @Mock private ProductRepository productRepository;
    @Mock private SystemSettingRepository systemSettingRepository;

    private PaymentService paymentService;
    private PaymentExpiryScheduler scheduler;
    private SystemSettingService settingService;
    private User user;
    private Order order;

    @BeforeEach
    void setUp() {
        paymentService = new PaymentService(paymentRepository, orderRepository, userService);
        ReflectionTestUtils.setField(paymentService, "vnpayTmnCode", "TESTTMN");
        ReflectionTestUtils.setField(paymentService, "vnpayHashSecret", "TEST_VNPAY_SECRET");
        ReflectionTestUtils.setField(paymentService, "vnpayUrl", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html");
        ReflectionTestUtils.setField(paymentService, "vnpayReturnUrl", "http://localhost:5173/payment/return");
        ReflectionTestUtils.setField(paymentService, "momoPartnerCode", "MOMO");
        ReflectionTestUtils.setField(paymentService, "momoAccessKey", "ACCESS");
        ReflectionTestUtils.setField(paymentService, "momoSecretKey", "SECRET");
        ReflectionTestUtils.setField(paymentService, "momoIpnUrl", "http://localhost:8080/ipn");
        ReflectionTestUtils.setField(paymentService, "momoReturnUrl", "http://localhost:5173/return");

        scheduler = new PaymentExpiryScheduler(orderRepository, paymentRepository, productRepository);
        settingService = new SystemSettingService(systemSettingRepository);

        user = new User();
        user.setId(1L);
        user.setUsername("buyer");

        order = new Order();
        order.setId(100L);
        order.setOrderCode("VGA-2026-100");
        order.setUser(user);
        order.setTotalAmount(new BigDecimal("15000000"));
        order.setStatus(OrderStatus.PENDING);
        order.setPaymentStatus(PaymentStatus.UNPAID);
    }

    @Test
    @DisplayName("WB-PAY-01: createPayment covers validation errors and COD, BANK_TRANSFER, VNPAY, MOMO")
    void testCreatePaymentAllMethodsAndGuards() {
        when(userService.getCurrentUser()).thenReturn(user);
        PaymentRequest req = new PaymentRequest();
        req.setPaymentMethod(PaymentMethod.COD);

        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(999L, 1L)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> paymentService.createPayment(999L, req, "127.0.0.1"));

        order.setStatus(OrderStatus.CANCELLED);
        when(orderRepository.findByIdAndUser_IdAndDeletedFalse(100L, 1L)).thenReturn(Optional.of(order));
        assertThrows(IllegalArgumentException.class, () -> paymentService.createPayment(100L, req, "127.0.0.1"));

        order.setStatus(OrderStatus.PENDING);
        Payment alreadyPaid = new Payment();
        alreadyPaid.setPaymentStatus(PaymentStatus.SUCCESS);
        when(paymentRepository.findByOrder_IdAndDeletedFalse(100L)).thenReturn(Optional.of(alreadyPaid));
        assertThrows(IllegalArgumentException.class, () -> paymentService.createPayment(100L, req, "127.0.0.1"));

        when(paymentRepository.findByOrder_IdAndDeletedFalse(100L)).thenReturn(Optional.empty());
        when(paymentRepository.save(any(Payment.class))).thenAnswer(inv -> {
            Payment p = inv.getArgument(0);
            p.setId(1L);
            return p;
        });

        for (PaymentMethod method : List.of(PaymentMethod.COD, PaymentMethod.BANK_TRANSFER, PaymentMethod.VNPAY, PaymentMethod.MOMO)) {
            req.setPaymentMethod(method);
            PaymentResponse resp = paymentService.createPayment(100L, req, "127.0.0.1");
            assertEquals(method, resp.getPaymentMethod());
            assertEquals(PaymentStatus.PENDING, resp.getPaymentStatus());
        }
    }

    @Test
    @DisplayName("WB-PAY-02: updatePaymentStatus and query methods cover SUCCESS/FAILED/lookups")
    void testUpdateStatusAndQueries() {
        Payment payment = new Payment();
        payment.setId(5L);
        payment.setOrder(order);
        payment.setPaymentMethod(PaymentMethod.BANK_TRANSFER);
        payment.setAmount(order.getTotalAmount());
        payment.setPaymentStatus(PaymentStatus.PENDING);

        when(paymentRepository.findById(5L)).thenReturn(Optional.of(payment));
        when(paymentRepository.save(any(Payment.class))).thenAnswer(inv -> inv.getArgument(0));

        PaymentResponse success = paymentService.updatePaymentStatus(5L, PaymentStatus.SUCCESS, "TXN-999");
        assertEquals(PaymentStatus.SUCCESS, success.getPaymentStatus());
        assertEquals(OrderStatus.CONFIRMED, order.getStatus());
        assertEquals("TXN-999", success.getTransactionCode());

        PaymentResponse failed = paymentService.updatePaymentStatus(5L, PaymentStatus.FAILED, "");
        assertEquals(PaymentStatus.FAILED, failed.getPaymentStatus());
        assertEquals(PaymentStatus.UNPAID, order.getPaymentStatus());

        when(userService.getCurrentUser()).thenReturn(user);
        when(paymentRepository.findByOrder_IdAndDeletedFalse(100L)).thenReturn(Optional.of(payment));
        assertEquals(5L, paymentService.getPaymentByOrderId(100L).getPaymentId());
        assertEquals(5L, paymentService.getPaymentById(5L).getPaymentId());

        Page<Payment> page = new PageImpl<>(List.of(payment));
        when(paymentRepository.findByOrder_User_IdAndDeletedFalse(eq(1L), any(Pageable.class))).thenReturn(page);
        when(paymentRepository.findByDeletedFalse(any(Pageable.class))).thenReturn(page);
        when(paymentRepository.findByPaymentStatusAndDeletedFalse(eq(PaymentStatus.PENDING), any(Pageable.class))).thenReturn(page);

        assertEquals(1, paymentService.getMyPayments(10, 0, "id", "asc").getTotalElements());
        assertEquals(1, paymentService.getAllPayments(10, 0, "id", "desc").getTotalElements());
        assertEquals(1, paymentService.getPaymentsByStatus(PaymentStatus.PENDING, 10, 0, "id", "asc").getTotalElements());
        assertEquals("TEST_VNPAY_SECRET", paymentService.getVnpayHashSecret());
        assertEquals("SECRET", paymentService.getMomoSecretKey());
    }

    @Test
    @DisplayName("WB-PAY-03: PaymentExpiryScheduler cancels expired BANK_TRANSFER and skips COD")
    void testExpirySchedulerBranches() {
        Product p = new Product();
        p.setId(9L);
        p.setStock(5);

        Order expiredTransfer = new Order();
        expiredTransfer.setId(1L);
        expiredTransfer.setStatus(OrderStatus.PENDING);
        OrderItem item = new OrderItem();
        item.setProduct(p);
        item.setQuantity(2);
        expiredTransfer.getItems().add(item);

        Payment bankPay = new Payment();
        bankPay.setPaymentMethod(PaymentMethod.BANK_TRANSFER);
        bankPay.setPaymentStatus(PaymentStatus.PENDING);

        Order codOrder = new Order();
        codOrder.setId(2L);
        Payment codPay = new Payment();
        codPay.setPaymentMethod(PaymentMethod.COD);

        when(orderRepository.findExpiredPendingOrders(any(LocalDateTime.class)))
                .thenReturn(List.of(expiredTransfer, codOrder));
        when(paymentRepository.findByOrder_IdAndDeletedFalse(1L)).thenReturn(Optional.of(bankPay));
        when(paymentRepository.findByOrder_IdAndDeletedFalse(2L)).thenReturn(Optional.of(codPay));

        scheduler.expireUnpaidBankTransferOrders();

        assertEquals(OrderStatus.CANCELLED, expiredTransfer.getStatus());
        assertEquals(PaymentStatus.FAILED, bankPay.getPaymentStatus());
        assertEquals(7, p.getStock());
        assertNotEquals(OrderStatus.CANCELLED, codOrder.getStatus());
    }

    @Test
    @DisplayName("WB-SET-01: SystemSettingService reads, falls back, and upserts settings")
    void testSystemSettingService() {
        SystemSetting existing = SystemSetting.builder()
                .settingKey("bank_name")
                .settingValue("MBBank")
                .description("Bank")
                .build();

        when(systemSettingRepository.findAll()).thenReturn(List.of(existing));
        assertEquals("MBBank", settingService.getAllSettings().get("bank_name"));

        when(systemSettingRepository.findBySettingKey("bank_name")).thenReturn(Optional.of(existing));
        when(systemSettingRepository.findBySettingKey("missing_key")).thenReturn(Optional.empty());
        assertEquals("MBBank", settingService.getSettingValue("bank_name", "DEFAULT"));
        assertEquals("DEFAULT", settingService.getSettingValue("missing_key", "DEFAULT"));

        settingService.updateSettings(Map.of("bank_name", "Vietcombank", "missing_key", "123"));
        verify(systemSettingRepository, times(2)).save(any(SystemSetting.class));
    }
}
