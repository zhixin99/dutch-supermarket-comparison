

import ProductCard from "./ProductCard"
import { useEffect } from "react"

export default function ProductResultSection({products, isLoading}) {
    
    const productCardEl = products.map(product => (
        <ProductCard 
            supermarket={product.supermarket} 
            id={product.id}
            key={product.id}
            image={product.image}
            brand={product.brand}
            productName={product.product_name_du}
            currentPrice={product.current_price} 
            regularPrice={product.regular_price}
            unit={product.unit_qty} 
            pricePerUnit={product.unit_price} 
            url={product.url} 
            unitType={product.unit_type_du} 
        />
    ))

    return (
        <section className="result-section">
            <h2>Search Results</h2>

            <div className="card-container">
            {productCardEl}
            </div>
        </section>

    )
}
