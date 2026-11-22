## 1. Tổng quan & Mục tiêu

### 1.1. Bối cảnh & Vấn đề

Trong quá trình phát triển và vận hành các ứng dụng nội bộ tiêu thụ nhiều dịch vụ API (API nội bộ, API đối tác bên thứ ba, hoặc các dịch vụ chuyên biệt như Thanh toán, Xác thực, AI...), tổ chức đối mặt với hai nhóm rủi ro cốt lõi:

- **Rủi ro lạm dụng API & Định danh máy móc:** API Key tĩnh dễ bị sao chép, rò rỉ hoặc dùng chéo giữa các thiết bị/ứng dụng (Token Replay/Theft), đồng thời thiếu cơ chế cô lập phạm vi truy cập dịch vụ và kiểm soát lưu lượng/chi phí giữa các dự án.
- **Rủi ro quản lý bí mật cho lập trình viên:** Việc phân phối file `.env` thủ công qua chat, email hoặc lưu trữ dạng văn bản thuần (plaintext) trên máy cá nhân gây lộ lọt thông tin nhạy cảm, vi phạm nguyên tắc đặc quyền tối thiểu (Least Privilege) và dẫn đến lệch cấu hình (Configuration Drift).

### 1.2. Yêu cầu Tổng quan của Khách hàng (Customer Requirements Overview)

Các yêu cầu nghiệp vụ cốt lõi làm kim chỉ nam cho toàn bộ thiết kế kỹ thuật:

**Về sử dụng Dịch vụ API (API Service)**

- **Ràng buộc chặt theo máy và theo dự án:** Mỗi tài khoản lập trình viên hoặc ứng dụng chỉ được phép sử dụng dịch vụ API trên **đúng 1 máy tính (hoặc 1 môi trường dịch vụ Docker)** đã đăng ký và phục vụ cho **đúng 1 dự án** được cấp phép.
- **Chống chia sẻ, sao chép Key:** Nếu API Key bị sao chép sang máy tính khác, gửi cho người khác, hoặc mang sang dùng cho dự án khác, hệ thống phải tự động phát hiện và chặn ngay lập tức.
- **Không lộ Key gốc:** Người dùng và ứng dụng không bao giờ nhìn thấy hoặc lưu giữ API Key gốc của nhà cung cấp dịch vụ (upstream), mà chỉ sử dụng khóa ảo (`Virtual Access Key`) do hệ thống trung tâm cấp phát.
- **Đúng dự án, đúng dịch vụ:** Mỗi dự án chỉ được gọi đúng danh sách các dịch vụ API đã duyệt (ví dụ: Dự án A chỉ được gọi Dịch vụ X và Y; nếu cố tình gọi sang Dịch vụ Z sẽ bị chặn).
- **Kiểm soát ngân sách và chống quá tải:** Mỗi dự án/đối tượng gọi có hạn mức sử dụng và tốc độ gọi riêng, đảm bảo một dự án chạy lỗi hoặc gọi quá nhiều không ảnh hưởng đến tài nguyên chung.

**Về quản lý file `.env` và Cấu hình Bí mật**

- **Xóa bỏ hoàn toàn file `.env` thủ công:** Chấm dứt việc gửi file `.env` qua công cụ chat/email hay lưu thông tin nhạy cảm (mật khẩu DB, khóa thanh toán, secret key) dưới dạng file plaintext trên ổ đĩa máy cá nhân.
- **Phân quyền rõ ràng theo vai trò (Least Privilege):**
    - Lập trình viên mảng **Tài chính/Thanh toán** được đọc các biến cấu hình thanh toán cùng với các biến dùng chung.
    - Lập trình viên mảng **Giao diện/Phổ thông** chỉ thấy các biến dùng chung, tuyệt đối không truy xuất được cấu hình tài chính hay hệ thống lõi.
