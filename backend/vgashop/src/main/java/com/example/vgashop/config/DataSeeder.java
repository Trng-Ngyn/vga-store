package com.example.vgashop.config;

import com.example.vgashop.entity.*;
import com.example.vgashop.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.math.BigDecimal;
import java.util.Date;

@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner initDatabase(
            ProductRepository productRepository,
            CategoryRepository categoryRepository,
            BrandRepository brandRepository,
            BlogRepository blogRepository,
            ReviewRepository reviewRepository,
            ServicePolicyRepository servicePolicyRepository,
            SystemSettingRepository systemSettingRepository,
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JdbcTemplate jdbcTemplate) {

        return args -> {

            // Seed Admin User if not exists
            if (userRepository.count() == 0) {
                User admin = new User();
                admin.setUsername("admin");
                admin.setEmail("admin@vgastore.com");
                admin.setPassword(passwordEncoder.encode("123"));
                admin.setFullName("System Admin");
                admin.setRole(Role.ADMIN);
                admin.setStatus(true);
                userRepository.save(admin);
                System.out.println(">>> [SEEDER] Created default Admin account: admin / 123");
            }

            // Error handling
            try {
                jdbcTemplate.execute("ALTER TABLE reviews ALTER COLUMN user_id DROP NOT NULL");
            } catch (Exception e) {
                System.out.println("Cột user_id trong reviews đã cho phép Null hoặc CSDL không hỗ trợ lệnh này.");
            }

            // Seed Settings
            if (systemSettingRepository.count() == 0) {
                systemSettingRepository.save(SystemSetting.builder().settingKey("BANK_ID").settingValue("970436").description("Mã BIN Ngân hàng (Vietcombank)").build());
                systemSettingRepository.save(SystemSetting.builder().settingKey("BANK_ACC_NO").settingValue("1234567890").description("Số tài khoản").build());
                systemSettingRepository.save(SystemSetting.builder().settingKey("BANK_ACC_NAME").settingValue("CONG TY VGA STORE").description("Tên chủ tài khoản").build());
            }

            // Seed Brands
            Brand asus = null;
            Brand gigabyte = null;
            if (brandRepository.count() == 0) {
                asus = new Brand();
                asus.setName("ASUS");
                asus.setSlug("asus");
                asus.setStatus(true);
                asus = brandRepository.save(asus);

                gigabyte = new Brand();
                gigabyte.setName("GIGABYTE");
                gigabyte.setSlug("gigabyte");
                gigabyte.setStatus(true);
                gigabyte = brandRepository.save(gigabyte);
            } else {
                asus = brandRepository.findAll().get(0);
                gigabyte = brandRepository.findAll().size() > 1 ? brandRepository.findAll().get(1) : asus;
            }

            // Seed Categories
            Category rtx40 = null;
            Category rtx30 = null;
            if (categoryRepository.count() == 0) {
                rtx40 = new Category();
                rtx40.setName("NVIDIA RTX 40 Series");
                rtx40.setDescription("Dòng card đồ họa kiến trúc Ada Lovelace");
                rtx40.setActive(true);
                rtx40 = categoryRepository.save(rtx40);

                rtx30 = new Category();
                rtx30.setName("NVIDIA RTX 30 Series");
                rtx30.setDescription("Dòng card đồ họa kiến trúc Ampere");
                rtx30.setActive(true);
                rtx30 = categoryRepository.save(rtx30);
            } else {
                rtx40 = categoryRepository.findAll().get(0);
                rtx30 = categoryRepository.findAll().size() > 1 ? categoryRepository.findAll().get(1) : rtx40;
            }

            // Seed Products
            if (productRepository.count() == 0) {
                Product p1 = new Product();
                p1.setName("ASUS TUF Gaming GeForce RTX 4090 24GB GDDR6X OC Edition");
                p1.setPrice(new BigDecimal("55990000"));
                p1.setOldPrice(new BigDecimal("62000000"));
                p1.setStock(15);
                p1.setSku("TUF-RTX4090-O24G-GAMING");
                p1.setDescription("Card màn hình cao cấp ASUS TUF RTX 4090 mang lại hiệu năng đỉnh cao cho game thủ và nhà sáng tạo.");
                p1.setImgUrl("/images/products/asus/asus_tuf_gaming_geforce_rtx_4090_24gb_gddr6x_oc_edit_051.jpg");
                p1.setGpuModel("GeForce RTX 4090");
                p1.setVram("24GB GDDR6X");
                p1.setStatus(true);
                p1.setBrand(asus);
                p1.setCategory(rtx40);
                productRepository.save(p1);

                Product p2 = new Product();
                p2.setName("GIGABYTE AORUS GeForce RTX 4080 SUPER XTREME ICE 16GB");
                p2.setPrice(new BigDecimal("35990000"));
                p2.setOldPrice(new BigDecimal("38900000"));
                p2.setStock(10);
                p2.setSku("GV-N408SAORUSX-ICE-16GD");
                p2.setDescription("Thiết kế màu trắng tinh tế phiên bản băng tuyết với hệ thống tản nhiệt Windforce cực mát.");
                p2.setImgUrl("/images/products/gigabyte/gigabyte_aorus_geforce_rtx_4080_super_xtreme_ice_16g_018.jpg");
                p2.setGpuModel("GeForce RTX 4080 SUPER");
                p2.setVram("16GB GDDR6X");
                p2.setStatus(true);
                p2.setBrand(gigabyte);
                p2.setCategory(rtx40);
                productRepository.save(p2);

                Product p3 = new Product();
                p3.setName("ASUS ProArt GeForce RTX 4070 Ti SUPER 16GB GDDR6X OC");
                p3.setPrice(new BigDecimal("26990000"));
                p3.setOldPrice(new BigDecimal("29000000"));
                p3.setStock(20);
                p3.setSku("PROART-RTX4070TIS-O16G");
                p3.setDescription("Dòng card chuyên biệt cho đồ họa, dựng phim 4K và kiến trúc sư với độ ổn định tuyệt đối.");
                p3.setImgUrl("/images/products/asus/asus_proart_geforce_rtx_4070_ti_super_16gb_gddr6x_oc_052.jpg");
                p3.setGpuModel("GeForce RTX 4070 Ti SUPER");
                p3.setVram("16GB GDDR6X");
                p3.setStatus(true);
                p3.setBrand(asus);
                p3.setCategory(rtx40);
                productRepository.save(p3);

                Product p4 = new Product();
                p4.setName("GIGABYTE GeForce RTX 4070 SUPER WINDFORCE OC 12GB");
                p4.setPrice(new BigDecimal("18500000"));
                p4.setOldPrice(new BigDecimal("20500000"));
                p4.setStock(25);
                p4.setSku("GV-N407SWF3OC-12GD");
                p4.setDescription("Hiệu năng vượt trội trong tầm giá, cân mượt mà mọi tựa game AAA ở độ phân giải 2K.");
                p4.setImgUrl("/images/products/gigabyte/gigabyte_geforce_rtx_4070_super_windforce_oc_12g_013.jpg");
                p4.setGpuModel("GeForce RTX 4070 SUPER");
                p4.setVram("12GB GDDR6X");
                p4.setStatus(true);
                p4.setBrand(gigabyte);
                p4.setCategory(rtx40);
                productRepository.save(p4);

                Product p5 = new Product();
                p5.setName("ASUS Dual GeForce RTX 4060 V2 OC Edition 8GB GDDR6");
                p5.setPrice(new BigDecimal("8990000"));
                p5.setOldPrice(new BigDecimal("9900000"));
                p5.setStock(30);
                p5.setSku("DUAL-RTX4060-O8G-V2");
                p5.setDescription("Card đồ họa phổ biến nhất cho dàn PC gaming tầm trung, tiết kiệm điện năng tối đa.");
                p5.setImgUrl("/images/products/asus/asus_dual_rtx4060_v2.png");
                p5.setGpuModel("GeForce RTX 4060");
                p5.setVram("8GB GDDR6");
                p5.setStatus(true);
                p5.setBrand(asus);
                p5.setCategory(rtx40);
                productRepository.save(p5);

                Product p6 = new Product();
                p6.setName("GIGABYTE GeForce RTX 3060 WINDFORCE OC 12GB V2");
                p6.setPrice(new BigDecimal("7490000"));
                p6.setOldPrice(new BigDecimal("8200000"));
                p6.setStock(18);
                p6.setSku("GV-N3060WF2OC-12GD-V2");
                p6.setDescription("Chiến binh quốc dân với 12GB VRAM thoải mái làm đồ họa và chơi game Esports.");
                p6.setImgUrl("/images/products/gigabyte/gigabyte_geforce_rtx_3060_windforce_oc_12g_v2_014.jpg");
                p6.setGpuModel("GeForce RTX 3060");
                p6.setVram("12GB GDDR6");
                p6.setStatus(true);
                p6.setBrand(gigabyte);
                p6.setCategory(rtx30);
                productRepository.save(p6);

                System.out.println(">>> [SEEDER] Created sample VGA products, categories, and brands successfully!");
            }



            if (blogRepository.count() == 0) {
                Blog b1 = new Blog();
                b1.setTitle("Lo Dien Dong Card AMD Radeon RX 8000 Series Sap Ra Mat");
                b1.setExcerpt("Theo thong tin ro ri, dong GPU RDNA 4 cua AMD se tap trung vao phan khuc tam trung, mang lai hieu nang vuot troi voi muc gia hop ly.");
                b1.setThumbnail("/images/blog/amd-rx8000.jpg");
                b1.setCategory("Tin cong nghe");
                b1.setAuthor("Admin");
                b1.setViews(120);
                b1.setFeatured(true);
                b1.setPublishedDate(new Date());
                b1.setContent("[" +
                    "{\"type\":\"Heading\",\"body\":\"AMD Sap Ra Mat RDNA 4\"}," +
                    "{\"type\":\"Paragraph\",\"body\":\"AMD da chinh thuc xac nhan se ra mat dong Radeon RX 8000 series moi vao cuoi nam nay. Day la the he GPU thu 4 cua AMD duoc xay dung tren kien truc RDNA 4 hoan toan moi.\"}," +
                    "{\"type\":\"Heading\",\"body\":\"Hieu Nang Du Doan\"}," +
                    "{\"type\":\"Paragraph\",\"body\":\"Theo cac bai ro ri, RX 8000 series se mang lai hieu nang tang 40-60% so voi the he RX 7000 trong khi giu nguyen muc gia hoac tham chi re hon.\"}," +
                    "{\"type\":\"tip\",\"body\":\"Neu ban dang dinh mua card do hoa moi, hay cho them vai thang de xem xet chon RX 8000 se mang lai gia tri tot hon.\"}," +
                    "{\"type\":\"Heading\",\"body\":\"Thoi Gian Ra Mat Du Kien\"}," +
                    "{\"type\":\"Paragraph\",\"body\":\"AMD du kien se chinh thuc gioi thieu dong RX 8000 tai su kien Computex 2025, voi gia ban du kien tu 8 trieu VND cho mau cap trung.\"}" +
                    "]");
                blogRepository.save(b1);

                Blog b2 = new Blog();
                b2.setTitle("Huong Dan Ve Sinh Card Do Hoa An Toan Tai Nha");
                b2.setExcerpt("Ve sinh VGA dinh ky giup tang tuoi tho va giam nhiet do hoat dong, duy tri hieu nang on dinh cho card do hoa cua ban.");
                b2.setThumbnail("/images/blog/vesinh.jpg");
                b2.setCategory("Huong dan");
                b2.setAuthor("Ky thuat vien");
                b2.setViews(250);
                b2.setFeatured(false);
                b2.setPublishedDate(new Date());
                b2.setContent("[" +
                    "{\"type\":\"Heading\",\"body\":\"Dung Cu Can Chuan Bi\"}," +
                    "{\"type\":\"Paragraph\",\"body\":\"Truoc khi ve sinh card do hoa, ban can chuan bi: binh khi nen, co mem, kem tan nhiet, tua vit 4 chau, khan sach.\"}," +
                    "{\"type\":\"Heading\",\"body\":\"Cac Buoc Ve Sinh Chi Tiet\"}," +
                    "{\"type\":\"steps\",\"items\":[" +
                    "{\"step\":1,\"title\":\"Thao Card khoi may tinh\",\"desc\":\"Tat nguon, rut het day, dung tua vit mo nap thung va nhe nhang thao card ra.\"}," +
                    "{\"step\":2,\"title\":\"Xit khi nen vao canh quat\",\"desc\":\"Giu canh quat co dinh bang tay, xit khi nen manh de thoi bay bui ban.\"}," +
                    "{\"step\":3,\"title\":\"Lap kem tan nhiet moi\",\"desc\":\"Dung co sach lau sach kem cu, boi kem tan nhiet moi len chip GPU.\"}," +
                    "{\"step\":4,\"title\":\"Lap lai va kiem tra\",\"desc\":\"Lap card tro lai may, bat may va kiem tra nhiet do xem co giam khong.\"}" +
                    "]}," +
                    "{\"type\":\"tip\",\"body\":\"Nen ve sinh card do hoa moi 6 thang 1 lan, dac biet neu ban song o moi truong nhieu bui.\"}" +
                    "]");
                blogRepository.save(b2);

                Blog b3 = new Blog();
                b3.setTitle("So Sanh RTX 4070 Super vs RX 7800 XT: Chon Card Nao Cho Game Thu Viet?");
                b3.setExcerpt("RTX 4070 Super va RX 7800 XT la 2 lua chon hang dau trong tam gia 15-18 trieu. Xem so sanh de biet chon card nao phu hop.");
                b3.setThumbnail("/images/blog/compare.jpg");
                b3.setCategory("Danh gia");
                b3.setAuthor("Gaming Expert");
                b3.setViews(480);
                b3.setFeatured(true);
                b3.setPublishedDate(new Date());
                b3.setContent("[" +
                    "{\"type\":\"Heading\",\"body\":\"Tong Quan Hai Doi Thu\"}," +
                    "{\"type\":\"Paragraph\",\"body\":\"RTX 4070 Super co muc gia 16.5 trieu, trong khi RX 7800 XT duoc ban quanh muc 15.9 trieu. Ca hai deu la lua chon chat luong o phan khuc tam cao.\"}," +
                    "{\"type\":\"Heading\",\"body\":\"Ket Luan\"}," +
                    "{\"type\":\"Paragraph\",\"body\":\"Neu uu tien DLSS 4 va ray tracing, chon RTX 4070 Super. Neu uu tien do phan giai RAM ve gia tri, chon RX 7800 XT.\"}" +
                    "]");
                blogRepository.save(b3);
            }

        };
    }
}
