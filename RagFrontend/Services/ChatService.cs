using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace RagFrontend.Services
{
    public class ChatService
    {
        private readonly HttpClient _httpClient;

        public event Action? OnChange;
        public void NotifyStateChanged() => OnChange?.Invoke();

        public ChatService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<ChatResponse> SendMessageAsync(string query, string sessionId = "nguoidung_dotnet", string username = "guest")
        {
            var request = new ChatRequest { Query = query, SessionId = sessionId, Username = username };
            
            // Gửi dữ liệu dạng JSON
            var response = await _httpClient.PostAsJsonAsync("http://localhost:8000/api/chat/", request);
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<ChatResponse>();
                return result ?? new ChatResponse { Answer = "Lỗi parse JSON." };
            }
            
            return new ChatResponse { Answer = "Lỗi kết nối tới Server AI." };
        }

        public async Task<List<ChatSessionResponse>> GetSessionsAsync(string username)
        {
            var response = await _httpClient.GetAsync($"http://localhost:8000/api/chat/sessions/{username}");
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<List<ChatSessionResponse>>();
                return result ?? new List<ChatSessionResponse>();
            }
            return new List<ChatSessionResponse>();
        }

        public async Task<List<ChatHistoryResponse>> GetHistoryAsync(string sessionId)
        {
            var response = await _httpClient.GetAsync($"http://localhost:8000/api/chat/history/{sessionId}");
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<List<ChatHistoryResponse>>();
                return result ?? new List<ChatHistoryResponse>();
            }
            return new List<ChatHistoryResponse>();
        }

        public async Task<bool> DeleteHistoryAsync(string sessionId)
        {
            var response = await _httpClient.DeleteAsync($"http://localhost:8000/api/chat/history/{sessionId}");
            return response.IsSuccessStatusCode;
        }

        public async Task<bool> DeleteAllHistoryAsync(string username)
        {
            var response = await _httpClient.DeleteAsync($"http://localhost:8000/api/chat/history/all/{username}");
            return response.IsSuccessStatusCode;
        }
    }

    // Cấu trúc cục hàng gửi đi
    public class ChatRequest
    {
        public string Query { get; set; } = string.Empty;
        public string SessionId { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
    }

    // Cấu trúc cục hàng nhận về
    public class ChatResponse
    {
        public string Answer { get; set; } = string.Empty;
        public List<string> Sources { get; set; } = new List<string>();
    }

    public class ChatHistoryResponse
    {
        [JsonPropertyName("user_message")]
        public string UserMessage { get; set; } = string.Empty;
        
        [JsonPropertyName("ai_response")]
        public string AiResponse { get; set; } = string.Empty;
        
        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; } = string.Empty;
    }

    public class ChatSessionResponse
    {
        [JsonPropertyName("session_id")]
        public string SessionId { get; set; } = string.Empty;
        
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;
    }
}