- **Đổi một nơi, cập nhật mọi nơi:** Khi Quản trị viên hoặc Tech Lead thêm mới, thay đổi hoặc thu hồi một biến cấu hình trên hệ thống trung tâm, môi trường làm việc của tất cả lập trình viên và dịch vụ liên quan phải **tự động cập nhật** qua cơ chế SDK hot-reload mà không cần sửa tay hay khởi động lại tiến trình.
- **Nạp trực tiếp vào bộ nhớ:** Cấu hình mới được đẩy thẳng vào RAM của tiến trình ứng dụng đang chạy, không tạo file rác hay file bí mật lưu lại trên ổ đĩa.

### 1.3. Phạm vi Hệ thống (Scope)

- **Trong phạm vi (In-Scope):** Xác thực mTLS cho máy tính cá nhân và workload Docker, quản lý `Virtual Access Key` và `Identity Binding`, định tuyến và kiểm soát quota tại API Gateway, tích hợp đăng nhập SSO qua **DUT AI Manage**, quản lý bí mật tập trung theo scope/role, cung cấp SDK hỗ trợ nạp và hot-reload cấu hình trong RAM, ghi nhận Audit Log và cảnh báo vi phạm.
- **Ngoài phạm vi (Out-of-Scope):** Phát triển logic nghiệp vụ của các dịch vụ API upstream, phát triển ứng dụng đầu cuối (App A, App B), quản lý hạ tầng mạng vật lý/cloud nền tảng, xây dựng hệ thống quản lý danh tính DUT AI Manage.

## 2. Các Tác nhân Hệ thống (Actors)

| **Tác nhân** | **Mô tả** | **Tương tác chính** |
| --- | --- | --- |
| **Application / Workload** (VD: App A, App B) | Ứng dụng nội bộ chạy trên hạ tầng Docker cần gọi các dịch vụ API và nhận cấu hình vận hành. | Thiết lập mTLS tới API Gateway kèm `Virtual Access Key`; dùng SDK đồng bộ bí mật vào RAM từ Control Plane. |
| **Developer** | Lập trình viên phát triển và kiểm thử ứng dụng theo từng mảng nghiệp vụ. | Đăng nhập SSO qua **DUT AI Manage** để đăng ký thiết bị và lấy cấu hình động theo Role (qua SDK); gọi API Gateway bằng `Device Identity` và `Virtual Access Key`. |
| **System Admin / Tech Lead** | Người quản trị hệ thống, chính sách bảo mật và định mức tài nguyên API. | Đăng nhập qua **DUT AI Manage**; khởi tạo/thu hồi bí mật, phân quyền RBAC, cấp phát/thu hồi Identity và Virtual Key, thiết lập Service Scope và Quota. |
| **DUT AI Manage (IdP)** | Hệ thống quản lý định danh tập trung (SSO) có sẵn của tổ chức. | Xác thực tài khoản Developer/Admin và cung cấp thông tin định danh/vai trò cho Control Plane. |
| **Upstream API Services** | Các dịch vụ API đích (API nội bộ, API thanh toán, API dữ liệu, API AI...). | Nhận request đã được API Gateway xác thực, tiêm credential thực tế và định tuyến. |
| **Security Auditor / SIEM** | Bộ phận hoặc hệ thống giám sát an ninh. | Theo dõi Audit Log bất biến và tiếp nhận cảnh báo vi phạm bảo mật (Identity Mismatch, truy cập trái phép). |

## 3. Mô hình Định danh Truy cập & Ràng buộc (Client Identity & Binding Model)

Hệ thống tách biệt **máy tính cá nhân của lập trình viên** và **máy chủ chạy ứng dụng** ở tầng quản trị (Control Plane) để quản lý đúng vòng đời, nhưng hợp nhất cả hai thành một thực thể định danh duy nhất là **Registered Client** tại tầng **API Gateway**.

### 3.1. Phân loại Đối tượng & Cơ chế Ràng buộc

