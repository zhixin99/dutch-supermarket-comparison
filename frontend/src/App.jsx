import { useState } from 'react'
import './index.css'
import Header from './components/Header'
import SearchSection from './components/SearchSection'
import ProductResultSection from './components/ProductResultSection'

function App() {
	const [products, setProducts] = useState([])
    const [isLoading, setIsLoading] = useState(false)

	async function handleSearch(searchData) {
		const {query, lang, supermarkets} = searchData
		setIsLoading(true)
		try {
			const response = await fetch("https://dutch-supermarket-comparison.onrender.com/search", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ 
					query: query,
					lang: lang, 
					supermarkets: supermarkets }),
			})

			if (!response.ok) {
				throw new Error(`Server error: ${response.status}`)
			}

			const data = await response.json()
			setProducts(data)
		} catch (error) {
			console.error("Error fetching products:", error)
		} finally {
			setIsLoading(false)
		}
	}

	return (
		<>
			<Header/>
			<SearchSection
				onSearch={handleSearch}
			/>
			<ProductResultSection 
				products={products}
				isLoading={isLoading}
			/>
		</>
	)
}

export default App
