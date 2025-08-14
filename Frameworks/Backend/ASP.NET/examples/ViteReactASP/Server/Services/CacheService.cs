using Microsoft.Extensions.Caching.Memory;
using System.Collections.Concurrent;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace ViteReactASP.Server.Services
{
    public class CacheService : ICacheService
    {
        private readonly IMemoryCache _memoryCache;
        private readonly ILogger<CacheService> _logger;
        private readonly ConcurrentDictionary<string, bool> _cacheKeys;
        private readonly object _lock = new();

        public CacheService(IMemoryCache memoryCache, ILogger<CacheService> logger)
        {
            _memoryCache = memoryCache;
            _logger = logger;
            _cacheKeys = new ConcurrentDictionary<string, bool>();
        }

        public async Task<T?> GetAsync<T>(string key) where T : class
        {
            try
            {
                if (_memoryCache.TryGetValue(key, out var cachedValue))
                {
                    _logger.LogInformation("Cache hit for key: {Key}", key);
                    
                    if (cachedValue is string jsonString)
                    {
                        return JsonSerializer.Deserialize<T>(jsonString);
                    }
                    
                    return cachedValue as T;
                }

                _logger.LogDebug("Cache miss for key: {Key}", key);
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving from cache for key: {Key}", key);
                return null;
            }
        }

        public async Task SetAsync<T>(string key, T value, TimeSpan? expiration = null) where T : class
        {
            try
            {
                if (value == null)
                {
                    _logger.LogWarning("Attempted to cache null value for key: {Key}", key);
                    return;
                }

                var options = new MemoryCacheEntryOptions();
                
                if (expiration.HasValue)
                {
                    options.SetAbsoluteExpiration(expiration.Value);
                }
                else
                {
                    options.SetAbsoluteExpiration(TimeSpan.FromMinutes(30)); // Default 30 minutes
                }

                options.RegisterPostEvictionCallback((evictedKey, evictedValue, reason, state) =>
                {
                    var keyString = evictedKey?.ToString() ?? "";
                    _cacheKeys.TryRemove(keyString, out _);
                    _logger.LogDebug("Cache entry evicted: {Key}, Reason: {Reason}", keyString, reason);
                });

                var serializedValue = JsonSerializer.Serialize(value, new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    WriteIndented = false
                });
                
                _memoryCache.Set(key, serializedValue, options);
                _cacheKeys.TryAdd(key, true);
                
                _logger.LogDebug("Cache set for key: {Key}, Expiration: {Expiration}", key, expiration?.ToString() ?? "Default");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting cache for key: {Key}", key);
            }
        }

        public async Task RemoveAsync(string key)
        {
            try
            {
                _memoryCache.Remove(key);
                _cacheKeys.TryRemove(key, out _);
                _logger.LogDebug("Cache removed for key: {Key}", key);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing cache for key: {Key}", key);
            }
        }

        public async Task RemovePatternAsync(string pattern)
        {
            try
            {
                var regex = new Regex(pattern, RegexOptions.IgnoreCase);
                var keysToRemove = _cacheKeys.Keys.Where(k => regex.IsMatch(k)).ToList();
                
                foreach (var key in keysToRemove)
                {
                    _memoryCache.Remove(key);
                    _cacheKeys.TryRemove(key, out _);
                }
                
                _logger.LogInformation("Removed {Count} cache entries matching pattern: {Pattern}", keysToRemove.Count, pattern);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing cache entries by pattern: {Pattern}", pattern);
            }
        }

        public async Task<bool> ExistsAsync(string key)
        {
            try
            {
                return _memoryCache.TryGetValue(key, out _);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking cache existence for key: {Key}", key);
                return false;
            }
        }

        public async Task ClearAllAsync()
        {
            try
            {
                lock (_lock)
                {
                    var keysToRemove = _cacheKeys.Keys.ToList();
                    foreach (var key in keysToRemove)
                    {
                        _memoryCache.Remove(key);
                        _cacheKeys.TryRemove(key, out _);
                    }
                    _logger.LogInformation("Cleared all cache entries. Total removed: {Count}", keysToRemove.Count);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error clearing all cache entries");
            }
        }
    }
}