| **Thuộc tính** | **Máy tính Cá nhân (User Device)** | **Máy chủ Ứng dụng (App Server)** |
| --- | --- | --- |
| **Chủ sở hữu (Owner)** | Gắn với 1 tài khoản `User` từ DUT AI Manage. | Gắn với 1 `Application` (Service/Deployment chạy trên Docker). |
| **Định danh mật mã** | `Device Identity` (chứng chỉ mTLS cấp riêng cho máy tính đó). | `Machine Identity` (chứng chỉ mTLS cấp cho dịch vụ Docker). |
| **Quy tắc Ràng buộc Khóa (Identity Binding)** | `Virtual Access Key` = (`Device Identity` + `Project`). Mỗi User chỉ dùng 1 máy tính cho 1 dự án với 1 key duy nhất tại một thời điểm. | `Virtual Access Key` = (`Machine Identity` + `Project`). Mỗi Application chỉ gọi API từ workload mang chứng chỉ hợp lệ với 1 key duy nhất tại một thời điểm. |
| **Cơ chế Cấp phát (Provisioning)** | Cấp phát sau khi User đăng nhập SSO thành công qua **DUT AI Manage**. | Cấp phát tự động (headless) qua quy trình quản trị/triển khai Docker, không phụ thuộc tài khoản cá nhân. |
| **Vòng đời & Thu hồi** | Khóa tài khoản trên DUT AI Manage hoặc thu hồi thiết bị sẽ vô hiệu hóa toàn bộ chứng chỉ và Virtual Key liên quan. | Độc lập với nhân sự; quản lý theo vòng đời dịch vụ/môi trường (Staging, Production). |
| **Quyền nhận cấu hình (`.env`)** | Nhận biến môi trường động qua SDK theo `Role` (RBAC) của User trong dự án. | Nhận tập bí mật/cấu hình thuộc phạm vi khai báo của chính Application đó qua SDK. |

### 3.2. Nguyên tắc Thực thi Thống nhất tại API Gateway

- **Một luồng xác thực duy nhất:** Mọi request gửi tới API Gateway — dù từ `User Device` hay `App Server` — đều đi qua 3 bước tuần tự:
    1. Xác thực chứng chỉ mTLS hợp lệ (`Registered Client`).
    2. Đối chiếu định danh trích xuất từ chứng chỉ với chủ sở hữu và dự án của `Virtual Access Key` (`Identity Binding`).
    3. Kiểm tra phạm vi dịch vụ (`Service Scoping`) và hạn mức (`Quota / Rate Limit`) gắn với cặp `(Project, Registered Client, API Service)`.
- **Chống dùng chéo tuyệt đối:** Mọi hành vi sao chép `Virtual Access Key` sang máy khác, giữa máy cá nhân và server Docker, hoặc mang sang dùng cho dự án khác đều bị chặn ngay với mã `HTTP 403 Forbidden`.
- **Tách bạch Giám sát & Hạn mức:** Audit Log và chính sách Quota gắn nhãn rõ loại nguồn gọi (`User Device` vs. `App Server`) để phân tách lưu lượng phát triển/kiểm thử với lưu lượng vận hành thực tế.

### 3.3. Các Giả định & Ràng buộc Thiết kế (Assumptions & Constraints)

- **Định danh trên hạ tầng Docker:** Vì container Docker có tính chất tạo mới/xóa bỏ khi redeploy, `Machine Identity` được gắn ở cấp độ **Docker Service / Deployment** (như App A) thông qua cơ chế nạp chứng chỉ bảo mật, không gắn cứng theo Container ID đơn lẻ.
- **Chính sách 1 Key duy nhất (Single Active Key):** Mỗi cặp `(Registered Client, Project)` chỉ được phép có duy nhất 1 `Virtual Access Key` hoạt động tại một thời điểm. Hệ thống chấp nhận độ trễ gián đoạn ngắn (brief downtime) trong quá trình xoay vòng khóa khi key cũ bị vô hiệu hóa ngay lúc key mới có hiệu lực.
- **Developer tham gia nhiều dự án:** Một lập trình viên làm việc trên nhiều dự án cùng một máy tính sẽ dùng chung `Device Identity` của máy đó, nhưng mỗi dự án được cấp 1 `Virtual Access Key` riêng biệt để đảm bảo cô lập phạm vi và quota.
- **Chính sách Fail-Closed & Yêu cầu Trực tuyến:** Hệ thống ưu tiên bảo mật tuyệt đối trên tính sẵn sàng. Khi mất kết nối tới Control Plane, API Gateway lập tức từ chối các yêu cầu mới (Fail-Closed) và môi trường Developer không thể khởi chạy hoặc nạp cấu hình ở chế độ offline.

