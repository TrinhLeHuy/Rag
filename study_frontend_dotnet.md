# Sổ Tay Lập Trình Giao Diện RAG bằng .NET - Phiên Bản Enterprise (Web Crawler)

Tài liệu này hướng dẫn cách xây dựng một giao diện người dùng (Frontend) bằng **.NET (Blazor WebAssembly)** kết nối với hệ thống Backend Enterprise RAG. Điểm khác biệt lớn nhất là thay vì thiết kế màn hình Upload File cồng kềnh, chúng ta sẽ làm một giao diện **Web Crawler** tinh gọn, cho phép người dùng ra lệnh cho Backend cào dữ liệu từ một URL (ví dụ: Báo cáo phát triển bền vững của TTC AgriS).

---

## 1. Thư mục `Services/` (Tầng Gọi API)
Ta sẽ thay thế file `DocumentService.cs` cũ bằng `CrawlerService.cs` để giao tiếp với API `/api/crawler`.

**File: `Services/CrawlerService.cs` (MỚI)**
Gửi một gói tin JSON chứa đường link cần cào lên hệ thống FastAPI.
```csharp
using System.Net.Http.Json;

namespace RagFrontend.Services
{
    public class CrawlerService
    {
        private readonly HttpClient _httpClient;

        public CrawlerService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        // Hàm gọi API Crawl Web
        public async Task<string> CrawlUrlAsync(string url)
        {
            var request = new CrawlRequest { Url = url };
            
            // Gửi JSON chứa URL sang Backend Python
            var response = await _httpClient.PostAsJsonAsync("http://localhost:8000/api/crawler/", request);
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<CrawlResponse>();
                return result?.Message ?? "Cào dữ liệu thành công và đã đẩy lên Cloud DB!";
            }
            return "Lỗi khi gọi bot cào dữ liệu.";
        }
    }

    public class CrawlRequest
    {
        public string Url { get; set; }
    }

    public class CrawlResponse
    {
        public string Message { get; set; }
        public string Url { get; set; }
    }
}
```

Đừng quên đăng ký Service này trong file **`Program.cs`**:
```csharp
// Thay thế builder.Services.AddScoped<DocumentService>(); bằng:
builder.Services.AddScoped<CrawlerService>();
```

---

## 2. Thư mục `Pages/` (Các Màn Hình Giao Diện)

### 2.1. Trang Giao Việc Cho Bot (Crawl Web)
**File: `Pages/Crawler.razor` (Thay thế cho Upload.razor)**
Màn hình này cho phép người dùng dán một đường link (ví dụ trang web TTC AgriS) và ra lệnh cho AI học kiến thức từ trang đó.

```razor
@page "/crawler"
@using RagFrontend.Services
@inject CrawlerService CrawlService

<h3>Ra Lệnh Bot Đọc Website (Data Ingestion)</h3>

<div class="card p-3 shadow-sm mt-4">
    <div class="mb-3">
        <label class="form-label fw-bold">Nhập đường dẫn trang web cần học:</label>
        <!-- Mặc định truyền sẵn URL báo cáo của TTC AgriS làm ví dụ -->
        <input type="text" class="form-control" @bind="targetUrl" />
        <small class="text-muted">Hệ thống sẽ tự động vào link này, lọc quảng cáo, đọc nội dung và lưu lên Cloud Vector Database (Pinecone).</small>
    </div>

    <button class="btn btn-primary" @onclick="StartCrawling" disabled="@isCrawling">
        @if (isCrawling)
        {
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span> Đang phân tích và xử lý Semantic Chunking...</span>
        }
        else
        {
            <span>Bắt Đầu Cào Dữ Liệu</span>
        }
    </button>

    @if (!string.IsNullOrEmpty(statusMessage))
    {
        <div class="alert alert-info mt-3">@statusMessage</div>
    }
</div>

@code {
    // Để sẵn ví dụ TTC AgriS cho dễ test
    private string targetUrl = "https://ttcagris.com.vn/bao-cao-phat-trien-ben-vung";
    private string statusMessage = "";
    private bool isCrawling = false;

    private async Task StartCrawling()
    {
        if (string.IsNullOrWhiteSpace(targetUrl))
        {
            statusMessage = "Vui lòng nhập đường link!";
            return;
        }

        isCrawling = true;
        statusMessage = "Bot đang đọc trang web. Quá trình này có thể tốn vài phút...";
        
        // Gọi Service gửi URL sang Python
        statusMessage = await CrawlService.CrawlUrlAsync(targetUrl);
        
        isCrawling = false;
    }
}
```

### 2.2. Trang Chat Với AI (`Pages/Chat.razor`)
Khung Chat không cần thay đổi code so với trước đây vì quá trình `Cào dữ liệu (Crawler)` và `Trả lời câu hỏi (Chat)` đã được thiết kế hoàn toàn tách biệt (Decoupled). Backend FastAPI đã tự động chuyển kết nối tìm kiếm từ Local ChromaDB sang Cloud Pinecone, nên Frontend chỉ việc gửi câu hỏi và nhận câu trả lời như cũ, nhưng **tốc độ sẽ nhanh hơn** và **chất lượng câu trả lời chính xác hơn** nhờ mô hình nhúng xịn và Semantic Chunking.

---

## 3. Cách Cập Nhật Lại Menu Thanh Điều Hướng
Để người dùng thấy được chức năng Crawler, bạn sửa file Menu của Blazor.
**File: `Shared/NavMenu.razor`**

```razor
<div class="nav-scrollable" onclick="ToggleNavMenu">
    <nav class="flex-column">
        <!-- Đổi đường dẫn từ upload sang crawler -->
        <div class="nav-item px-3">
            <NavLink class="nav-link" href="crawler">
                <span class="oi oi-globe" aria-hidden="true"></span> Đọc Website
            </NavLink>
        </div>
        <div class="nav-item px-3">
            <NavLink class="nav-link" href="chat">
                <span class="oi oi-chat" aria-hidden="true"></span> Hỏi Đáp AI
            </NavLink>
        </div>
    </nav>
</div>
```

---

**=> Hoàn Tất!** 
Bây giờ khi chạy ứng dụng `dotnet watch run`, bạn chỉ việc vào mục "Đọc Website", bấm nút, và Frontend sẽ ra lệnh cho Backend cào toàn bộ nội dung Báo cáo phát triển bền vững của TTC AgriS, đẩy lên Pinecone Cloud, và bạn có thể sang trang Chat để hỏi AI về tình hình doanh nghiệp ngay lập tức!
