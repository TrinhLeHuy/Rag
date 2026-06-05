using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace RagFrontend.Services
{
    public class CrawlerService
    {
        private readonly HttpClient _httpClient;
        private const string BaseUrl = "http://localhost:8000/api/crawler/";

        public CrawlerService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        /// <summary>
        /// Gửi yêu cầu crawl, server trả về job_id ngay lập tức (không chờ xử lý xong).
        /// </summary>
        public async Task<int> StartCrawlAsync(string url)
        {
            var request = new CrawlRequest { Url = url };
            var response = await _httpClient.PostAsJsonAsync(BaseUrl, request);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<CrawlStartResponse>();
            return result?.JobId ?? throw new Exception("Server không trả về Job ID");
        }

        /// <summary>
        /// Lấy trạng thái hiện tại của một job theo job_id.
        /// </summary>
        public async Task<CrawlStatusResponse> GetStatusAsync(int jobId)
        {
            var result = await _httpClient.GetFromJsonAsync<CrawlStatusResponse>($"{BaseUrl}{jobId}");
            return result ?? throw new Exception("Không đọc được trạng thái từ server");
        }
    }

    // --- Models ---

    public class CrawlRequest
    {
        [JsonPropertyName("url")]
        public string Url { get; set; } = "";
    }

    public class CrawlStartResponse
    {
        [JsonPropertyName("job_id")]
        public int JobId { get; set; }

        [JsonPropertyName("status")]
        public string Status { get; set; } = "";

        [JsonPropertyName("message")]
        public string Message { get; set; } = "";
    }

    public class CrawlStatusResponse
    {
        [JsonPropertyName("job_id")]
        public int JobId { get; set; }

        [JsonPropertyName("url")]
        public string Url { get; set; } = "";

        [JsonPropertyName("status")]
        public string Status { get; set; } = "";  // queued | processing | success | failed

        [JsonPropertyName("message")]
        public string Message { get; set; } = "";
    }
}