## 4. Các Kịch bản Người dùng & Kiểm thử (User Scenarios & Testing)

### Kịch bản 1 - Thực thi Định danh Client & Ràng buộc Khóa (Identity Binding) cho Dịch vụ API (Priority: P1)

Mọi `Registered Client` (`User Device` hoặc `App Server` trên Docker) chỉ có thể gọi dịch vụ API upstream qua API Gateway khi đồng thời chứng minh được chứng chỉ mTLS hợp lệ và sử dụng đúng `Virtual Access Key` gắn với chính nó và đúng `Project`.

- **Kiểm thử độc lập:** Triển khai hai client giả lập (Client A và Client B); xác minh Client A gọi thành công bằng đúng chứng chỉ và key của mình; sau đó cho Client B dùng key của Client A và kiểm tra Gateway từ chối ngay với lỗi Identity Mismatch.
- **Kịch bản Chấp thuận:**
    1. **Given** Client A có chứng chỉ mTLS hợp lệ và `Virtual Access Key` gắn với `(Client A, Project X)`, **When** Client A gọi dịch vụ API qua Gateway, **Then** Gateway xác thực mTLS thành công, khớp Identity Binding, tiêm credential upstream, chuyển tiếp request và ghi Audit Log thành công.
    2. **Given** Client B có chứng chỉ mTLS hợp lệ của Client B nhưng gửi kèm `Virtual Access Key` thuộc sở hữu của Client A (hoặc thuộc Project khác), **When** Client B gọi Gateway, **Then** Gateway phát hiện sai lệch định danh, lập tức trả về `HTTP 403 Forbidden`, ghi Audit Log và phát cảnh báo bảo mật.
    3. **Given** một client bên ngoài hoặc không có chứng chỉ mTLS hợp lệ cố gắng truy cập Gateway bằng key của Client A, **When** thiết lập kết nối, **Then** Gateway ngắt kết nối ngay tại tầng TLS Handshake.

### Kịch bản 2 - Quản lý Cấu hình Bí mật Tập trung & Phân quyền Đặc quyền Tối thiểu (Priority: P2)

Lập trình viên đăng nhập SSO qua **DUT AI Manage** để nhận cấu hình bí mật theo đúng vai trò nghiệp vụ, xóa bỏ hoàn toàn file `.env` thủ công.

- **Kiểm thử độc lập:** Đăng nhập hai tài khoản trên DUT AI Manage (Developer Phổ thông vs. Developer Tài chính); xác minh Developer Tài chính đọc được biến thanh toán, trong khi Developer Phổ thông bị từ chối khi yêu cầu biến tài chính.
- **Kịch bản Chấp thuận:**
    1. **Given** Developer thuộc vai trò Tài chính (Financial Role) xác thực SSO thành công qua DUT AI Manage, **When** SDK yêu cầu cấu hình cho dự án, **Then** Control Plane trả về đầy đủ biến dùng chung (Common) và biến chuyên biệt mảng tài chính.
    2. **Given** Developer thuộc vai trò Phổ thông (General Role) xác thực SSO thành công, **When** SDK yêu cầu cấu hình, **Then** Control Plane chỉ trả về biến dùng chung và từ chối mọi biến tài chính/thanh toán.
    3. **Given** phiên đăng nhập hết hạn, chưa xác thực hoặc token không hợp lệ, **When** gửi yêu cầu lấy cấu hình, **Then** Control Plane từ chối truy cập và ghi nhận vi phạm vào Audit Log.

