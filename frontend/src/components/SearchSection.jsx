import { useState } from 'react'

export default function SearchSection({onSearch}) {
    const [query, setQuery] = useState()
    const [supermarkets, setSupermarkets] = useState(["ah", "dirk", "hoogvliet"])
    const [lang, setLang] = useState("du")

    function handleChange(e) {
        setQuery(e.target.value)
    }

    function handleSubmit(e) {
        e.preventDefault()
        onSearch({query, lang, supermarkets})
    }

    function handleCheckboxChange(name) {
        setSupermarkets(prev => prev.includes(name) ? prev.filter(s => s !== name) : [...prev, name])
        console.log(supermarkets)
    }

    return (
        <section className="search-section">
            <h1>Compare Dutch Supermarkets</h1>
            <div className="text-grey">Compare prices across top supermarkets in the Netherlands and never overpay again.</div>


            <div className="form-container">
                <form 
                    onSubmit={handleSubmit}
                >
                    <div className="filter-container white-container">
                        <fieldset className="filter-part-section">
                            <legend><h4>Supermarkets</h4></legend>
                            
                            <div className="text-grey explain-text">Select one or more stores to compare</div>
                            
                            <div className="store-checkbox-container">
                                <div className="store-container">
                                    <input 
                                        type="checkbox" 
                                        name="supermarket"
                                        value="ah"
                                        id="ah"
                                        checked={supermarkets.includes("ah")}
                                        onChange={() => handleCheckboxChange("ah")}
                                        className="check-box"
                                    />
                                    <label htmlFor="ah" className="store-clickable-label">
                                        <img src="/img/ah.png" alt="ah icon" className="filter-store-icon"/>
                                        <div>Albert Hejin</div>
                                    </label>
                                </div>

                                <div className="store-container">
                                    <input 
                                        type="checkbox" 
                                        name="supermarket"
                                        value="dirk"
                                        id="dirk"
                                        checked={supermarkets.includes("dirk")}
                                        onChange={() => handleCheckboxChange("dirk")}
                                        className="check-box"
                                    />
                                    <label htmlFor="dirk" className="store-clickable-label">
                                        <img src="/img/dirk.png" alt="dirk icon" className="filter-store-icon"/>
                                        <div>Dirk</div>
                                    </label>
                                </div>

                                <div className="store-container">
                                    <input 
                                        type="checkbox" 
                                        name="supermarket"
                                        value="hoogvliet"
                                        id="hoogvliet"
                                        checked={supermarkets.includes("hoogvliet")}
                                        onChange={() => handleCheckboxChange("hoogvliet")}
                                        className="check-box"
                                    />
                                    <label htmlFor="hoogvliet" className="store-clickable-label">
                                        <img src="/img/hoogvliet.png" alt="hoogvliet icon" className="filter-store-icon"/>
                                        <div>Hoogvliet</div>
                                    </label>     
                                </div>                                
                            </div>
                        </fieldset>

                        <fieldset className="filter-part-section">
                            <legend><h4>Language</h4></legend>
                            <div className="text-grey explain-text">Choose your search language</div>
                            <div className="language-container top-language-container">
                                <input type="radio" name="lang" id="du" value="du" checked={lang === "du"} onChange={() => setLang("du")} className="check-box"/>                                
                                <label htmlFor="du" className="language-clickable-label">NL</label>
                            </div>                            
                            <div className="language-container">
                                <input type="radio" name="lang" id="en" value="en" checked={lang === "en"} onChange={() => setLang("en")} className="check-box"/>
                                <label htmlFor="en" className="language-clickable-label">EN</label>
                            </div>
                        </fieldset>
                    </div>

                    <div className="search-container white-container">
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
                    </div>

                    
                </form>
            </div>
        </section>
    )
}