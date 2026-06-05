using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using RagFrontend;
using RagFrontend.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Đăng ký HttpClient làm "Người đưa thư" chung và tăng thời gian chờ (Timeout) lên 10 phút
builder.Services.AddScoped(sp => new HttpClient 
{ 
    BaseAddress = new Uri(builder.HostEnvironment.BaseAddress),
    Timeout = TimeSpan.FromMinutes(10) 
});

// Đăng ký các Dịch vụ gọi API của chúng ta (Dependency Injection)
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<CrawlerService>();
builder.Services.AddScoped<ChatService>();

await builder.Build().RunAsync();
