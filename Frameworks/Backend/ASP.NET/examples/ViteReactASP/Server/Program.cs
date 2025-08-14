using Microsoft.AspNetCore.Cors;
using Microsoft.EntityFrameworkCore;
using ViteReactASP.Server.Data;
using ViteReactASP.Server.Services;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.WriteIndented = true;
    });

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { 
        Title = "Vite React ASP.NET Core API", 
        Version = "v1",
        Description = "Contact Management API with Caching and Transactions"
    });
});

// Configure Database (SQLite for development, can be changed to PostgreSQL in production)
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") 
    ?? "Data Source=contacts.db";

builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseSqlite(connectionString);
    if (builder.Environment.IsDevelopment())
    {
        options.EnableSensitiveDataLogging();
        options.EnableDetailedErrors();
    }
});

// Add Memory Caching
builder.Services.AddMemoryCache();
builder.Services.AddScoped<ICacheService, CacheService>();

// Configure CORS for Vite React frontend
builder.Services.AddCors(options =>
{
    options.AddPolicy("ViteReactPolicy", policy =>
    {
        policy.WithOrigins(
            "http://localhost:5173",    // Vite dev server default port
            "https://localhost:5173",   // Vite dev server HTTPS
            "http://localhost:4173",    // Vite preview port
            "https://localhost:4173"    // Vite preview HTTPS
        )
        .AllowAnyHeader()
        .AllowAnyMethod()
        .AllowCredentials()
        .SetIsOriginAllowedToAllowWildcardSubdomains();
    });
});

// Add logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

// Add health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<ApplicationDbContext>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "Vite React ASP API V1");
        options.RoutePrefix = "swagger";
        options.EnableTryItOutByDefault();
    });
    app.UseDeveloperExceptionPage();
}

// Security headers
app.Use(async (context, next) =>
{
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
    await next();
});

app.UseHttpsRedirection();

// Enable CORS - must be before UseAuthorization
app.UseCors("ViteReactPolicy");

app.UseAuthorization();

// Map controllers
app.MapControllers();

// Map health checks
app.MapHealthChecks("/health");

// Serve static files for production (Vite build output)
app.UseDefaultFiles();
app.UseStaticFiles();

// Fallback routing for SPA (important for client-side routing)
app.MapFallbackToFile("/index.html");

// Root endpoint with API info
app.MapGet("/", () => Results.Ok(new { 
    Message = "Vite React ASP.NET Core API with Contact Management",
    Version = "1.0.0",
    Environment = app.Environment.EnvironmentName,
    Endpoints = new[] {
        "/swagger - API Documentation",
        "/api/contacts - Contact CRUD operations",
        "/api/contacts/search/{term} - Search contacts",
        "/api/contacts/stats - Contact statistics",
        "/api/contacts/bulk - Bulk operations",
        "/health - Health check"
    },
    Features = new[] {
        "Entity Framework with SQLite",
        "Memory Caching with invalidation",
        "Database transactions",
        "Soft delete functionality",
        "Bulk operations",
        "Advanced search",
        "Statistics endpoints"
    }
}));

// Ensure database is created and seeded
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
    
    try
    {
        await context.Database.EnsureCreatedAsync();
        logger.LogInformation("Database initialized successfully");
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "An error occurred while initializing the database");
    }
}

var logger = app.Services.GetRequiredService<ILogger<Program>>();
logger.LogInformation("🚀 Starting Vite React ASP.NET Core application with Contact Management...");
logger.LogInformation("📊 Features: Caching, Transactions, CRUD Operations, Search, Statistics");

app.Run();