### Kịch bản 3 - Tự động Đồng bộ Môi trường qua SDK Hot-Reload Không Cần File Thủ công (Priority: P3)

Khi Quản trị viên hoặc Tech Lead thay đổi, thêm mới hoặc thu hồi biến cấu hình trên Control Plane, tất cả ứng dụng đang chạy tích hợp SDK tự động cập nhật giá trị mới ngay trong bộ nhớ mà không cần khởi động lại hay chỉnh sửa file.

- **Kiểm thử độc lập:** Thay đổi giá trị một biến bí mật trên Control Plane và xác minh tiến trình ứng dụng tích hợp SDK nhận diện giá trị mới trong RAM mà không restart tiến trình và không phát sinh file `.env` trên ổ đĩa.
- **Kịch bản Chấp thuận:**
    1. **Given** Quản trị viên cập nhật một biến bí mật trên Control Plane, **When** thay đổi được lưu, **Then** tất cả tiến trình ứng dụng đã đăng ký scope biến đó tự động nhận thông báo/đồng bộ giá trị mới.
    2. **Given** ứng dụng đang chạy với SDK nạp cấu hình động trong bộ nhớ (in-memory hot-reload), **When** giá trị bí mật thay đổi trên trung tâm, **Then** tiến trình sử dụng ngay giá trị mới mà không cần restart và không ghi bất kỳ file bí mật nào xuống ổ đĩa.

### Kịch bản 4 - Phân vùng Phạm vi Dịch vụ (Service Scoping) & Kiểm soát Quota theo Số lượng Request (Priority: P4)

Mỗi dự án chỉ được phép gọi đúng danh sách tên dịch vụ API được duyệt và chịu giới hạn số lượng request (RPM/RPH/ngày) để tránh quá tải tài nguyên chung.

- **Kiểm thử độc lập:** Cho Client thuộc Dự án A (chỉ được cấp quyền gọi Dịch vụ X và Y) gửi request tới Dịch vụ Z và kiểm tra Gateway trả về lỗi từ chối; sau đó gửi vượt ngưỡng RPM quy định để kiểm tra mã `HTTP 429`.
- **Kịch bản Chấp thuận:**
    1. **Given** Dự án A chỉ được cấp phép gọi Dịch vụ X và Dịch vụ Y, **When** Client của Dự án A gọi tới Dịch vụ Z, **Then** Gateway chặn request với `HTTP 403 Forbidden` kèm thông báo không có quyền sử dụng dịch vụ này.
    2. **Given** Client hoặc Dự án A đã chạm trần số lượng request (RPM/RPH/ngày), **When** tiếp tục gửi request, **Then** Gateway trả về `HTTP 429 Too Many Requests` kèm thông tin điều tiết (`Retry-After`).

### Các Trường hợp Biên (Edge Cases)

- **Mất kết nối tới Control Plane (Fail-Closed):** Khi Control Plane không phản hồi, API Gateway từ chối mọi request mới (trả về lỗi dịch vụ không sẵn sàng `HTTP 503`) thay vì cho qua; môi trường Developer mất mạng không thể khởi động ứng dụng lấy cấu hình mới.
- **Chứng chỉ mTLS hết hạn hoặc bị thu hồi:** Dù mang đúng `Virtual Access Key`, kết nối vẫn bị ngắt ngay tại tầng TLS Handshake.
- **Thu hồi tài khoản trên DUT AI Manage:** Khi nhân sự bị vô hiệu hóa tài khoản, phiên SDK và quyền truy cập `Device Identity` bị chấm dứt và ghi log ngay ở chu kỳ kiểm tra kế tiếp.
- **Burst Traffic chạm ngưỡng Rate Limit:** Bộ đếm request phải đảm bảo tính nguyên tử (atomic) để không xảy ra vượt ngưỡng khi nhiều request đến đồng thời.

## 5. Yêu cầu Chức năng (Functional Requirements)

### Nhóm 1: Định danh Client & API Gateway (P1)

