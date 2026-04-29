import { useState } from 'react'

export default function SearchSection({onSearch}) {
    const [searchQuery, setSearchQuery] = useState()

    function handleChange(e) {
        setSearchQuery(e.target.value)
    }

    function handleSubmit(e) {
        e.preventDefault()
        onSearch(searchQuery, "du", ["ah", "dirk", "hoogvliet"], "unit_price")
    }


    return (
        <section className="search-section">
            <h1>Compare Dutch Supermarkets</h1>
            <div className="text-grey">Compare prices across top supermarkets in the Netherlands and never overpay again.</div>

            <div className="search-container">
                <form 
                    onSubmit={handleSubmit}
                    className="search-wrapper"
                >
                    <i class="fa-solid fa-magnifying-glass"></i>

                    <input 
                        type="text"
                        placeholder="Enter the product you want to search"
                        aria-label="Search bar for entering the product you want to search."
                        onChange={handleChange}
                        className="search-input"
                    >
                    </input>

                    <button className="search-button">Search</button>
                </form>
            </div>
        </section>
    )
}