using TaskAPI.Models;

namespace TaskAPI.Services;

public interface IAuthService
{
    Task<AuthResponse?> LoginAsync(UserLoginRequest request);
    Task<AuthResponse?> RegisterAsync(UserCreateRequest request);
    string GenerateJwtToken(User user);
    Task<User?> GetUserFromTokenAsync(string token);
}