- **FR-01 (Xác thực mTLS bắt buộc):** API Gateway chỉ chấp nhận kết nối từ `Registered Client` (`User Device` hoặc `App Server`) mang chứng chỉ mTLS hợp lệ do hệ thống tin cậy cấp phát; ngắt kết nối ngay tại tầng TLS Handshake với mọi client không hợp lệ.
- **FR-02 (Ràng buộc Khóa - Identity Binding):** Mọi `Virtual Access Key` được gắn duy nhất với một cặp `(Registered Client, Project)`. Mỗi cặp chỉ có duy nhất 1 key hoạt động tại một thời điểm. Gateway đối chiếu định danh từ chứng chỉ mTLS với chủ sở hữu và dự án của key trên từng request.
- **FR-03 (Chặn sai lệch định danh):** Khi phát hiện Identity Mismatch (dùng key của máy khác hoặc dự án khác), Gateway từ chối ngay với `HTTP 403 Forbidden`, ghi Audit Log mức nghiêm trọng cao và kích hoạt cảnh báo bảo mật.
- **FR-04 (Che giấu Upstream Credentials):** `Registered Client` chỉ nắm giữ `Virtual Access Key`; API Gateway tự động tiêm credential thực tế (API Key, Bearer Token, Basic Auth...) trước khi chuyển tiếp request tới API upstream.

### Nhóm 2: Quản lý Bí mật Tập trung & Xác thực SSO (P2)

- **FR-05 (Phân nhóm cấu hình theo Scope):** Control Plane tổ chức biến môi trường và bí mật theo phạm vi dùng chung (`Common`) và phạm vi chuyên biệt (`Financial`, `Auth-Core`, `Frontend`...) gắn với từng `Project`.
- **FR-06 (Kiểm soát truy cập theo vai trò - RBAC):** Áp dụng nguyên tắc Least Privilege; Developer chỉ truy xuất được các scope gắn với vai trò của mình, còn `App Server` chỉ truy xuất được scope khai báo cho ứng dụng đó.
- **FR-07 (Tích hợp SSO qua DUT AI Manage):** Xác thực người dùng (Developer và Admin) hoàn toàn thông qua hệ thống định danh tập trung **DUT AI Manage** (OIDC/OAuth2). Mọi yêu cầu thiếu token hợp lệ đều bị từ chối và ghi vào Audit Log.

### Nhóm 3: Đồng bộ Cấu hình Động qua SDK (P3)

- **FR-08 (SDK In-Memory Injection):** Cung cấp thư viện SDK để nạp trực tiếp biến môi trường/bí mật vào vùng nhớ RAM của tiến trình ứng dụng, không ghi ra file `.env` hay file plaintext trên ổ đĩa.
- **FR-09 (Hot-Reload thời gian thực):** Khi Admin thêm mới, cập nhật hoặc thu hồi bí mật trên Control Plane, SDK tự động cập nhật giá trị mới trong bộ nhớ tiến trình đang chạy mà không yêu cầu khởi động lại ứng dụng.

### Nhóm 4: Phân vùng Dịch vụ & Kiểm soát Quota (P4)

- **FR-10 (Service Scoping ở mức Tên dịch vụ):** Cho phép cấu hình danh sách tên dịch vụ API được phép gọi (Allowlist) cho từng `Project` (hoặc chi tiết theo `(Project, Registered Client)`). Trả về `HTTP 403 Forbidden` nếu gọi dịch vụ ngoài danh sách.
- **FR-11 (Rate Limiting & Quota theo Số lượng Request):** Theo dõi và thực thi giới hạn số lượng request (RPM, RPH, hoặc theo ngày) gắn với `(Project, Registered Client, API Service)`. Trả về `HTTP 429 Too Many Requests` kèm header `Retry-After` khi vượt ngưỡng.

### Nhóm 5: Giám sát, Kiểm toán & An toàn Lỗi (Cross-cutting)

