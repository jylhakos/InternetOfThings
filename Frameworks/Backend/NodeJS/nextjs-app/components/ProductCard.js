import React from 'react';

const ProductCard = ({ product }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'in stock':
        return '#28a745';
      case 'low stock':
        return '#ffc107';
      case 'out of stock':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  return (
    <div className="product-card">
      <div className="product-image">
        {product.image ? (
          <img src={product.image} alt={product.name} />
        ) : (
          <div className="placeholder-image">
            <span>No Image</span>
          </div>
        )}
        <div className="product-badge" style={{ backgroundColor: getStatusColor(product.status) }}>
          {product.status}
        </div>
      </div>

      <div className="product-info">
        <h3 className="product-title">{product.name}</h3>
        <p className="product-description">{product.description}</p>
        
        <div className="product-details">
          <span className="product-category">{product.category}</span>
          <div className="product-rating">
            <span className="stars">{'★'.repeat(Math.floor(product.rating))}</span>
            <span className="rating-text">({product.rating})</span>
          </div>
        </div>

        <div className="product-footer">
          <div className="product-price">
            <span className="current-price">{formatPrice(product.price)}</span>
            {product.originalPrice && product.originalPrice > product.price && (
              <span className="original-price">{formatPrice(product.originalPrice)}</span>
            )}
          </div>
          <button className="add-to-cart-btn">Add to Cart</button>
        </div>
      </div>

      <style jsx>{`
        .product-card {
          border: 1px solid #e9ecef;
          border-radius: 12px;
          overflow: hidden;
          background: white;
          transition: all 0.3s ease;
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .product-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .product-image {
          position: relative;
          height: 200px;
          overflow: hidden;
        }

        .product-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .placeholder-image {
          width: 100%;
          height: 100%;
          background: #f8f9fa;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6c757d;
          font-weight: 500;
        }

        .product-badge {
          position: absolute;
          top: 10px;
          right: 10px;
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: bold;
          text-transform: uppercase;
        }

        .product-info {
          padding: 1rem;
          display: flex;
          flex-direction: column;
          flex-grow: 1;
        }

        .product-title {
          margin: 0 0 0.5rem 0;
          font-size: 1.1rem;
          font-weight: 600;
          color: #333;
          line-height: 1.4;
        }

        .product-description {
          margin: 0 0 1rem 0;
          color: #6c757d;
          font-size: 0.9rem;
          line-height: 1.5;
          flex-grow: 1;
        }

        .product-details {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .product-category {
          background: #e9ecef;
          color: #495057;
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 0.75rem;
          text-transform: capitalize;
        }

        .product-rating {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .stars {
          color: #ffc107;
          font-size: 0.9rem;
        }

        .rating-text {
          color: #6c757d;
          font-size: 0.8rem;
        }

        .product-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: auto;
        }

        .product-price {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .current-price {
          font-size: 1.2rem;
          font-weight: bold;
          color: #0070f3;
        }

        .original-price {
          font-size: 0.9rem;
          color: #6c757d;
          text-decoration: line-through;
        }

        .add-to-cart-btn {
          background: #0070f3;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.2s;
        }

        .add-to-cart-btn:hover {
          background: #0051a2;
        }

        .add-to-cart-btn:active {
          transform: translateY(1px);
        }
      `}</style>
    </div>
  );
};

export default ProductCard;
