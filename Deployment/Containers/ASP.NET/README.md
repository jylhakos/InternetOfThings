# RESTful application with C# and ASP.NET Core using MongoDB for Docker deployment

## The C# program entry point

```

	using TaskAPI.Data;
	using TaskAPI.Services;
	using TaskAPI.Models;
	using Microsoft.AspNetCore.Authentication.JwtBearer;
	using Microsoft.IdentityModel.Tokens;
	using Microsoft.OpenApi.Models;
	using System.Text;
	using System.Text.Json.Serialization;

	var builder = WebApplication.CreateBuilder(args);

	// Add services to the container
	builder.Services.AddControllers()
	    .AddJsonOptions(options =>
	    {
	        options.JsonSerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase;
	        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
	        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
	    });

	// MongoDB configuration
	builder.Services.Configure<MongoDbSettings>(
	    builder.Configuration.GetSection("MongoDbSettings"));

	builder.Services.AddSingleton<MongoDbContext>();
	builder.Services.AddScoped<IUserService, UserService>();
	builder.Services.AddScoped<ITaskService, TaskService>();
	builder.Services.AddScoped<IAuthService, AuthService>();

	// JWT Authentication
	var jwtKey = builder.Configuration["Jwt:Key"] ?? "YourSuperSecretKeyForJWTTokenGeneration123456789";
	var key = Encoding.ASCII.GetBytes(jwtKey);

	builder.Services.AddAuthentication(options =>
	{
	    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
	    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
	})
	.AddJwtBearer(options =>
	{
	    options.RequireHttpsMetadata = false;
	    options.SaveToken = true;
	    options.TokenValidationParameters = new TokenValidationParameters
	    {
	        ValidateIssuerSigningKey = true,
	        IssuerSigningKey = new SymmetricSecurityKey(key),
	        ValidateIssuer = false,
	        ValidateAudience = false,
	        ClockSkew = TimeSpan.Zero,
	        RequireExpirationTime = true,
	        ValidateLifetime = true
	    };
	});

	builder.Services.AddAuthorization();

	// CORS configuration
	builder.Services.AddCors(options =>
	{
	    options.AddPolicy("AllowReactApp", policy =>
	    {
	        policy.WithOrigins("http://localhost:3000", "http://localhost:3001", "https://localhost:3000")
	              .AllowAnyHeader()
	              .AllowAnyMethod()
	              .AllowCredentials();
	    });
	});

	// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
	builder.Services.AddEndpointsApiExplorer();
	builder.Services.AddSwaggerGen(c =>
	{
	    c.SwaggerDoc("v1", new OpenApiInfo 
	    { 
	        Title = "Task Management API", 
	        Version = "v1",
	        Description = "ASP.NET Core Web API with MongoDB",
	        Contact = new OpenApiContact
	        {
	            Name = "",
	            Email = "x.x@example.com"
	        }
	    });

	    // JWT Bearer token configuration for Swagger
	    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
	    {
	        Description = "JWT Authorization header using the Bearer scheme. Enter 'Bearer' [space] and then your token in the text input below.",
	        Name = "Authorization",
	        In = ParameterLocation.Header,
	        Type = SecuritySchemeType.ApiKey,
	        Scheme = "Bearer"
	    });

	    c.AddSecurityRequirement(new OpenApiSecurityRequirement
	    {
	        {
	            new OpenApiSecurityScheme
	            {
	                Reference = new OpenApiReference
	                {
	                    Type = ReferenceType.SecurityScheme,
	                    Id = "Bearer"
	                }
	            },
	            Array.Empty<string>()
	        }
	    });
	});

	// Health checks
	builder.Services.AddHealthChecks()
	    .AddCheck<MongoDbHealthCheck>("mongodb");

	var app = builder.Build();

	// Configure the HTTP request pipeline
	if (app.Environment.IsDevelopment())
	{
	    app.UseSwagger();
	    app.UseSwaggerUI(c =>
	    {
	        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Task Management API V1");
	        c.RoutePrefix = string.Empty; // Set Swagger UI at the app's root
	    });
	}

	app.UseRouting();
	app.UseCors("AllowReactApp");

	app.UseAuthentication();
	app.UseAuthorization();

	app.MapControllers();
	app.MapHealthChecks("/health");

	// Global exception handling
	app.UseExceptionHandler("/error");

	// Root endpoint
	app.MapGet("/", () => new
	{
	    message = "ASP.NET Core Web API with MongoDB",
	    timestamp = DateTime.UtcNow,
	    user = "",
	    date = "2025-06-22",
	    version = "1.0.0",
	    environment = app.Environment.EnvironmentName
	});

	Console.WriteLine($"🚀 ASP.NET Core API Starting");
	Console.WriteLine($"📅 Date: 2025-06-22 09:28:27 UTC");
	Console.WriteLine($"👤 User: ");
	Console.WriteLine($"🐧 Platform: Linux");
	Console.WriteLine($"🌍 Environment: {app.Environment.EnvironmentName}");

	app.Run();

```