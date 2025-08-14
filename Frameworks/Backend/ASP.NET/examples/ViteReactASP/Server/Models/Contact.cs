using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ViteReactASP.Server.Models
{
    public class Contact
    {
        [Key]
        public int Id { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = string.Empty;
        
        [Required]
        [Phone]
        [MaxLength(20)]
        public string PhoneNumber { get; set; } = string.Empty;
        
        [EmailAddress]
        [MaxLength(255)]
        public string? Email { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        
        [MaxLength(500)]
        public string? Notes { get; set; }
        
        [MaxLength(100)]
        public string? Company { get; set; }
        
        [MaxLength(200)]
        public string? Address { get; set; }
        
        public bool IsActive { get; set; } = true;
        
        [MaxLength(50)]
        public string? Category { get; set; }
    }
}
