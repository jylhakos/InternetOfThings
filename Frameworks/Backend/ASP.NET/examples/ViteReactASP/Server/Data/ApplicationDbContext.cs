using Microsoft.EntityFrameworkCore;
using ViteReactASP.Server.Models;

namespace ViteReactASP.Server.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }
        
        public DbSet<Contact> Contacts { get; set; }
        
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            
            // Configure Contact entity
            modelBuilder.Entity<Contact>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
                entity.Property(e => e.PhoneNumber).IsRequired().HasMaxLength(20);
                entity.Property(e => e.Email).HasMaxLength(255);
                entity.Property(e => e.Notes).HasMaxLength(500);
                entity.Property(e => e.Company).HasMaxLength(100);
                entity.Property(e => e.Address).HasMaxLength(200);
                entity.Property(e => e.Category).HasMaxLength(50);
                entity.HasIndex(e => e.PhoneNumber).IsUnique();
                entity.HasIndex(e => e.Email).IsUnique();
                
                // Set default values
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("CURRENT_TIMESTAMP");
                entity.Property(e => e.UpdatedAt).HasDefaultValueSql("CURRENT_TIMESTAMP");
                entity.Property(e => e.IsActive).HasDefaultValue(true);
            });
            
            // Seed data
            modelBuilder.Entity<Contact>().HasData(
                new Contact 
                { 
                    Id = 1, 
                    Name = "John Doe", 
                    PhoneNumber = "+1234567890", 
                    Email = "john.doe@example.com",
                    Notes = "Sample contact",
                    Company = "Tech Corp",
                    Category = "Business",
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Contact 
                { 
                    Id = 2, 
                    Name = "Jane Smith", 
                    PhoneNumber = "+0987654321", 
                    Email = "jane.smith@example.com",
                    Notes = "Another sample contact",
                    Company = "Design Studio",
                    Category = "Client",
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Contact 
                { 
                    Id = 3, 
                    Name = "Bob Johnson", 
                    PhoneNumber = "+1555123456", 
                    Email = "bob.johnson@example.com",
                    Notes = "IoT project manager",
                    Company = "IoT Solutions Inc",
                    Category = "Project",
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                }
            );
        }
    }
}
