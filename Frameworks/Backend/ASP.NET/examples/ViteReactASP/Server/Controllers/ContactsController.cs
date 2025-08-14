using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ViteReactASP.Server.Data;
using ViteReactASP.Server.Models;
using ViteReactASP.Server.Services;
using System.Transactions;

namespace ViteReactASP.Server.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ContactsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ICacheService _cacheService;
        private readonly ILogger<ContactsController> _logger;
        private const string CACHE_KEY_PREFIX = "contact_";
        private const string CACHE_KEY_ALL = "contacts_all";
        private const string CACHE_KEY_SEARCH_PREFIX = "search_";

        public ContactsController(
            ApplicationDbContext context, 
            ICacheService cacheService,
            ILogger<ContactsController> logger)
        {
            _context = context;
            _cacheService = cacheService;
            _logger = logger;
        }

        // GET: api/contacts
        [HttpGet]
        public async Task<ActionResult<IEnumerable<Contact>>> GetContacts([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
        {
            try
            {
                var cacheKey = $"{CACHE_KEY_ALL}_page_{page}_size_{pageSize}";
                
                // Try to get from cache first
                var cachedContacts = await _cacheService.GetAsync<List<Contact>>(cacheKey);
                if (cachedContacts != null)
                {
                    _logger.LogInformation("Retrieved {Count} contacts from cache (page {Page})", cachedContacts.Count, page);
                    return Ok(new { Data = cachedContacts, Page = page, PageSize = pageSize, FromCache = true });
                }

                // Get from database with pagination
                var contacts = await _context.Contacts
                    .Where(c => c.IsActive)
                    .OrderBy(c => c.Name)
                    .Skip((page - 1) * pageSize)
                    .Take(pageSize)
                    .ToListAsync();

                // Cache the results
                await _cacheService.SetAsync(cacheKey, contacts, TimeSpan.FromMinutes(15));
                
                var totalCount = await _context.Contacts.Where(c => c.IsActive).CountAsync();
                
                _logger.LogInformation("Retrieved {Count} contacts from database (page {Page})", contacts.Count, page);
                return Ok(new { 
                    Data = contacts, 
                    Page = page, 
                    PageSize = pageSize, 
                    TotalCount = totalCount,
                    FromCache = false 
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving contacts");
                return StatusCode(500, new { Error = "Internal server error", Details = ex.Message });
            }
        }

        // GET: api/contacts/5
        [HttpGet("{id}")]
        public async Task<ActionResult<Contact>> GetContact(int id)
        {
            try
            {
                var cacheKey = $"{CACHE_KEY_PREFIX}{id}";
                
                // Try cache first
                var cachedContact = await _cacheService.GetAsync<Contact>(cacheKey);
                if (cachedContact != null)
                {
                    _logger.LogInformation("Retrieved contact {Id} from cache", id);
                    return Ok(new { Data = cachedContact, FromCache = true });
                }

                // Get from database
                var contact = await _context.Contacts
                    .Where(c => c.Id == id && c.IsActive)
                    .FirstOrDefaultAsync();
                
                if (contact == null)
                {
                    return NotFound(new { Error = $"Contact with ID {id} not found" });
                }

                // Cache the result
                await _cacheService.SetAsync(cacheKey, contact, TimeSpan.FromMinutes(30));
                
                _logger.LogInformation("Retrieved contact {Id} from database", id);
                return Ok(new { Data = contact, FromCache = false });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving contact {Id}", id);
                return StatusCode(500, new { Error = "Internal server error", Details = ex.Message });
            }
        }

        // POST: api/contacts
        [HttpPost]
        public async Task<ActionResult<Contact>> CreateContact(Contact contact)
        {
            using var transaction = await _context.Database.BeginTransactionAsync();
            try
            {
                if (!ModelState.IsValid)
                {
                    return BadRequest(new { Error = "Invalid model", Details = ModelState });
                }

                // Check if phone number already exists
                var existingPhoneContact = await _context.Contacts
                    .FirstOrDefaultAsync(c => c.PhoneNumber == contact.PhoneNumber && c.IsActive);
                
                if (existingPhoneContact != null)
                {
                    return Conflict(new { Error = "A contact with this phone number already exists" });
                }

                // Check if email already exists (if provided)
                if (!string.IsNullOrEmpty(contact.Email))
                {
                    var existingEmailContact = await _context.Contacts
                        .FirstOrDefaultAsync(c => c.Email == contact.Email && c.IsActive);
                    
                    if (existingEmailContact != null)
                    {
                        return Conflict(new { Error = "A contact with this email already exists" });
                    }
                }

                contact.CreatedAt = DateTime.UtcNow;
                contact.UpdatedAt = DateTime.UtcNow;
                contact.IsActive = true;

                _context.Contacts.Add(contact);
                await _context.SaveChangesAsync();
                await transaction.CommitAsync();

                // Cache the new contact
                var cacheKey = $"{CACHE_KEY_PREFIX}{contact.Id}";
                await _cacheService.SetAsync(cacheKey, contact, TimeSpan.FromMinutes(30));
                
                // Invalidate list caches
                await _cacheService.RemovePatternAsync($"{CACHE_KEY_ALL}_.*");

                _logger.LogInformation("Created contact {Id} - {Name}", contact.Id, contact.Name);
                return CreatedAtAction(nameof(GetContact), new { id = contact.Id }, 
                    new { Data = contact, Message = "Contact created successfully" });
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Error creating contact");
                return StatusCode(500, new { Error = "Failed to create contact", Details = ex.Message });
            }
        }

        // PUT: api/contacts/5
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateContact(int id, Contact contact)
        {
            using var transaction = await _context.Database.BeginTransactionAsync();
            try
            {
                if (id != contact.Id)
                {
                    return BadRequest(new { Error = "ID mismatch" });
                }

                if (!ModelState.IsValid)
                {
                    return BadRequest(new { Error = "Invalid model", Details = ModelState });
                }

                var existingContact = await _context.Contacts
                    .FirstOrDefaultAsync(c => c.Id == id && c.IsActive);
                
                if (existingContact == null)
                {
                    return NotFound(new { Error = $"Contact with ID {id} not found" });
                }

                // Check if phone number is being changed and if it conflicts
                if (existingContact.PhoneNumber != contact.PhoneNumber)
                {
                    var phoneConflict = await _context.Contacts
                        .FirstOrDefaultAsync(c => c.PhoneNumber == contact.PhoneNumber && c.Id != id && c.IsActive);
                    
                    if (phoneConflict != null)
                    {
                        return Conflict(new { Error = "A contact with this phone number already exists" });
                    }
                }

                // Check email conflicts
                if (!string.IsNullOrEmpty(contact.Email) && existingContact.Email != contact.Email)
                {
                    var emailConflict = await _context.Contacts
                        .FirstOrDefaultAsync(c => c.Email == contact.Email && c.Id != id && c.IsActive);
                    
                    if (emailConflict != null)
                    {
                        return Conflict(new { Error = "A contact with this email already exists" });
                    }
                }

                // Update fields
                existingContact.Name = contact.Name;
                existingContact.PhoneNumber = contact.PhoneNumber;
                existingContact.Email = contact.Email;
                existingContact.Notes = contact.Notes;
                existingContact.Company = contact.Company;
                existingContact.Address = contact.Address;
                existingContact.Category = contact.Category;
                existingContact.UpdatedAt = DateTime.UtcNow;

                await _context.SaveChangesAsync();
                await transaction.CommitAsync();

                // Update cache
                var cacheKey = $"{CACHE_KEY_PREFIX}{id}";
                await _cacheService.SetAsync(cacheKey, existingContact, TimeSpan.FromMinutes(30));
                
                // Invalidate list caches
                await _cacheService.RemovePatternAsync($"{CACHE_KEY_ALL}_.*");
                await _cacheService.RemovePatternAsync($"{CACHE_KEY_SEARCH_PREFIX}.*");

                _logger.LogInformation("Updated contact {Id} - {Name}", id, contact.Name);
                return Ok(new { Data = existingContact, Message = "Contact updated successfully" });
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Error updating contact {Id}", id);
                return StatusCode(500, new { Error = "Failed to update contact", Details = ex.Message });
            }
        }

        // DELETE: api/contacts/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteContact(int id)
        {
            using var transaction = await _context.Database.BeginTransactionAsync();
            try
            {
                var contact = await _context.Contacts
                    .FirstOrDefaultAsync(c => c.Id == id && c.IsActive);
                
                if (contact == null)
                {
                    return NotFound(new { Error = $"Contact with ID {id} not found" });
                }

                // Soft delete - set IsActive to false
                contact.IsActive = false;
                contact.UpdatedAt = DateTime.UtcNow;

                await _context.SaveChangesAsync();
                await transaction.CommitAsync();

                // Remove from cache
                var cacheKey = $"{CACHE_KEY_PREFIX}{id}";
                await _cacheService.RemoveAsync(cacheKey);
                
                // Invalidate list caches
                await _cacheService.RemovePatternAsync($"{CACHE_KEY_ALL}_.*");
                await _cacheService.RemovePatternAsync($"{CACHE_KEY_SEARCH_PREFIX}.*");

                _logger.LogInformation("Deleted (soft) contact {Id} - {Name}", id, contact.Name);
                return Ok(new { Message = "Contact deleted successfully" });
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Error deleting contact {Id}", id);
                return StatusCode(500, new { Error = "Failed to delete contact", Details = ex.Message });
            }
        }

        // POST: api/contacts/bulk
        [HttpPost("bulk")]
        public async Task<ActionResult> CreateBulkContacts([FromBody] List<Contact> contacts)
        {
            using var transaction = await _context.Database.BeginTransactionAsync();
            try
            {
                var createdContacts = new List<Contact>();
                var errors = new List<string>();

                foreach (var contact in contacts)
                {
                    // Validate each contact
                    if (string.IsNullOrEmpty(contact.Name) || string.IsNullOrEmpty(contact.PhoneNumber))
                    {
                        errors.Add($"Contact missing required fields: Name={contact.Name}, Phone={contact.PhoneNumber}");
                        continue;
                    }

                    // Check for duplicates within the batch
                    if (contacts.Count(c => c.PhoneNumber == contact.PhoneNumber) > 1)
                    {
                        errors.Add($"Duplicate phone number in batch: {contact.PhoneNumber}");
                        continue;
                    }

                    // Check if phone number already exists in database
                    var existing = await _context.Contacts
                        .FirstOrDefaultAsync(c => c.PhoneNumber == contact.PhoneNumber && c.IsActive);
                    
                    if (existing != null)
                    {
                        errors.Add($"Phone number already exists: {contact.PhoneNumber}");
                        continue;
                    }

                    contact.CreatedAt = DateTime.UtcNow;
                    contact.UpdatedAt = DateTime.UtcNow;
                    contact.IsActive = true;
                    
                    _context.Contacts.Add(contact);
                    createdContacts.Add(contact);
                }

                if (createdContacts.Any())
                {
                    await _context.SaveChangesAsync();
                    await transaction.CommitAsync();

                    // Invalidate list caches
                    await _cacheService.RemovePatternAsync($"{CACHE_KEY_ALL}_.*");

                    _logger.LogInformation("Created {Count} contacts in bulk operation", createdContacts.Count);
                }
                else
                {
                    await transaction.RollbackAsync();
                }

                return Ok(new 
                { 
                    Message = $"Bulk operation completed", 
                    CreatedCount = createdContacts.Count,
                    ErrorCount = errors.Count,
                    Errors = errors,
                    CreatedContacts = createdContacts
                });
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Error in bulk create operation");
                return StatusCode(500, new { Error = "Bulk operation failed", Details = ex.Message });
            }
        }

        // GET: api/contacts/search/{term}
        [HttpGet("search/{term}")]
        public async Task<ActionResult<IEnumerable<Contact>>> SearchContacts(string term, [FromQuery] int page = 1, [FromQuery] int pageSize = 20)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(term))
                {
                    return BadRequest(new { Error = "Search term cannot be empty" });
                }

                var cacheKey = $"{CACHE_KEY_SEARCH_PREFIX}{term.ToLower()}_page_{page}_size_{pageSize}";
                
                // Try cache first
                var cachedResults = await _cacheService.GetAsync<List<Contact>>(cacheKey);
                if (cachedResults != null)
                {
                    return Ok(new { Data = cachedResults, Page = page, PageSize = pageSize, FromCache = true });
                }

                // Search database
                var contacts = await _context.Contacts
                    .Where(c => c.IsActive && (
                        c.Name.Contains(term) || 
                        c.PhoneNumber.Contains(term) || 
                        (c.Email != null && c.Email.Contains(term)) ||
                        (c.Company != null && c.Company.Contains(term)) ||
                        (c.Category != null && c.Category.Contains(term))
                    ))
                    .OrderBy(c => c.Name)
                    .Skip((page - 1) * pageSize)
                    .Take(pageSize)
                    .ToListAsync();

                // Cache search results for shorter time
                await _cacheService.SetAsync(cacheKey, contacts, TimeSpan.FromMinutes(5));
                
                return Ok(new { Data = contacts, Page = page, PageSize = pageSize, FromCache = false });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error searching contacts with term: {Term}", term);
                return StatusCode(500, new { Error = "Search failed", Details = ex.Message });
            }
        }

        // GET: api/contacts/stats
        [HttpGet("stats")]
        public async Task<ActionResult> GetContactStats()
        {
            try
            {
                var cacheKey = "contact_stats";
                var cachedStats = await _cacheService.GetAsync<object>(cacheKey);
                
                if (cachedStats != null)
                {
                    return Ok(new { Data = cachedStats, FromCache = true });
                }

                var stats = new
                {
                    TotalContacts = await _context.Contacts.CountAsync(c => c.IsActive),
                    TotalInactive = await _context.Contacts.CountAsync(c => !c.IsActive),
                    ContactsByCategory = await _context.Contacts
                        .Where(c => c.IsActive)
                        .GroupBy(c => c.Category ?? "Uncategorized")
                        .Select(g => new { Category = g.Key, Count = g.Count() })
                        .ToListAsync(),
                    ContactsWithEmail = await _context.Contacts.CountAsync(c => c.IsActive && c.Email != null),
                    ContactsWithCompany = await _context.Contacts.CountAsync(c => c.IsActive && c.Company != null),
                    RecentContacts = await _context.Contacts
                        .Where(c => c.IsActive && c.CreatedAt >= DateTime.UtcNow.AddDays(-30))
                        .CountAsync()
                };

                await _cacheService.SetAsync(cacheKey, stats, TimeSpan.FromMinutes(10));
                
                return Ok(new { Data = stats, FromCache = false });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving contact statistics");
                return StatusCode(500, new { Error = "Failed to retrieve statistics", Details = ex.Message });
            }
        }

        // DELETE: api/contacts/cache
        [HttpDelete("cache")]
        public async Task<ActionResult> ClearCache()
        {
            try
            {
                await _cacheService.RemovePatternAsync("contact_.*");
                await _cacheService.RemovePatternAsync("search_.*");
                
                _logger.LogInformation("Cleared all contact-related cache entries");
                return Ok(new { Message = "Cache cleared successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error clearing cache");
                return StatusCode(500, new { Error = "Failed to clear cache", Details = ex.Message });
            }
        }
    }
}
