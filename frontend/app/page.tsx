"use client";

import { useState } from "react";
import ProductCard from "./productcard";

// ================= Styles =================
const baseCircle =
  "w-14 h-14 rounded-full flex items-center justify-center cursor-pointer text-sm font-medium select-none transition-all duration-200";

const activeRing =
  "ring-2 ring-[#4285F4] shadow-[0_0_8px_#4285F433]";

const softNeumorph =
  "bg-[#eef1f4] shadow-[2px_2px_5px_#d1d9e6,_-2px_-2px_5px_#ffffff]";

const softInset =
  "bg-[#eef1f4] shadow-[inset_3px_3px_6px_#d1d9e6,_inset_-3px_-3px_6px_#ffffff]";

// ================= Constants =================
const supermarketLogos: Record<string, string> = {
  ah: "/logos/ah.png",
  dirk: "/logos/dirk.png",
  hoogvliet: "/logos/hoogvliet.png",
};

const supermarketsList = [
  { id: "ah", label: "AH" },
  { id: "dirk", label: "Dirk" },
  { id: "hoogvliet", label: "Hoogvliet" },
];

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!;

const glassCard =
  "w-full rounded-3xl backdrop-blur-xl bg-white/40 shadow-lg px-6 py-8";

// ================= Types =================
import type { Product } from "./types/product";

// ================= Page =================
export default function HomePage() {
  const [productText, setProductText] = useState("");
  const [supermarkets, setSupermarkets] = useState<string[]>([
    "ah",
    "dirk",
    "hoogvliet",
  ]);
  const [lang, setLang] = useState<"du" | "en">("du");

  const [results, setResults] = useState<Product[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Toggle supermarket
  const toggleSupermarket = (value: string) => {
    setSupermarkets((prev) =>
      prev.includes(value)
        ? prev.filter((v) => v !== value)
        : [...prev, value]
    );
  };

  // Perform search
  const performSearch = async () => {
    const queries = productText
      .split("\n")
      .map((q) => q.trim())
      .filter(Boolean);

    if (queries.length === 0) {
      setResults([]);
      setMessage("Please enter at least one product.");
      return;
    }

    setLoading(true);
    setMessage("Searching...");

    try {
      const res = await fetch(`${BACKEND_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          queries,
          search_lang: lang,
          supermarkets,
          sort_by: "unit_price",
        }),
      });

      const data = await res.json();

      const products: Product[] = data.results.flatMap(
        (q: any) => q.results
      );

      setResults(products);
      setMessage(products.length === 0 ? "No products found." : null);
    } catch (err) {
      console.error(err);
      setResults([]);
      setMessage("Search failed.");
    } finally {
      setLoading(false);
    }
  };

  // ================= Render =================
  return (
    <main className="max-w-7xl mx-auto px-6 pb-10 pt-20">
      {/* Title */}
      <h1 className="font-heading text-3xl md:text-5xl font-semibold text-center mb-12">
        Dutch Supermarket Price Compare
      </h1>

      {/* Main layout */}
      <div className="flex flex-col lg:flex-row gap-10">
        {/* ================= LEFT: Search Panel ================= */}
        <section className="flex-1">
          <div className={`${glassCard} space-y-6`}>
            {/* Supermarket selection */}
            <div>
              <p className="font-semibold mb-2">Select supermarket:</p>
              <div className="flex gap-5">
                {supermarketsList.map((s) => {
                  const selected = supermarkets.includes(s.id);
                  return (
                    <div
                      key={s.id}
                      onClick={() => toggleSupermarket(s.id)}
                      className={
                        baseCircle +
                        " " +
                        (selected
                          ? `${softInset} ${activeRing}`
                          : softNeumorph)
                      }
                    >
                      <img
                        src={supermarketLogos[s.id]}
                        alt={s.label}
                        className="w-10 h-10"
                      />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Language */}
            <div>
              <p className="font-semibold mb-2">Search language:</p>
              <div className="flex gap-5">
                {[
                  { id: "du", label: "DU" },
                  { id: "en", label: "EN" },
                ].map((lg) => {
                  const selected = lang === lg.id;
                  return (
                    <div
                      key={lg.id}
                      onClick={() => setLang(lg.id as "du" | "en")}
                      className={
                        baseCircle +
                        " " +
                        (selected
                          ? `${softInset} ${activeRing}`
                          : softNeumorph)
                      }
                    >
                      {lg.label}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Textarea */}
            <div>
              <label className="block mb-2 font-semibold">
                Enter products (one per line):
              </label>
              <textarea
                value={productText}
                onChange={(e) => setProductText(e.target.value)}
                placeholder={"e.g.\nvolle melk\nchicken breast"}
                className="
                  w-full h-48 resize-none rounded-3xl px-6 py-5
                  bg-white/30 backdrop-blur-xl
                  shadow-[inset_4px_4px_8px_rgba(0,0,0,0.06),_inset_-4px_-4px_8px_rgba(255,255,255,0.5)]
                  ring-1 ring-[#dbe1ea]
                  focus:ring-2 focus:ring-[#4285F4]
                  outline-none transition-all
                "
              />
            </div>

            {/* Search button */}
            <div className="flex justify-end">
              <button
                onClick={performSearch}
                disabled={loading}
                className="
                  px-8 py-3 rounded-full
                  bg-gradient-to-br from-[#5ba0f8] to-[#2f6ce0]
                  text-white font-medium
                  shadow-[0_4px_12px_rgba(66,133,244,0.35)]
                  hover:shadow-[0_6px_16px_rgba(66,133,244,0.45)]
                  active:scale-95
                  transition-all
                  disabled:opacity-60
                "
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </div>
          </div>
        </section>

        {/* ================= RIGHT: Results ================= */}
        <section className="flex-1">
          <div className={`${glassCard} h-full`}>
            <h2 className="font-semibold mb-4">Results</h2>

            {message && (
              <div className="text-gray-500 mb-4">{message}</div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
              {results.map((p) => (
                <ProductCard
                  key={`${p.supermarket}-${p.sku}`}
                  product={p}
                />
              ))}
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}