- **FR-12 (Audit Logging bất biến):** Ghi nhận đầy đủ các sự kiện: gọi API thành công/thất bại (phân tách nhãn `User Device` và `App Server`), Identity Mismatch, truy cập bí mật, đăng nhập SSO, và mọi thao tác thay đổi cấu hình/chính sách từ Admin.
- **FR-13 (Cơ chế Fail-Closed):** Khi kết nối giữa API Gateway hoặc SDK tới Control Plane bị gián đoạn, hệ thống mặc định từ chối xử lý yêu cầu mới (không dùng chính sách quá hạn hoặc chế độ chạy offline cho Developer) và ghi nhận cảnh báo hạ tầng.

## 6. Các Thực thể Cốt lõi (Key Entities)

- **Project:** Dự án nghiệp vụ; chứa danh sách dịch vụ API được cấp phép (Service Allowlist) và tập các scope bí mật liên quan.
- **Registered Client:** Thực thể trừu tượng đại diện cho nguồn gọi tại Gateway, phân loại gồm `User Device` (gắn với 1 `User`) hoặc `App Server` (gắn với 1 `Application` trên Docker), sở hữu chứng chỉ mTLS (`Device/Machine Identity`) có thời hạn và trạng thái thu hồi.
- **Virtual Access Key:** Khóa truy cập ảo gắn duy nhất với một cặp `(Registered Client, Project)`, đảm bảo ràng buộc tối đa 1 key ở trạng thái `active` tại một thời điểm.
- **Secret / Config Item:** Cặp khóa-giá trị được mã hóa, thuộc một `Scope` trong `Project`, có phiên bản (version) và lịch sử thay đổi.
- **User & Role:** Thông tin định danh đồng bộ từ **DUT AI Manage** và tập quyền RBAC ánh xạ tới các `Scope` được phép đọc/ghi.
- **Upstream API Service:** Định nghĩa dịch vụ API đích (tên dịch vụ, base URL, cơ chế xác thực upstream và credential thực tế đã mã hóa).
- **Quota & Rate Limit Policy:** Chính sách giới hạn số lượng request (RPM/RPH/ngày) gắn với `(Project, Registered Client, Upstream API Service)`.
- **Audit Event:** Bản ghi bất biến gồm timestamp, client type (`User Device` / `App Server`), actor, project, action, target resource, kết quả (`Allow`/`Deny`), mã lỗi và metadata.

## 7. Yêu cầu Phi chức năng & Tiêu chí Thành công (NFRs & Success Criteria)

- **Bảo mật (Security):**
    - 100% kết nối từ `Registered Client` (`User Device` và `App Server`) tới API Gateway sử dụng mTLS.
    - 100% bí mật được mã hóa khi lưu trữ (Encryption at Rest) và khi truyền tải (TLS 1.3).
    - Tuyệt đối không phát sinh file `.env` hoặc file bí mật dạng plaintext trên ổ đĩa máy Developer hay bên trong Docker image/container.
    - Audit Log không bao giờ lưu giá trị plaintext của bí mật, credential upstream hoặc `Virtual Access Key`.
    - Tuân thủ nghiêm ngặt chế độ **Fail-Closed** khi Control Plane mất kết nối.
- **Hiệu năng (Performance):**
    - Độ trễ phát sinh (overhead) tại API Gateway cho xác thực mTLS, kiểm tra Identity Binding và Quota giữ ở mức tối thiểu (mục tiêu dưới 20ms ở p95, chưa tính thời gian xử lý của API upstream).
    - Thời gian đẩy và cập nhật bí mật mới qua SDK hot-reload đảm bảo tính tức thời (mục tiêu dưới 5 giây kể từ khi Admin lưu thay đổi).
- **Độ tin cậy (Reliability):**
    - API Gateway chịu tải đồng thời từ nhiều `User Device` và `App Server` Docker mà không xảy ra hiện tượng ứng dụng này làm nghẽn ứng dụng khác (Noisy Neighbor).
    - Cơ chế đếm Rate Limit đảm bảo tính nguyên tử (atomic) dưới tải đồng thời cao.