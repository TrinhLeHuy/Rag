using System.Net.Http.Json;

namespace RagFrontend.Services
{
    public class AuthService
    {
        private readonly HttpClient _httpClient;

        // Lưu trữ thông tin người dùng đang đăng nhập (đơn giản)
        public string? CurrentUsername { get; private set; } = null;
        public bool IsLoggedIn => !string.IsNullOrEmpty(CurrentUsername);

        public AuthService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<string> RegisterAsync(string username, string password)
        {
            var request = new { username, password };
            var response = await _httpClient.PostAsJsonAsync("http://localhost:8000/api/auth/register", request);
            
            if (response.IsSuccessStatusCode) return "Đăng ký thành công!";
            return "Đăng ký thất bại (Tên đã tồn tại hoặc lỗi).";
        }

        public async Task<bool> LoginAsync(string username, string password)
        {
            var request = new { username, password };
            var response = await _httpClient.PostAsJsonAsync("http://localhost:8000/api/auth/login", request);
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<LoginResponse>();
                CurrentUsername = result?.Username;
                return true;
            }
            return false;
        }

        public void Logout()
        {
            CurrentUsername = null;
        }
    }

    public class LoginResponse
    {
        public string Message { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
    }
}
