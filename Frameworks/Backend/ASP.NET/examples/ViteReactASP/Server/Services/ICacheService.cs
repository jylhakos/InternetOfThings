namespace ViteReactASP.Server.Services
{
    public interface ICacheService
    {
        Task<T?> GetAsync<T>(string key) where T : class;
        Task SetAsync<T>(string key, T value, TimeSpan? expiration = null) where T : class;
        Task RemoveAsync(string key);
        Task RemovePatternAsync(string pattern);
        Task<bool> ExistsAsync(string key);
        Task ClearAllAsync();
    }
}
