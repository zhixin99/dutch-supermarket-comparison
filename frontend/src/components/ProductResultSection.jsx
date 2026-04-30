import ProductCard from "./ProductCard"
import { useState } from "react"

export default function ProductResultSection({products, isLoading}) {
    //     {
    //   "results": {
    //     "query": "melk",
    //     "results": [
    //       {
    //         "supermarket": "hoogvliet",
    //         "id": 59458,
    //         "sku": "731607000",
    //         "url": "https://www.hoogvliet.com/product/den-eelder-geiten-melk",
    //          ... }, 
    //        {}, 
    //        {}...
    //     ]
    const [sortBy, setSortBy] = useState("price");

    const safeProducts = products?.results?.results || []

    const sortedProducts = [...safeProducts].sort((a, b) => {
        if (sortBy === "price") {
            return a.unit_price - b.unit_price;
        } else if (sortBy === "relevance") {
            return b.similarity - a.similarity;
        }
        return 0
    })
    
    const productCardEl = sortedProducts.map(product => (
        <ProductCard 
            supermarket={product.supermarket} 
            id={product.id}
            key={product.id}
            image={product.image}
            brand={product.brand}
            productName={product.product_name_du}
            currentPrice={product.current_price} 
            regularPrice={product.regular_price}
            pricePerUnit={product.unit_price} 
            url={product.url} 
            unitType={product.unit_type} 
            unitQty={product.unit_qty} 
        />
    ))

    return (
        <section className="result-section">
            {safeProducts.length ? <h2>Search Results</h2> : ""}

            <div aria-live="polite" className="sr-only">
                {isLoading ? "Searching for products..." : `${safeProducts.length} products found.`}
            </div>

            {isLoading && <div aria-hidden="true">Searching...</div>}

            {!isLoading && safeProducts.length > 0 && (
                <div className="sort-container">
                    <label htmlFor="sort">Sort by: </label>
                    <select 
                        id="sort" 
                        value={sortBy} 
                        onChange={(e) => setSortBy(e.target.value)}
                    >
                        <option value="relevance">Relevance</option>
                        <option value="price">Price per Unit</option>
                    </select>
                </div>
                )}

            <div className="card-container">
                {!isLoading && productCardEl}
            </div>
        </section>

    )
}
