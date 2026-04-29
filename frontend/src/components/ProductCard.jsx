export default function ProductCard({supermarket, id, image, brand, productName, currentPrice, regularPrice, unit, unitType, pricePerUnit, url}) {
    
    let discount = null

    if (currentPrice !== regularPrice) {
        discount = Math.round((currentPrice - regularPrice) / regularPrice * 100)
    }

    return (
        <>
        <div className="product-card" key={id}>

                <div className="discount-icon-container">
                    {discount && <span className="discount">{discount}%</span>}
                    <img src={`/img/${supermarket}.png`} alt={`${supermarket} store icon`} className="store-icon"/> 
                </div>


                <div>
                    <img src={image} alt={productName} className="store-image"/>
                </div>

                <div>
                    <div className="text-grey">{brand}</div>
                    <div>{productName}</div>
                </div>

                <div>
                    {currentPrice !== regularPrice && <span className="text-highlight price">€{currentPrice}</span>}
                    <span className={currentPrice !== regularPrice ? "striked" : "price"}>€{regularPrice}</span>
                    <div>€{pricePerUnit} per {unitType}</div>
                </div>

                <a 
                    className="view-product-btn"
                    href={url}
                    target="_blank"
                >
                    View Product
                </a>
        </div>
        </>
    )
} 